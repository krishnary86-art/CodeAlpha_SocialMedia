from django.contrib import admin

from .models import Comment, Follow, Like, Post, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']

    def content_preview(self, obj):
        return obj.content[:60]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content_preview', 'created_at']

    def content_preview(self, obj):
        return obj.content[:60]


admin.site.register(Like)
admin.site.register(Follow)
