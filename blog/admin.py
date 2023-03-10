from django.contrib import admin

from blog.models import Blog, Comment


# Register your models here.


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'text', 'post_date', "is_posted")

    search_fields = ['title']
    list_filter = ["is_posted", 'post_date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'author', 'text', "is_published")
