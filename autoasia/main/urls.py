from django.urls import path
from .views import *
from . import views


app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('shop/', shop, name='shop'),
    path('contact/', contact, name='contact'),
    path('applications/', views.ApplicationsView.as_view(), name='applications'),
    # path('products/', c, name='contact'),
    path('<int:brand_pk>/', automodels, name='automodels'),
    path('<int:brand_pk>/<int:model_pk>/', category, name='category'),
    path('<int:brand_pk>/<int:model_pk>/<int:category_pk>/', products, name='products'),
    path('product/<int:product_pk>/', product_view, name='product'),
]
