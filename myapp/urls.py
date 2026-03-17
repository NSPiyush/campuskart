from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/buy/', views.buy_product, name='buy_product'),
    path('product/<int:product_id>/request/', views.request_product, name='request_product'),
    
    path('add-product/', views.add_product, name='add_product'),
    path('my-products/', views.my_products, name='my_products'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    
    path('profile/', views.profile, name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    path('change-password/', views.change_password, name='change_password'),
    path('debug-urls/', views.debug_urls, name='debug_urls'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]