"""
认证 / 用户中心相关序列化器。

用户登录支持邮箱或用户名（沿用 backends.py 的 EmailOrUsernameModelBackend），
所以登录字段叫 account 而不是 username 或 email，免得歧义。
"""
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CaptchaModel, UserProfile

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    """当前登录用户的精简信息（前端 store 持有）。"""
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar']

    def get_avatar(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.avatar:
            return profile.avatar.url
        return ''


class RegisterSerializer(serializers.Serializer):
    """注册：用户名 + 邮箱 + 邮件验证码 + 密码。
    校验逻辑直接搬自原 RegisterForm。
    """
    username = serializers.CharField(min_length=2, max_length=20, error_messages={
        'required': '用户名不能为空',
        'min_length': '用户名长度不能小于2',
        'max_length': '用户名长度不能大于20',
    })
    email = serializers.EmailField(error_messages={
        'required': '邮箱不能为空',
        'invalid': '邮箱格式不正确',
    })
    captcha = serializers.CharField(min_length=4, max_length=6, error_messages={
        'required': '验证码不能为空',
        'min_length': '验证码长度不正确',
        'max_length': '验证码长度不正确',
    })
    password = serializers.CharField(min_length=6, max_length=20, write_only=True, error_messages={
        'required': '密码不能为空',
        'min_length': '密码长度不能小于6',
        'max_length': '密码长度不能大于20',
    })

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已注册')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已被占用')
        return value

    def validate(self, attrs):
        captcha = attrs.get('captcha')
        email = attrs.get('email')
        record = CaptchaModel.objects.filter(email=email).first()
        if not record:
            raise serializers.ValidationError({'captcha': '请先获取验证码'})

        # 5 分钟有效期
        if (timezone.now() - record.created_time).total_seconds() > 5 * 60:
            record.delete()
            raise serializers.ValidationError({'captcha': '验证码已过期，请重新获取'})

        # 失败次数锁定：连续 5 次错误后必须重新获取
        if record.failed_attempts >= 5:
            record.delete()
            raise serializers.ValidationError({'captcha': '错误次数过多，请重新获取验证码'})

        if record.captcha != captcha:
            record.failed_attempts += 1
            record.save(update_fields=['failed_attempts'])
            remaining = 5 - record.failed_attempts
            if remaining <= 0:
                record.delete()
                raise serializers.ValidationError({'captcha': '错误次数过多，请重新获取验证码'})
            raise serializers.ValidationError({'captcha': f'验证码错误，剩余尝试次数 {remaining} 次'})

        # 校验通过，删除验证码记录
        record.delete()
        return attrs

    def create(self, validated_data):
        validated_data.pop('captcha')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.get_or_create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """邮箱或用户名 + 密码 登录，成功返回 access/refresh token。"""
    account = serializers.CharField(error_messages={'required': '账号不能为空'})
    password = serializers.CharField(write_only=True, error_messages={'required': '密码不能为空'})

    def validate(self, attrs):
        request = self.context.get('request')
        # backends.py 里 username 字段同时承载邮箱/用户名
        user = authenticate(request, username=attrs['account'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError({'detail': '账号或密码错误'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': '该账号已被禁用'})

        refresh = RefreshToken.for_user(user)
        attrs['user'] = user
        attrs['access'] = str(refresh.access_token)
        attrs['refresh'] = str(refresh)
        return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):
    """修改用户名 / 邮箱。"""
    username = serializers.CharField(required=True, error_messages={'required': '用户名不能为空'})
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def validate_username(self, value):
        user = self.instance
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('该用户名已被占用，请换一个')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True, min_length=6)
    new_password2 = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': '旧密码不正确'})
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': '两次输入的新密码不一致'})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

    def save(self, **kwargs):
        user = self.context['request'].user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.avatar = self.validated_data['avatar']
        profile.save()
        return profile
