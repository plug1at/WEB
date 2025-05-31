from django import forms
from .models import Album, CustomUser, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['artist', 'title', 'price', 'release_year']
        widgets = {
            'release_year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})