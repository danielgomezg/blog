from django.urls import path
from .views import (
    PostListView, 
    PostDetailView, 
    PostHeadingsView,
    IncrementPostClickView
) 

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('post/<slug>', PostDetailView.as_view(), name='post-detail'),
    path('post/headings/', PostHeadingsView.as_view(), name='post-headings'), #antes 'post/<slug:slug>/headings/', ahor en views.py se obtiene el slug del request
    path('post/increments_clicks/', IncrementPostClickView.as_view(), name='increment-post-clicks')
]