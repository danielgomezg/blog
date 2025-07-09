from rest_framework import serializers
from .models import Post, Category, Heading, PostView

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name',
            'slug'
        ]

class HeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heading
        fields = [
            "title",
            "slug",
            "level",
            "order",
        ]

class PostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostView
        fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    headings = HeadingSerializer(many=True)
    view_count = serializers.SerializerMethodField() #el nombre de esta variable debe ser igual a la funcion sin e get_ y se agrega view_count a all (en este caso por que es all se agrega automanticamente)
    class Meta:
        model = Post
        fields = "__all__"

    def get_view_count(self, obj):
        return obj.post_view.count()

class PostListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()
    view_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "thumbnail",
            "slug",
            "category",
            "view_count"
        ]

    def get_view_count(self, obj):
        return obj.post_view.count()

