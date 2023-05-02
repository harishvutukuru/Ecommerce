
from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings as sett
urlpatterns = [
    path('', index, name='index'),
    # path('login/', login_view, name='login'),
    path('products/',product, name='product'),
    path('products/edit/<int:pk>/', product_edit,
         name='products-edit'),
    path('products/delete/<int:pk>/', product_delete,
         name='products-delete'),
    path('order/', order, name='order'),
    path('products/detail/<int:pk>/', product_detail,
         name='products-detail'),
    path('user/', user, name='user'),
    path('stats/', stats, name='stats'),
    path('purchase/', purchase, name='purchase'),
    path('sale/', sale, name='sale'),
    path('ecom/', ecom, name="ecom"),
    path('user_create/', user_create, name="user_create"),
    path('user/edit/<int:pk>/', user_edit,
         name='user-edit'),
    path('user/delete/<int:pk>/', user_delete,
         name='user-delete'),

    path('category/', category, name="category"),
    path('category/edit/<int:pk>/', category_edit,
         name='category-edit'),
    path('category/delete/<int:pk>/', category_delete,
         name='category-delete'),

    path('sub_category/', sub_category, name="sub_category"),
    path('sub_category/edit/<int:pk>/', sub_category_edit,
         name='sub-category-edit'),
    path('sub_category/delete/<int:pk>/', sub_category_delete,
         name='sub-category-delete'),
    path('access_denied',AccessDeniend,name="access_denied"),

    path('settings/', settings, name="settings"),
    path('order-status-update/edit/<int:pk>/',order_status_update,name="order-status-update"),
    path('cart_view/',cart_view,name="cart_view"),
    path('checkout/',checkout,name="checkout"),
    path('add_cart/',AddCart,name="add_cart"),
    path('add_cart/<int:pk>/',AddCart,name="add_cart"),
    path('cart_update/',UpdateCart,name="cart_update"),
    path('cart_remove/',RemoveCart,name="cart_remove"),
    path('cart_update/<int:pk>/',UpdateCart,name="cart_update"),
    path('cart_remove/<int:pk>/',RemoveCart,name="cart_remove"),
    




]
