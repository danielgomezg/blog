from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer
from .models import Post, Heading
from rest_framework.views import APIView
from rest_framework.response import Response

#Lista por eso el listApiView
#class PostListView(ListAPIView):
#    queryset = Post.postObjects.all()
#    serializer_class = PosListSerializer
#esta es otra forma de hacer la vista en la cual se definen los metedos por lo que que hay que hacer return 
class PostListView(APIView):
    def get(self, request, *args, **kwargs):
        posts = Post.postObjects.all()
        serialized_posts = PostListSerializer(posts, many=True).data
        return Response(serialized_posts)

#es como un getid, por lo que recibe solo uno por eso el RetrieveApiView
#class PostDetailView(RetrieveAPIView):
 #   queryset = Post.postObjects.all()
  #  serializer_class = PostSerializer
   # lookup_field = 'slug'

class PostDetailView(RetrieveAPIView):
    def get(self, request, slug):
        post = Post.postObjects.get(slug=slug)
        serialized_post = PostSerializer(post).data
        return Response(serialized_post)

class PostHeadingsView(ListAPIView):
    serializer_classes = HeadingSerializer

    def get_queryset(self):
        post_slug = self.kwargs.get("slug")
        #post__slug el guion bajo doble sirve para acceder al atributo del modelo, a la izquierda el modelo y derecha atributo(sin no se coloca nada accede todos los atributos*)
        return Heading.objects.filter(post__slug = post_slug)