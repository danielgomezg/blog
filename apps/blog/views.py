from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer, PostView
from .models import Post, Heading, PostAnalytics
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_client_ip
from rest_framework.exceptions import NotFound, APIException 
from rest_framework import permissions

#Lista por eso el listApiView
#class PostListView(ListAPIView):
#    queryset = Post.postObjects.all()
#    serializer_class = PosListSerializer
#esta es otra forma de hacer la vista en la cual se definen los metedos por lo que que hay que hacer return 
class PostListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            posts = Post.postObjects.all()

            if not posts.exists():
                raise NotFound(detail="No posts found")
            
            serialized_posts = PostListSerializer(posts, many=True).data
        except Post.DoesNotExist:
            raise NotFound(detail="No posts found")
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurreed: {str(e)}")
        
        return Response(serialized_posts)

#es como un getid, por lo que recibe solo uno por eso el RetrieveApiView
#class PostDetailView(RetrieveAPIView):
 #   queryset = Post.postObjects.all()
  #  serializer_class = PostSerializer
   # lookup_field = 'slug'

class PostDetailView(RetrieveAPIView):

    def get(self, request, slug):
        try:
            post = Post.postObjects.get(slug=slug)

        except Post.DoesNotExist:
            raise NotFound(detail="The requested post does not exist")
        
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurreed: {str(e)}")
        
        serialized_post = PostSerializer(post).data
        try:
            #incrementar las vistas del post
            post_analytics = PostAnalytics.objects.get(post=post)
            post_analytics.increment_view(request)
        except PostAnalytics.DoesNotExist:
            raise NotFound(detail="Analytics data for this post does not exist")
        except Exception as e:
            raise APIException(detail=f"An error ocurred while updating post analytics: {str(e)}")
        
        #antigua forma de hacaerlo
        #client_ip = get_client_ip(request)
        #if PostView.objects.filter(post=post, ip_address=client_ip).exists():
        #    return Response(serialized_post)
       # PostView.objects.create(post=post, ip_address=client_ip)
        return Response(serialized_post)

#class PostDetailView(RetrieveAPIView):
 #   def get(self, request, slug):
  #      post = Post.postObjects.get(slug=slug)
   #     serialized_post = PostSerializer(post).data
    #    return Response(serialized_post)

class PostHeadingsView(ListAPIView):
    serializer_classes = HeadingSerializer

    def get_queryset(self):
        post_slug = self.kwargs.get("slug")
        #post__slug el guion bajo doble sirve para acceder al atributo del modelo, a la izquierda el modelo y derecha atributo(sin no se coloca nada accede todos los atributos*)
        return Heading.objects.filter(post__slug = post_slug)
    
class IncrementPostClickView(APIView):

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

        return Response({
            "message": "Click incremented successfully",
            "clicks": post_analytics.clicks
        })