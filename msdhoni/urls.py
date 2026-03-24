"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('category/<str:category>/', views.category_products, name='category_products'),
    path('mobiles/', views.mobiles, name='mobiles'),
    path('accessories/', views.accessories, name='accessories'),
    path('deals/', views.deals, name='deals'),
    path('contact/', views.contact, name='contact'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/count/', views.cart_count, name='cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('checkout/complete/<int:order_id>/', views.checkout_complete, name='checkout_complete'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]