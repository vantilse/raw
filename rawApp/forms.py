from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Artwork, Profile, Artist, Category
from django.contrib.auth.forms import PasswordChangeForm

class ArtworkForm(forms.ModelForm):
    new_artist = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        label='Имя нового автора'
    )
    new_categories = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text='Введите категории через запятую'
    )

    class Meta:
        model = Artwork
        fields = ['title', 'description', 'image', 'artist', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Название картины'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control form-control-lg',
                'placeholder': 'Описание картины'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*'
            }),
            'artist': forms.Select(attrs={
                'class': 'form-select form-control-lg'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-select form-control-lg d-none'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['artist'].queryset = Artist.objects.all()
        self.fields['artist'].required = False
        self.fields['categories'].queryset = Category.objects.all()
        self.fields['categories'].required = False


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Имя',
        max_length=30,
        required=False
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        required=False
    )
    delete_avatar = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Удалить текущий аватар"
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Расскажите о себе'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        if commit:
            profile.user.save()
            profile.save()
        return profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['bio', 'country', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Информация о художнике'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Страна происхождения'
            }),
            'birth_date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            )
        }

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Логин',
            'email': 'Email'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )