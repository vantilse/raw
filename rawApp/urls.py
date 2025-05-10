from django.urls import path
from . import views
from .views import account_settings, delete_account
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artwork/<int:artwork_id>/like/', views.toggle_like, name='toggle_like'),
    path('add/', views.add_artwork, name='add_artwork'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('category/<int:pk>/', views.category_view, name='category'),
    path('popular/', views.popular_artworks, name='popular'),
    path('new/', views.new_artworks, name='new'),
    path('collections/', views.collections, name='collections'),
    # path('create-artist/', views.create_artist_profile, name='create_artist_profile'),
    path('artists/', views.artist_list, name='artist_list'),
    path('submission-success/', views.submission_success, name='submission_success'),
    path('settings/', account_settings, name='settings'),
    path('delete-account/', delete_account, name='delete_account'),
    path('moderation/', views.moderation_list, name='moderation_list'),
    path('moderate/<int:pk>/', views.moderate_artwork, name='moderate_artwork'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)