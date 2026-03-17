from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.http import JsonResponse
from django.http import HttpResponse
import random
import string
from datetime import timedelta
from django.utils import timezone
from .models import Product, Category, ProductRequest, UserProfile
from .forms import UserRegistrationForm, ProductForm, ProductRequestForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
def index(request):
    """Homepage with latest products and categories"""
    products = Product.objects.filter(is_sold=False).order_by('-created_at')[:12]
    categories = Category.objects.all()
    return render(request, 'index.html', {
        'products': products,
        'categories': categories
    })

def register(request):
    """User registration page"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            favorite_food = request.POST.get("favorite_food")
            profile = user.profile
            profile.favorite_food = favorite_food
            profile.save()
            messages.success(request, ' Registration successful! Welcome to CampusKart.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def user_login(request):
    """User login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f' Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, ' Invalid username or password. Please try again.')
    
    return render(request, 'login.html')

def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, ' You have been logged out successfully.')
    return redirect('index')

@login_required
def dashboard(request):
    selling = Product.objects.filter(seller=request.user).order_by('-created_at')
    buying = ProductRequest.objects.filter(buyer=request.user).order_by('-created_at')
    received = ProductRequest.objects.filter(product__seller=request.user).order_by('-created_at')
    
    context = {
        'selling': selling,
        'buying': buying,
        'received': received,
        'selling_count': selling.count(),
        'buying_count': buying.count(),
        'received_count': received.count(),
        'sold_count': selling.filter(is_sold=True).count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def product_list(request):
    """List all available products with filters"""
    products = Product.objects.filter(is_sold=False)
    
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    condition = request.GET.get('condition')
    if condition:
        products = products.filter(condition=condition)
    
    return render(request, 'product_list.html', {
        'products': products,
        'categories': Category.objects.all()
    })

@login_required
def product_detail(request, product_id):
    """View single product details"""
    product = get_object_or_404(Product, id=product_id)

    product_request = ProductRequest.objects.filter(
        product=product,
        buyer=request.user
    ).first()

    has_requested = product_request is not None

    is_accepted = False
    if product_request and product_request.status == "accepted":
        is_accepted = True

    return render(request, 'product_detail.html', {
        'product': product,
        'has_requested': has_requested,
        'is_owner': request.user == product.seller,
        'is_accepted': is_accepted
    })

@login_required
def buy_product(request, product_id):
    """Direct purchase - marks product as sold immediately"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user == product.seller:
        messages.error(request, ' You cannot buy your own product!')
        return redirect('product_detail', product_id=product.id)
    
    if product.is_sold:
        messages.error(request, ' This product has already been sold!')
        return redirect('product_detail', product_id=product.id)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        ProductRequest.objects.create(
            product=product,
            buyer=request.user,
            message=message,
            status='completed'
        )
        
        product.is_sold = True
        product.save()
        
        messages.success(request, f' Congratulations! You have successfully purchased {product.name}. Please contact the seller to arrange pickup.')
        return redirect('dashboard')
    
    return redirect('product_detail', product_id=product.id)

@login_required
def request_product(request, product_id):
    """Request to buy - seller needs to approve"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user == product.seller:
        messages.error(request, ' You cannot request your own product!')
        return redirect('product_detail', product_id=product.id)
    
    if product.is_sold:
        messages.error(request, ' This product has already been sold!')
        return redirect('product_detail', product_id=product.id)
    
    existing_request = ProductRequest.objects.filter(
        product=product,
        buyer=request.user
    ).first()

    
    if existing_request:
        if existing_request.status == 'pending':
            messages.warning(request, ' You have already requested this product. Please wait for seller response.')
        elif existing_request.status == 'accepted':
            messages.info(request, ' Your request has been accepted! Please contact the seller to complete the transaction.')
        elif existing_request.status == 'rejected':
            messages.error(request, ' Your previous request was rejected. You can try again.')
        return redirect('product_detail', product_id=product.id)
    
    pending_requests = ProductRequest.objects.filter(buyer=request.user,status='pending').count()

    if pending_requests >= 2:
        messages.warning(request,' You can only have 2 active product requests at a time.')
        return redirect('product_detail', product_id=product.id)

    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        ProductRequest.objects.create(
            product=product,
            buyer=request.user,
            message=message,
            status='pending'
        )
        
        messages.success(request, ' Request sent successfully! The seller will respond soon.')
        return redirect('product_detail', product_id=product.id)
    
    return redirect('product_detail', product_id=product.id)


@login_required
def add_product(request):
    """Add a new product for sale"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, ' Product listed successfully!')
            return redirect('my_products')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    return render(request, 'add_product.html', {
        'form': form,
        'categories': categories
    })

@login_required
def my_products(request):
    """View all products listed by the user"""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'my_products.html', {'products': products})

@login_required
def edit_product(request, product_id):
    """Edit an existing product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Product updated successfully!')
            return redirect('my_products')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'edit_product.html', {
        'form': form,
        'product': product,
        'categories': categories
    })

@login_required
def delete_product(request, product_id):
    """Delete a product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, '✅ Product deleted successfully!')
        return redirect('my_products')
    
    return render(request, 'delete_product.html', {'product': product})


@login_required
def manage_requests(request):
    """Manage all requests (received and made)"""
    received = ProductRequest.objects.filter(
        product__seller=request.user
    ).order_by('-created_at')
    
    made = ProductRequest.objects.filter(
        buyer=request.user
    ).order_by('-created_at')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        product_request = get_object_or_404(ProductRequest, id=request_id, product__seller=request.user)
        
        if action == 'accept':
            product_request.status = 'accepted'
            messages.success(request, ' Request accepted! The buyer will be notified.')
        elif action == 'reject':
            product_request.status = 'rejected'
            messages.success(request, ' Request rejected.')
        elif action == 'complete':
            product_request.status = 'completed'
            product_request.product.is_sold = True
            product_request.product.save()
            messages.success(request, 'Transaction completed! Product marked as sold.')
        
        product_request.save()
        return redirect('manage_requests')
    
    return render(request, 'requests.html', {
        'received': received,
        'made': made
    })


@login_required
def profile(request):
    """View and edit user profile"""
    user_profile = request.user.profile
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        department = request.POST.get('department', '')
        current_year = request.POST.get('current_year', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        favorite_food = request.POST.get('favorite_food', '').lower().strip()
        
        if not department or not current_year:
            messages.error(request, ' Department and Current Year are required fields.')
            return render(request, 'profile.html', {'profile': user_profile})
        
        user_profile.phone_number = phone_number
        user_profile.department = department
        user_profile.current_year = current_year
        user_profile.favorite_color = favorite_food
        user_profile.save()
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, ' Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'profile.html', {'profile': user_profile})

@login_required
def delete_account(request):
    """Permanently delete user account"""
    if request.method == 'POST':
        user = request.user
        username = user.username
        
        confirm_username = request.POST.get('confirm_username', '')
        
        if confirm_username != username:
            messages.error(request, ' Username does not match. Account not deleted.')
            return redirect('profile')
        
        logout(request)
        
        try:
            with transaction.atomic():
                user_id = user.id
                user_email = user.email
                
                user.delete()
                
                messages.success(request, f' Account "{username}" has been permanently deleted. We\'re sorry to see you go!')
                
        except Exception as e:
            messages.error(request, f' Error deleting account: {str(e)}')
            return redirect('profile')
        
        return redirect('index')
    
    return redirect('profile')



@login_required
def change_password(request):

    if request.method == "POST":

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        fav_food = request.POST.get("favorite_food", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if profile.lock_until and timezone.now() < profile.lock_until:
            remaining = profile.lock_until - timezone.now()
            minutes = remaining.seconds // 60

            return JsonResponse({
                "status": "error",
                "message": f"Too many attempts. Try again after {minutes} minutes."
            })

        if fav_food.lower() != profile.favorite_food.lower():

            profile.wrong_attempts += 1

            if profile.wrong_attempts >= 3:
                profile.lock_until = timezone.now() + timedelta(minutes=10)
                profile.wrong_attempts = 0
                profile.save()

                return JsonResponse({
                    "status": "error",
                    "message": "Too many wrong attempts. Locked for 10 minutes."
                })

            profile.save()

            remaining = 3 - profile.wrong_attempts

            return JsonResponse({
                "status": "error",
                "message": f"Wrong favorite food. {remaining} attempts left."
            })

        if new_password != confirm_password:
            return JsonResponse({
                "status": "error",
                "message": "Passwords do not match."
            })

        if len(new_password) < 8:
            return JsonResponse({
                "status": "error",
                "message": "Password must be at least 8 characters."
            })

        user = request.user
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        profile.wrong_attempts = 0
        profile.lock_until = None
        profile.save()

        return JsonResponse({
            "status": "success"
        })

    return render(request, "change_password.html")

def forgot_password(request):

    if request.method == "GET":
        return render(request, "forgot_password.html")

    if request.method == "POST":

        email = request.POST.get("email")
        fav_food = request.POST.get("favorite_food")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Email not found"
            })

        if not profile.favorite_food:
            return JsonResponse({
                "status": "error",
                "message": "Security question not set for this account"
            })

      
        if fav_food.lower() != profile.favorite_food.lower():

            profile.wrong_attempts += 1

            if profile.wrong_attempts >= 3:

                profile.lock_until = timezone.now() + timedelta(minutes=10)
                profile.wrong_attempts = 0
                profile.save()

                return JsonResponse({
                    "status": "error",
                    "message": "Too many attempts. Try again in 10 minutes"
                })

            profile.save()

            return JsonResponse({
                "status": "error",
                "message": "Wrong favorite food"
            })

        if new_password != confirm_password:
            return JsonResponse({
                "status": "error",
                "message": "Passwords do not match"
            })

        user.set_password(new_password)
        user.save()

        profile.wrong_attempts = 0
        profile.lock_until = None
        profile.save()

        return JsonResponse({
            "status": "success"
        })
def debug_urls(request):
    from django.urls import get_resolver
    urls = []
    for pattern in get_resolver().url_patterns:
        urls.append(str(pattern.pattern))
    return HttpResponse('<br>'.join(urls))