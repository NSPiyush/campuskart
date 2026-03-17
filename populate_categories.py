import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product.settings')
django.setup()

from myapp.models import Category

# Run the function to create default categories
print("Starting to populate categories...")
count = Category.create_default_categories()
print(f"Successfully created {count} new categories!")
print(f"Total categories now: {Category.objects.count()}")