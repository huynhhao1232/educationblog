from django.urls import path
from django.conf import settings
from . import views

app_name = 'homepage'
urlpatterns = [
    path('', views.getHomePage, name="Homepage"),
    path('category/<int:category_id>/', views.getCategory, name="category"),
    path('post/<int:post_id>/', views.getViewPost, name='post'),
    path('cctc/<int:pb_id>/', views.getCCTC, name="cctc"),
    

]
