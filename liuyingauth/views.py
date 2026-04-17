from django.utils import timezone
from django.shortcuts import render, redirect, reverse
from django.http.response import JsonResponse
import string
import random
import os
from django.core.mail import send_mail
from .models import CaptchaModel
from django.views.decorators.http import require_http_methods,require_POST
from .forms import RegisterForm,LoginForm
from django.contrib.auth import login,logout,get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from blog.models import Blog,BlogComment
from .models import UserProfile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, logout, get_user_model, authenticate 


User=get_user_model()


@require_http_methods(['GET', 'POST'])
def lylogin(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    form = LoginForm(request.POST)
    if form.is_valid():
        account = form.cleaned_data.get('email')  # 这里虽然变量叫 email，但实际上用户填邮箱或用户名都可以
        password = form.cleaned_data.get('password')
        remember = request.POST.get('remember')
        
        # ★ 优雅重构：直接把账号密码扔给 Django 的 authenticate 去处理
        user = authenticate(request, username=account, password=password)

        if user is not None:
            # 认证成功，执行登录
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            return redirect('/')
        else:
            messages.error(request, '账号或密码错误') # 提示语改成账号，更严谨
            return render(request, 'login.html', {'form': form})
    else:
        return render(request, 'login.html', {'form': form})
        
        
def lylogout(request):
    logout(request)
    return redirect('/')



@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    form = RegisterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        username = form.cleaned_data.get('username')
        User.objects.create_user(email=email, username=username, password=password)
        messages.success(request, '注册成功！请登录')
        return redirect(reverse('liuyingauth:login'))
    else:
        print(form.errors)
        return render(request, 'register.html', {'form': form})


def send_email_captcha(request):
    # ?email=xxx
    email=request.GET.get('email')
    if not email:
        return JsonResponse({
            'code':400,
            'message':'邮箱不能为空'
        })
        
    # ★ 防刷限流逻辑：查询数据库中该邮箱最近一次的发送记录
    captcha_record = CaptchaModel.objects.filter(email=email).first()
    if captcha_record:
        # 计算当前时间与上一次发送时间的差值
        time_diff = timezone.now() - captcha_record.created_time
        # 如果距离上次发送还不到 60 秒，直接拦截
        if time_diff.total_seconds() < 60:
            return JsonResponse({
                'code': 400,
                'message': '验证码发送太频繁，请 60 秒后再试'
            })
            
    # 生成验证码
    captcha = "".join(random.sample(string.digits, 4))
    
    # 存入数据库（update_or_create 会自动更新 created_time）
    CaptchaModel.objects.update_or_create(email=email,defaults={'captcha':captcha})
    #print(captcha)
    # 发送邮件
    try:
        send_mail(
            subject='流萤博客注册验证码',
            message='您的验证码是：%s，有效时间为5分钟。' % captcha,
            from_email=os.getenv('EMAIL_HOST_USER', '3302393536@qq.com'), # 顺便这里也规范一下
            recipient_list=[email],
            fail_silently=False, # 发送失败抛出异常，方便查错
        )
        return JsonResponse({
            'code': 200,
            'message': '验证码发送成功',
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'邮件发送失败，具体错误：{str(e)}'
        })
@login_required
def user_profile(request):
    # 第94行：查询当前用户发布的博客
    user = request.user
    user_blogs = Blog.objects.filter(author=request.user).order_by('-pub_time')
    user_comments = BlogComment.objects.filter(author=request.user).select_related('blog').order_by('-pub_time')
    liked_blogs = user.liked_blogs.all().order_by('-pub_time')
    collected_blogs = user.collected_blogs.all().order_by('-pub_time')
    return render(request, 'user_profile.html', {
        'user_blogs': user_blogs,
        'user': request.user,
        'user_comments':user_comments,
        'liked_blogs': liked_blogs,
        'collected_blogs': collected_blogs,
   })
   
   
@login_required
def upload_avatar(request):
    if request.method == 'POST':
        avatar_file = request.FILES.get('avatar')
        if avatar_file:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.avatar = avatar_file
            profile.save()
            return JsonResponse({
                'code': 200,
                'msg': '上传成功',
                'avatar_url': profile.avatar.url,
            })
    return JsonResponse({'code': 400, 'msg': '上传失败'}, status=400)
    
    
@require_POST
@login_required
def update_profile_info(request):
    """修改用户名和邮箱"""
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    user = request.user

    if not username:
        return JsonResponse({'code': 400, 'msg': '用户名不能为空'})
    
    # 检查用户名是否被别人占了（排除自己）
    if User.objects.filter(username=username).exclude(id=user.id).exists():
        return JsonResponse({'code': 400, 'msg': '该用户名已被占用，请换一个'})

    user.username = username
    user.email = email
    user.save()

    return JsonResponse({
        'code': 200, 
        'msg': '基本信息修改成功', 
        'new_username': user.username  # 返回新用户名供前端实时更新
    })

@require_POST
@login_required
def update_password(request):
    """修改密码"""
    old_password = request.POST.get('old_password', '')
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    user = request.user

    if not user.check_password(old_password):
        return JsonResponse({'code': 400, 'msg': '旧密码不正确'})
    
    if new_password1 != new_password2:
        return JsonResponse({'code': 400, 'msg': '两次输入的新密码不一致'})
    
    if len(new_password1) < 6:
        return JsonResponse({'code': 400, 'msg': '新密码长度不能少于6位'})

    user.set_password(new_password1)
    user.save()
    
    # ★ 这一步很重要！修改密码后，保持当前用户的登录状态不掉线
    update_session_auth_hash(request, user)

    return JsonResponse({'code': 200, 'msg': '密码修改成功'})
    