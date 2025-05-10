from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # slug = models.SlugField(max_length=50, unique=True, blank=True)
    # description = models.TextField(blank=True)
    # parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    #def save(self, *args, **kwargs):
    #    if not self.slug:
    #        self.slug = slugify(self.name)
    #    super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist', null=True, blank=True)
    name = models.CharField(max_length=100, default='Unknown Artist')
    bio = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        elif self.user and self.user.get_full_name():
            return self.user.get_full_name()
        return f"Художник #{self.id}"

    def display_name(self):
        if self.name:
            return self.name
        elif self.user and self.user.get_full_name():
            return self.user.get_full_name()
        return "Неизвестный художник"


class Artwork(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    )
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='artworks/')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, verbose_name='Художник', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='artworks')
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_artworks', blank=True)
    views = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    custom_artist = models.CharField(max_length=255, blank=True, null=True, verbose_name='Имя художника (если нет в списке)')
    # custom_categories = models.JSONField(default=list)
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.artwork}'

class Rating(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(1,1), (2,2), (3,3), (4,4), (5,5)])

class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    artworks = models.ManyToManyField(Artwork)
    is_public = models.BooleanField(default=True)

class CustomLoginView(LoginView):
    template_name = 'rawApp/login.html'

class CustomLogoutView(LogoutView):
    next_page = 'home'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()