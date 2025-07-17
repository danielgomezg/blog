from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer, PostView
from .models import Post, Heading, PostAnalytics
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
            #Antes de llamar a la bd se verifica si hay un cahce guardado con la llave post_list (el cache se guarda con llave valor)
            cached_posts = cache.get("post_list") 
            #si existe responde el cache si no se jecuta toda la operacion get 
            if cached_posts:
                #se incrementa las impresiones en cache
                for post in cached_posts:
                    redis_client.incr(f"post:impressions:{post.id}") 

                return self.paginate(request, cached_posts) #respuesta con apiview Response(cached_posts)
            
            posts = Post.postObjects.all()

            if not posts.exists():
                raise NotFound(detail="No posts found")
            
            serialized_posts = PostListSerializer(posts, many=True).data

            #se guarda el serialized_post en cache por 5 min
            cache.set("post_list", serialized_posts, timeout=60*5)

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
    
        #return Response({
        #    "message": "Click incremented successfully",
        #    "clicks": post_analytics.clicks
        #})