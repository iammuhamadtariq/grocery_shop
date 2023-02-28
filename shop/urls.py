from django.urls import path
from . import views

urlpatterns = [

    path('/<int:category>', views.home_page, name="home_page"),
    path('', views.home_page, name="home_page"),
    path('login', views.login, name="login"),
    path('signup_page', views.signup_page, name="signup_page"),
    path('add_product', views.add_product, name="add_product"),
    path('add_category', views.add_category, name="add_category"),
    path('logout', views.logout, name="logout"),
    path('cart_page', views.cart_page, name="cart_page"),
    path('check_out', views.check_out, name='check_out'),
    path('admin_page', views.admin_page, name="admin_page"),
    path('update_user_type/<int:pk>', views.update_user_type, name="update_user_type"),
    path('delete_product/<int:pk>', views.delete_product, name="delete_product"),
    path('orders', views.orders, name="orders"),
] 