from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class CaptchaModel(models.Model):
    email = models.EmailField(unique= True)
    captcha = models.CharField(max_length=4)
    created_time = models.DateTimeField(auto_now=True)
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True, verbose_name='头像')
    # 关注系统：symmetrical=False 表示关注是单向的（我关注你，你不一定关注我）
    following = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='followers', 
        blank=True,
        verbose_name='关注的人'
    )    

    def __str__(self):
        return f"{self.user.username} 的头像"

    class Meta:
        verbose_name = '用户头像'
        verbose_name_plural = verbose_name