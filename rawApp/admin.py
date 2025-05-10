from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *
from .models import Category, Artist, Artwork

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'created_at', 'author', 'is_approved')
    filter_horizontal = ('categories', 'likes')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'artist')
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)

    approve_selected.short_description = "Одобрить выбранные работы"

admin.site.register(Profile)
admin.site.register(Artist)
admin.site.register(Category)
admin.site.register(Comment)