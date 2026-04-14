from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name='liuyingauth'

urlpatterns = [
    path('login',views.lylogin,name='login'),

    path('logout',views.lylogout,name='logout'),

    path('register',views.register,name='register'),


    path('captcha',views.send_email_captcha,name='email_captcha'), 
    
    
    path('profile/', views.user_profile, name='profile'),
    
    path('upload_avatar/', views.upload_avatar, name='upload_avatar'),
     
    path('profile/update_info/', views.update_profile_info, name='update_profile_info'),
    path('profile/update_password/', views.update_password, name='update_password'),
    
    
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)