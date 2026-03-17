from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.dispatch import receiver
class UserProfile(models.Model):
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('cse', 'Computer Science Engineering'),
        ('ece', 'Electronics & Communication Engineering'),
        ('eee', 'Electrical & Electronics Engineering'),
        ('mech', 'Mechanical Engineering'),
        ('civil', 'Civil Engineering'),
        ('it', 'Information Technology'),
        ('aiml', 'Artificial Intelligence & Machine Learning'),
       
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)
    college_name = models.CharField(max_length=200, default='SRIT')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='other')  # Increased to 50
    current_year = models.CharField(max_length=5, choices=YEAR_CHOICES, default='1')
    graduation_year = models.IntegerField()
    favorite_food = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    wrong_attempts = models.IntegerField(default=0)
    lock_until = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_department_display()} - Year {self.current_year}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_default_categories(cls):
        default_categories = [
            {'name': 'Textbooks', 'slug': 'textbooks', 'icon': 'fas fa-book'},
            {'name': 'Electronics', 'slug': 'electronics', 'icon': 'fas fa-microchip'},
            {'name': 'Lab Equipment', 'slug': 'lab-equipment', 'icon': 'fas fa-flask'},
            {'name': 'Fiction Books', 'slug': 'fiction-books', 'icon': 'fas fa-book-open'},
            {'name': 'Sports Equipment', 'slug': 'sports-equipment', 'icon': 'fas fa-futbol'},
            {'name': 'Notes', 'slug': 'notebooks', 'icon': 'fas fa-pen'},
            {'name': 'Stationery', 'slug': 'stationery', 'icon': 'fas fa-pencil-alt'},
           
        ]
        
        created_count = 0
        for cat in default_categories:
            obj, created = cls.objects.get_or_create(
                name=cat['name'],
                defaults={
                    'slug': cat['slug'],
                    'icon': cat['icon']
                }
            )
            if created:
                created_count += 1
                print(f"Created category: {cat['name']}")
        
        return created_count

class Product(models.Model):
    CONDITION_CHOICES = [
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    image = models.ImageField(upload_to='product_images/')
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"

class ProductRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'buyer']
    
    def __str__(self):
        return f"{self.buyer.username} wants {self.product.name}"

@receiver(post_migrate)
def create_categories_on_migration(sender, **kwargs):
    """Automatically create categories after migration"""
    if sender.name == 'myapp':
        print("\n" + "="*50)
        print("CHECKING FOR DEFAULT CATEGORIES")
        print("="*50)
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'myapp_category'
                    );
                """)
                table_exists = cursor.fetchone()[0]
            
            if table_exists:
                count = Category.create_default_categories()
                if count > 0:
                    print(f" Successfully created {count} default categories!")
                else:
                    print(" All categories already exist!")
            else:
                print(" Category table doesn't exist yet. Skipping category creation.")
                
        except Exception as e:
            print(f" Note: {e}")
        print("="*50 + "\n")