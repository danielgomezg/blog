from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer, CategoryListSerializer
from .models import Post, Heading, PostAnalytics, Category
from rest_framework.views import APIView
from rest_framework_api.views import StandardAPIView
from rest_framework.response import Response
from .utils import get_client_ip
from rest_framework.exceptions import NotFound, APIException 
from rest_framework import permissions
from .tasks import increment_post_impressions, increment_post_views_task
import redis
from django.conf import settings
from core.permissions import HasValidAPIKey
#metodo de cache mas rapido
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .utils import get_client_ip

from faker import Faker
import random
import uuid
from django.utils.text import slugify

from django.db.models import Q, F, Prefetch
from django.shortcuts import get_object_or_404


redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)

#Lista por eso el listApiView
#class PostListView(ListAPIView):
#    queryset = Post.postObjects.all()
#    serializer_class = PosListSerializer
#esta es otra forma de hacer la vista en la cual se definen los metedos por lo que que hay que hacer return 
#*recordar que la respuesta se cambio de apiview a standarapiview creado por el profe de udemy
class PostListView(StandardAPIView):
    permission_classes = [HasValidAPIKey] #Validado con al apikey de env, validador de permisos

    #@method_decorator(cache_page(60 * 1)) metodo de cache de 1 min, es un metodo rapido pero no tan efectivo ya que por ejemplo las impresiones no se actualizarian, ya 
    #el primero que carga (se demoraria lo normal pero los demas cargarian la misma info durante un min por lo que las impresion por ejemplo no estaria actualizadas)
    def get(self, request, *args, **kwargs):
        try:
            #Capturar termino del request (en la url con ?termino=)
            #ejemplo https://urban-train-4w957jg7rrg2747w-8000.app.github.dev/api/blog/posts/?search=chile&sorting=newest&ordering=az
            #/api/blog/posts/?search=chile&sorting=newest&ordering=az&category=categoria-cinco&category=categoria-dos
            search = request.query_params.get("search", "").strip()
            sorting = request.query_params.get("sorting", None)
            ordering = request.query_params.get("ordering", None)
            categories = request.query_params.getlist("category", [])
            page = request.query_params.get("p", 1)

            #variables que ingresan por la url
            cache_key = f"post_list:{search}:{sorting}:{ordering}:{categories}:{page}"

            #Antes de llamar a la bd se verifica si hay un cahce guardado con la llave post_list (el cache se guarda con llave valor)
            cached_posts = cache.get(cache_key) 
            #si existe responde el cache si no se jecuta toda la operacion get 
            if cached_posts:
                 # Serializar los datos del caché
               # serialized_posts = PostListSerializer(cached_posts, many=True).data
                #se incrementa las impresiones en cache
                for post in cached_posts:
                    redis_client.incr(f"post:impressions:post['id']") #redis_client.incr(f"post:impressions:{post.id}") 

                return self.paginate(request, cached_posts) #respuesta con apiview Response(cached_posts)
            
            #consulta inicial vacia
            posts = Post.postObjects.all().select_related("category").prefetch_related(
                Prefetch("post_analytics", to_attr="analytics_cache")
            )

            if not posts.exists():
                raise NotFound(detail="No posts found")

            # Filtrar por busqueda
            if search != "":
                posts = Post.postObjects.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(content__icontains=search) |
                    Q(keywords__icontains=search) 
                )
            
            # Filtrar por categoria
            if categories:
                category_queries = Q()
                for category in categories:
                    # Check if category is a valid uuid
                    try:
                        uuid.UUID(category)
                        uuid_query = (
                            Q(category__id=category)
                        )
                        category_queries |= uuid_query
                    except ValueError:
                        slug_query = (
                            Q(category__slug=category)
                        )
                        category_queries |= slug_query
                posts = posts.filter(category_queries)

            # Ordenamiento
            if sorting:
                if sorting == 'newest':
                    posts = posts.order_by("-created_at")
                elif sorting == 'recently_updated':
                    posts = posts.order_by("-updated_at") #created_at  updated_at
                elif sorting == 'most_viewed':
                    posts = posts.annotate(popularity=F("analytics_cache__views")).order_by("-popularity")

            if ordering:
                if ordering == 'az':
                    posts = posts.order_by("title")
                if ordering == 'za':
                    posts = posts.order_by("-title")

            serialized_posts = PostListSerializer(posts, many=True).data

            #se guarda el serialized_post en cache por 5 min
            cache.set(cache_key, serialized_posts, timeout=60*5)

            #serialized_posts = PostListSerializer(posts, many=True).data

            #esto funciona, pero no es lo ideal ya que si se tiene muchos posts los recorreria todos (para mejorar esto aplica celery beat), esta es forma antigua
            #for post in posts:
                #increment_post_impressions.delay(post.id) #delay es para que ejecute la tarea
            #se incrementa las impresiones en redis
            for post in posts:
                redis_client.incr(f"post:impressions:{post.id}") #Redis usa claves estructuradas tipo "recurso:tipo:identificador"

        except Post.DoesNotExist:
            raise NotFound(detail="No posts found")
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurreed: {str(e)}")
        
        #recordar que paginate es de la libreria que creo el instructor, por ende en la documentacion esta el fucnionamiento
        #ipServidor/api/blog/posts/?p=1&page_size=10
        return self.paginate(request, serialized_posts) #Respuesta con paginacion; Antes => Response(serialized_posts)

#es como un getid, por lo que recibe solo uno por eso el RetrieveApiView
#class PostDetailView(RetrieveAPIView):
 #   queryset = Post.postObjects.all()
  #  serializer_class = PostSerializer
   # lookup_field = 'slug'

#Recordar que el slug en el curso viene en la peticion asi url?slug=hola-mundo, como en la clase class PostHeadingsView(StandardAPIView), yo no lo modifique aca
class PostDetailView(StandardAPIView):
    permission_classes = [HasValidAPIKey] #Validado con al apikey de env, validador de permisos

    def get(self, request, slug):
        ip_address = get_client_ip(request)

        try:
            #Antes de llamar a la bd se verifica si hay un cahce guardado con la llave post_list (el cache se guarda con llave valor)
            cached_post = cache.get(f"post_detail:{slug}") 
            #si existe responde el cache si no se jecuta toda la operacion get 
            if cached_post:
               #incremento las vistas del posts
               increment_post_views_task.delay(cached_post['slug'], ip_address)
               return self.response(cached_post) #Response(cached_post)

            post = Post.postObjects.get(slug=slug)

            serialized_post = PostSerializer(post).data

            #se guarda el serialized_post en cache por 5 min
            cache.set(f"post_detail:{slug}", serialized_post, timeout=60*5)

            #incremento las vistas del posts
            increment_post_views_task.delay(post.slug, ip_address)

        except Post.DoesNotExist:
            raise NotFound(detail="The requested post does not exist")
        
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurreed: {str(e)}")
        
        #antigua forma de hacaerlo
        #client_ip = get_client_ip(request)
        #if PostView.objects.filter(post=post, ip_address=client_ip).exists():
        #    return Response(serialized_post)
       # PostView.objects.create(post=post, ip_address=client_ip)
        return self.response(serialized_post) #Response(serialized_post)

#class PostDetailView(RetrieveAPIView):
 #   def get(self, request, slug):
  #      post = Post.postObjects.get(slug=slug)
   #     serialized_post = PostSerializer(post).data
    #    return Response(serialized_post)

class PostHeadingsView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def get(self,request):
        post_slug = request.query_params.get("slug")
        heading_objects = Heading.objects.filter(post__slug = post_slug)
        serialized_data = HeadingSerializer(heading_objects, many=True).data
        return self.response(serialized_data)
    
    
class IncrementPostClickView(StandardAPIView):
    permission_classes = [HasValidAPIKey] #Validado con al apikey de env, validador de permisos

    def post(self, request):
        """
        Incrementa el contador de clics de un post basado en su slug.
        """
        data = request.data
        try:
            post = Post.postObjects.get(slug=data['slug'])
        except Post.DoesNotExist:
            raise NotFound(detail="The requested post does not exist")
        
        try:
            post_analytics, created = PostAnalytics.objects.get_or_create(post=post)
            post_analytics.increment_click()
        except Exception as e:
            raise APIException(detail=f"An error ocurred while updating post analytics: {str(e)}")
        
        return self.response({
            "message": "Click incremented successfully",
            "clicks": post_analytics.clicks
        })

#ejemplo de url ipServer /api/blog/categories/?parent_slug=categoria-dos&ordering=za&search=ultricies&p=1
class CategoryListView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def get(self, request):

        try:
            # Parametros de solicitud
            parent_slug = request.query_params.get("parent_slug", None)
            ordering = request.query_params.get("ordering", None)
            sorting = request.query_params.get("sorting", None)
            search = request.query_params.get("search", "").strip()
            page = request.query_params.get("p", "1")

            # Construir clave de cache para resultados paginados
            cache_key = f"category_list:{page}:{ordering}:{sorting}:{search}:{parent_slug}"
            cached_categories = cache.get(cache_key)
            if cached_categories:
                # Serializar los datos del caché
                serialized_categories = CategoryListSerializer(cached_categories, many=True).data
                # Incrementar impresiones en Redis para los posts del caché
                for category in cached_categories:
                    redis_client.incr(f"category:impressions:{category.id}")  # Usar `post.id`
                return self.paginate(request, serialized_categories)

            # Consulta inicial optimizada
            if parent_slug:
                categories = Category.objects.filter(parent__slug=parent_slug).prefetch_related(
                    Prefetch("category_analytics", to_attr="analytics_cache")
                )
            else:
                # Si no especificamos un parent_slug buscamos las categorias padre
                categories = Category.objects.filter(parent__isnull=True).prefetch_related(
                    Prefetch("category_analytics", to_attr="analytics_cache")
                )

            if not categories.exists():
                raise NotFound(detail="No categories found.")
            
            # Filtrar por busqueda
            if search != "":
                categories = categories.filter(
                    Q(name__icontains=search) |
                    Q(slug__icontains=search) |
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # Ordenamiento
            if sorting:
                if sorting == 'newest':
                    categories = categories.order_by("-created_at")
                elif sorting == 'recently_updated':
                    categories = categories.order_by("-updated_at")
                elif sorting == 'most_viewed':
                    categories = categories.annotate(popularity=F("analytics_cache__views")).order_by("-popularity")

            if ordering:
                if ordering == 'az':
                    categories = categories.order_by("name")
                if ordering == 'za':
                    categories = categories.order_by("-name")

            # Guardar los objetos en el caché
            cache.set(cache_key, categories, timeout=60 * 5)

            # Serializacion
            serialized_categories = CategoryListSerializer(categories, many=True).data

            # Incrementar impresiones en Redis
            for category in categories:
                redis_client.incr(f"category:impressions:{category.id}")

            return self.paginate(request, serialized_categories)
        except Exception as e:
                raise APIException(detail=f"An unexpected error occurred: {str(e)}")
        
#ejemplo ipSever/api/blog/category/posts/?slug=subcategoria-41
class CategoryDetailView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def get(self, request):

        try:
            # Obtener parametros
            slug = request.query_params.get("slug", None)
            page = request.query_params.get("p", "1")

            if not slug:
                return self.error("Missing slug parameter")
            
            # Construir cache
            cache_key = f"category_posts:{slug}:{page}"
            cached_posts = cache.get(cache_key)
            if cached_posts:
                # Serializar los datos del caché
                serialized_posts = PostListSerializer(cached_posts, many=True).data
                # Incrementar impresiones en Redis para los posts del caché
                for post in cached_posts:
                    redis_client.incr(f"post:impressions:{post.id}")  # Usar `post.id`
                return self.paginate(request, serialized_posts)

            # Obtener la categoria por slug
            category = get_object_or_404(Category, slug=slug)

            # Obtener los posts que pertenecen a esta categoria
            posts = Post.postObjects.filter(category=category).select_related("category").prefetch_related(
                Prefetch("post_analytics", to_attr="analytics_cache")
            )
            
            if not posts.exists():
                raise NotFound(detail=f"No posts found for category '{category.name}'")
            
            # Guardar los objetos en el caché
            cache.set(cache_key, posts, timeout=60 * 5)

            # Serializar los posts
            serialized_posts = PostListSerializer(posts, many=True).data

            # Incrementar impresiones en Redis
            for post in posts:
                redis_client.incr(f"post:impressions:{post.id}")

            return self.paginate(request, serialized_posts)
        except Exception as e:
            raise APIException(detail=f"An unexpected error occurred: {str(e)}")

class IncrementCategoryClickView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    def category(self, request):
        """
        Incrementa el contador de clics de una categoria basado en su slug.
        """
        data = request.data

        try:
            category = Category.objects.get(slug=data['slug'])
        except Category.DoesNotExist:
            raise NotFound(detail="The requested category does not exist")
        
        try:
            category_analytics, created = CategoryAnalytics.objects.get_or_create(category=category)
            category_analytics.increment_click()
        except Exception as e:
            raise APIException(detail=f"An error ocurred while updating category analytics: {str(e)}")

        return self.response({
            "message": "Click incremented successfully",
            "clicks": category_analytics.clicks
        })

class GenerateFakePostsView(StandardAPIView):

    def get(self,request):
        # Configurar Faker
        fake = Faker()

        # Obtener todas las categorías existentes
        categories = list(Category.objects.all())

        if not categories:
            return self.response("No hay categorías disponibles para asignar a los posts", 400)

        posts_to_generate = 100  # Número de posts ficticios a generar
        status_options = ["draft", "published"]

        for _ in range(posts_to_generate):
            title = fake.sentence(nb_words=6)  # Generar título aleatorio
            post = Post(
                id=uuid.uuid4(),
                title=title,
                description=fake.sentence(nb_words=12),
                content=fake.paragraph(nb_sentences=5),
                keywords=", ".join(fake.words(nb=5)),
                slug=slugify(title),  # Generar slug a partir del título
                category=random.choice(categories),  # Asignar una categoría aleatoria
                status=random.choice(status_options),
            )
            post.save()

        return self.response(f"{posts_to_generate} posts generados exitosamente.")

class GenerateFakeAnalyticsView(StandardAPIView):

    def get(self, request):
        fake = Faker()

        # Obtener todos los posts existentes
        posts = Post.objects.all()

        if not posts:
            return self.response({"error": "No hay posts disponibles para generar analíticas"}, status=400)

        analytics_to_generate = len(posts)  # Una analítica por post

        # Generar analíticas para cada post
        for post in posts:
            views = random.randint(50, 1000)  # Número aleatorio de vistas
            impressions = views + random.randint(100, 2000)  # Impresiones >= vistas
            clicks = random.randint(0, views)  # Los clics son <= vistas
            avg_time_on_page = round(random.uniform(10, 300), 2)  # Tiempo promedio en segundos
            
            # Crear o actualizar analíticas para el post
            analytics, created = PostAnalytics.objects.get_or_create(post=post)
            analytics.views = views
            analytics.impressions = impressions
            analytics.clicks = clicks
            analytics.avg_time_on_page = avg_time_on_page
            analytics._update_click_through_rate()  # Recalcular el CTR
            analytics.save()

        return self.response({"message": f"Analíticas generadas para {analytics_to_generate} posts."})