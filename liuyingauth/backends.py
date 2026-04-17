from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    自定义认证后端：允许用户使用 邮箱 或 用户名 进行登录
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 这里的 username 参数接收前端传来的账号（可能是邮箱，也可能是用户名）
        try:
            # Q 对象允许我们进行 OR 查询：邮箱匹配 OR 用户名匹配
            user = User.objects.get(Q(email=username) | Q(username=username))
        except User.DoesNotExist:
            return None
        
        # 验证密码，并检查账号是否被禁用 (is_active)
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None