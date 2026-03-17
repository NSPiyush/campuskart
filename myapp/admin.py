from django.contrib import admin
from .models import UserProfile, Category, Product, ProductRequest

admin.site.site_header = "CampusKart Admin"
admin.site.site_title = "CampusKart Admin Portal"
admin.site.index_title = "Welcome to CampusKart Dashboard"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'college_name', 'department', 'current_year', 'graduation_year', 'created_at']
    list_filter = ['college_name', 'department', 'current_year', 'graduation_year']
    search_fields = ['user__username', 'user__email', 'phone_number', 'department']
    readonly_fields = ['created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'category', 'price', 'condition', 'is_sold', 'created_at']
    list_filter = ['condition', 'is_sold', 'category', 'created_at']
    search_fields = ['name', 'description', 'seller__username']
    list_editable = ['is_sold']
    readonly_fields = ['created_at']
    raw_id_fields = ['seller']

@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ['product', 'buyer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product__name', 'buyer__username', 'message']
    list_editable = ['status']
    readonly_fields = ['created_at']
    raw_id_fields = ['product', 'buyer']