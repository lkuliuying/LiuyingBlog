import re
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
# Create your models here.
class BlogCategory(models.Model):
    name = models.CharField(max_length=20,verbose_name='分类名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '博客分类'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    title = models.CharField(max_length=200,verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    pub_time = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    updated_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, verbose_name='分类')
    # 点赞：一篇文章可以被多个人点赞，一个人也可以点赞多篇文章
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_blogs', 
        blank=True,
        verbose_name='点赞用户'
    )
    
    # 收藏：同理
    collections = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='collected_blogs', 
        blank=True,
        verbose_name='收藏用户'
    )

    # 为了方便前端展示，可以加上这两个辅助方法
    def total_likes(self):
        return self.likes.count()
        
    def total_collections(self):
        return self.collections.count()
    
    @property
    def first_image(self):
        # 用正则从 HTML 内容中匹配第一张图片的 src
        match = re.search(r'<img[^>]+src="([^"]+)"', self.content)
        if match:
            return match.group(1)
        # 如果没有图片，返回 None
        return None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name
        ordering = ['-pub_time']


class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments", verbose_name='所属博客')
    content = models.TextField(verbose_name='内容')
    pub_time = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='replies',
        verbose_name='父评论'
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_comments', 
        blank=True,
        verbose_name='点赞用户'
    )

    # 辅助方法
    def total_likes(self):
        return self.likes.count()
    

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '博客评论'
        verbose_name_plural = verbose_name
        ordering = ['-pub_time']