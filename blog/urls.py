from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
    path('tags/<slug:slug>/', views.tag, name='tag'),
    path('search/', views.search, name='search'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/confirm/<uuid:token>/', views.confirm_subscription, name='confirm_subscription'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe'),
]
