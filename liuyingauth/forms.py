from django import forms
from django.contrib.auth import get_user_model
from .models import CaptchaModel
from django.utils import timezone

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20,min_length=2,error_messages={
                               'required':'用户名不能为空',
                               'min_length':'用户名长度不能小于2',
                               'max_length':'用户名长度不能大于20'
                             })
    email = forms.EmailField(error_messages={
                               'required':'邮箱不能为空',
                               'invalid':'邮箱格式不正确'
                             })

    captcha = forms.CharField(max_length=4,min_length=4,error_messages={
                               'required':'验证码不能为空',
                               'min_length':'验证码长度不能小于4',
                               'max_length':'验证码长度不能大于4'
                             })

    password = forms.CharField(max_length=20,min_length=6,error_messages={
                               'required':'密码不能为空',
                               'min_length':'密码长度不能小于6',
                               'max_length':'密码长度不能大于20'
                             })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exists=User.objects.filter(email=email).exists()
        if exists:
            raise forms.ValidationError('邮箱已注册')
        return email

    def clean_captcha(self):
        captcha = self.cleaned_data.get('captcha')
        email = self.cleaned_data.get('email')
        captcha_model = CaptchaModel.objects.filter(email=email,captcha=captcha).first()
        if not captcha_model:
            raise forms.ValidationError('验证码错误或邮箱不存在')
        time_diff = timezone.now() - captcha_model.created_time
        if time_diff.total_seconds() > 5 * 60:
            captcha_model.delete() # 顺手清理掉这个过期的废弃验证码
            raise forms.ValidationError('验证码已过期，请重新获取')
        captcha_model.delete()
        return captcha


class LoginForm(forms.Form):
    email = forms.CharField(
               label='邮箱或用户名',
               max_length=150,
               error_messages={
                               'required':'邮箱不能为空',
                               'invalid':'邮箱格式不正确'
                             })
    password = forms.CharField(
                label='密码',
                max_length=20,
                min_length=6,           
                error_messages={
                               'required':'密码不能为空',
                               'min_length':'密码长度不能小于6',
                               'max_length':'密码长度不能大于20'
                             })
    remerber = forms.IntegerField(required=False)