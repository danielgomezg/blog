from django.urls import path
from .views import (
    PostListView, 
    PostDetailView, 
    PostHeadingsView,
    IncrementPostClickView,
    CategoryListView,
    CategoryDetailView,
    IncrementCategoryClickView,
    GenerateFakePostsView,
    GenerateFakeAnalyticsView
) 

urlpatterns = [
    path('generate_posts/', GenerateFakePostsView.as_view()),
    path('generate_analytics/', GenerateFakeAnalyticsView.as_view()),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('post/<slug>', PostDetailView.as_view(), name='post-detail'),
    path('post/headings/', PostHeadingsView.as_view(), name='post-headings'), #antes 'post/<slug:slug>/headings/', ahor en views.py se obtiene el slug del request
    path('post/increments_clicks/', IncrementPostClickView.as_view(), name='increment-post-clicks'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('category/posts/', CategoryDetailView.as_view(), name='category-posts'),
    path('category/increments_clicks/', IncrementCategoryClickView.as_view(), name='increment-category-clicks'),
]