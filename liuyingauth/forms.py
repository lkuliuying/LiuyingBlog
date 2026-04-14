from django import forms
from django.contrib.auth import get_user_model
from .models import CaptchaModel

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
        captcha_model.delete()
        return captcha


class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={
                               'required':'邮箱不能为空',
                               'invalid':'邮箱格式不正确'
                             })
    password = forms.CharField(max_length=20,min_length=6,error_messages={
                               'required':'密码不能为空',
                               'min_length':'密码长度不能小于6',
                               'max_length':'密码长度不能大于20'
                             })
    remerber = forms.IntegerField(required=False)