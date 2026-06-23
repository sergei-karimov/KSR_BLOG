from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
    path('tags/<slug:slug>/', views.tag_detail, name='tag'),
]
