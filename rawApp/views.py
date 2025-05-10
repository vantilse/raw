from django.contrib.auth import authenticate, logout
from .forms import ProfileForm
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserSettingsForm
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ArtworkForm
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserCreationForm, ArtistProfileForm
from django.db.models import Count, Prefetch
import logging
from .models import Artist
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Artwork
from django.shortcuts import render
from .models import Category
from django.db.models import Case, When, IntegerField

logger = logging.getLogger(__name__)


def artist_list(request):
    artists = Artist.objects.select_related('user').all()
    return render(request, 'artists.html', {'artists': artists})


def home(request):
    try:
        artwork_prefetcher = Prefetch('artist', queryset=Artist.objects.only('name', 'id'))

        popular_artworks = Artwork.objects.filter(
            is_approved=True
        ).annotate(
            likes_count=Count('likes')
        ).order_by('-likes_count', '-created_at'
                   ).prefetch_related(artwork_prefetcher)[:4]

        new_artworks = Artwork.objects.filter(
            is_approved=True
        ).order_by('-created_at')[:4]

        categories = Category.objects.annotate(
            artworks_count=Count('artwork')
        ).filter(
            artworks_count__gt=0
        ).order_by('-artworks_count')[:12]

        context = {
            'popular_artworks': popular_artworks,
            'new_artworks': new_artworks,
            'categories': categories
        }

    except Exception as e:
        print(f"Error in home view: {str(e)}")
        context = {
            'popular_artworks': [],
            'new_artworks': [],
            'categories': []
        }

    return render(request, 'rawApp/home.html', context)


def category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    artworks = Artwork.objects.filter(categories=category, is_approved=True)
    return render(request, 'rawApp/category.html', {
        'category': category,
        'artworks': artworks
    })


def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    artwork.increment_views()
    is_liked = False
    if request.user.is_authenticated:
        is_liked = request.user in artwork.likes.all()

    return render(request, 'rawApp/artwork_detail.html', {
        'artwork': artwork,
        'is_liked': is_liked
    })

@login_required
def add_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                artwork = form.save(commit=False)
                artwork.author = request.user
                artwork.status = 'pending'

                new_artist = request.POST.get('new_artist', '').strip()
                if new_artist:
                    artist, created = Artist.objects.get_or_create(
                        name=new_artist,
                        defaults={'user': None}
                    )
                    artwork.artist = artist

                artwork.save()

                form.save_m2m()

                new_cats = request.POST.get('new_categories', '')
                if new_cats:
                    for cat in new_cats.split(','):
                        cat_name = cat.strip()
                        if cat_name:
                            category, _ = Category.objects.get_or_create(name=cat_name)
                            artwork.categories.add(category)

                messages.success(request, 'Статья успешно отправлена!')
                return redirect('submission_success')

            except Exception as e:
                messages.error(request, f'Ошибка сохранения: {str(e)}')
        else:
            messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = ArtworkForm()

    return render(request, 'rawApp/add_artwork.html', {
        'form': form,
        'artists': Artist.objects.all(),
        'categories': Category.objects.all()
    })

def submission_success(request):
    return render(request, 'rawApp/submission_success.html')


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user) 
    artworks = Artwork.objects.filter(author=user, is_approved=True)

    return render(request, 'rawApp/profile.html', {
        'profile': profile,
        'artworks': artworks
    })


@login_required
def my_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:

        Profile.objects.create(user=request.user)
        return redirect('my_profile')

    user_artworks = Artwork.objects.filter(author=request.user, is_approved=True)

    return render(request, 'rawApp/profile.html', {
        'profile': profile,
        'artworks': user_artworks
    })


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if form.cleaned_data.get('delete_avatar'):
                if profile.avatar:
                    profile.avatar.delete(save=False) 
                    profile.avatar = None
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'rawApp/edit_profile.html', {'form': form})


def register(request):

    print("Register view called") 
    if request.method == 'POST':
        print("POST data:", request.POST)

    user_form = UserCreationForm()
    artist_form = ArtistProfileForm()

    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        artist_form = ArtistProfileForm(request.POST)

        if user_form.is_valid() and artist_form.is_valid():
            try:
                user = user_form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('home')

            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
        else:
            errors = []
            for field, error_list in user_form.errors.items():
                errors.append(f"{user_form[field].label}: {', '.join(error_list)}")
            for field, error_list in artist_form.errors.items():
                errors.append(f"{artist_form[field].label}: {', '.join(error_list)}")
            messages.error(request, "Исправьте ошибки:<br>" + "<br>".join(errors))

    return render(request, 'rawApp/register.html', {
        'user_form': user_form,
        'artist_form': artist_form
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user, backend='rawApp.authentication_backends.EmailOrUsernameModelBackend')
            return redirect('home')
        else:
            messages.error(request, 'Неверные учетные данные')

    return render(request, 'rawApp/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')


def search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('home')

    results = Artwork.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(artist__name__icontains=query) |
        Q(categories__name__icontains=query),
        is_approved=True
    ).annotate(
        search_order=Case(
            When(title__icontains=query, then=3),
            When(description__icontains=query, then=2),
            When(artist__name__icontains=query, then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by('-search_order', '-created_at').distinct()

    return render(request, 'rawApp/search.html', {
        'results': results,
        'query': query
    })


def popular_artworks(request):
    popular = Artwork.objects.filter(is_approved=True).annotate(
        like_count=Count('likes')
    ).order_by('-like_count')
    return render(request, 'rawApp/popular.html', {'popular_artworks': popular})


def new_artworks(request):
    new = Artwork.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'rawApp/new.html', {'new_artworks': new})


def collections(request):
    categories = Category.objects.all()
    return render(request, 'rawApp/collections.html', {
        'categories': categories
    })

def submission_success(request):
    return render(request, 'rawApp/submission_success.html')


def account_settings(request):
    if request.method == 'POST':
        if 'update_info' in request.POST:
            form = UserSettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Данные успешно обновлены')
                return redirect('settings')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно изменен')
                return redirect('settings')
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки')

    user_form = UserSettingsForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    return render(request, 'rawApp/settings.html', {
        'user_form': user_form,
        'password_form': password_form
    })


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Аккаунт успешно удален')
        return redirect('home')
    return redirect('settings')

@staff_member_required
def moderation_list(request):
    artworks = Artwork.objects.filter(status='pending')
    return render(request, 'moderation/list.html', {'artworks': artworks})

@staff_member_required
def moderate_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['approved', 'rejected']:
            artwork.status = new_status
            artwork.save()
            return redirect('moderation_list')
    return render(request, 'moderation/detail.html', {'artwork': artwork})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    artworks = category.artwork_set.filter(is_approved=True)
    return render(request, 'rawApp/category_detail.html', {
        'category': category,
        'artworks': artworks
    })


@login_required
def toggle_like(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    user = request.user

    if user in artwork.likes.all():
        artwork.likes.remove(user)
    else:
        artwork.likes.add(user)

    return redirect('artwork_detail', pk=artwork_id)
