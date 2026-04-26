from django.contrib import admin
from .models import CaptchaModel, UserProfile

# Register your models here.

@admin.register(CaptchaModel)
class CaptchaModelAdmin(admin.ModelAdmin):
    list_display = ('email', 'captcha', 'created_time')
    search_fields = ('email',)
    list_filter = ('created_time',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')
    search_fields = ('user__username', 'user__email')
