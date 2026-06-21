from django.contrib import admin
from .models import Blog, BlogCategory, BlogComment

# 美化博客展示
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'pub_time')
    list_per_page = 20
    list_display_links = ('id', 'title')
    list_filter = ('category', 'pub_time')
    search_fields = ('title', 'content')

# 美化评论展示
@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'blog', 'content_short', 'pub_time')
    list_filter = ('pub_time',)
    search_fields = ('content', 'author__username')
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = '评论内容'

# 美化分类展示
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')