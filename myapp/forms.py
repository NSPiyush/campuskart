from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, Product, ProductRequest

def validate_srit_email(value):
    """Validate that email ends with @sritcbe.ac.in"""
    if not value.endswith('@sritcbe.ac.in'):
        raise ValidationError('Only SRIT college email addresses (@sritcbe.ac.in) are allowed to register.')

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[validate_srit_email],
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'yourname@sritcbe.ac.in'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    department = forms.ChoiceField(
        choices=UserProfile.DEPARTMENT_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    current_year = forms.ChoiceField(
        choices=UserProfile.YEAR_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    graduation_year = forms.IntegerField(
        min_value=2020, 
        max_value=2030, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Graduation Year'})
    )
    favorite_food = forms.CharField(
    max_length=50,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Favorite Food (Security Question)'
    })
)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 
                 'department', 'current_year', 'graduation_year','favorite_food']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@sritcbe.ac.in'):
            raise ValidationError('Email must be from SRIT College (@sritcbe.ac.in)')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                college_name='SRIT',
                department=self.cleaned_data['department'],
                current_year=self.cleaned_data['current_year'],
                graduation_year=self.cleaned_data['graduation_year'],
                favorite_food=self.cleaned_data['favorite_food']
            )
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'condition', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your product...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "--------- Select Category ---------"
        self.fields['condition'].empty_label = "--------- Select Condition ---------"

class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Message to seller (optional)'}),
        }