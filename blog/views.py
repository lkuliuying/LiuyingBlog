import os
import uuid
import traceback  # 引入 Python 的错误追踪模块
from django.conf import settings
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from .models import BlogCategory, Blog, BlogComment
from .forms import PubBlogForm
from django.http.response import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.views.decorators.vary import vary_on_cookie

#@vary_on_cookie
#@cache_page(60 * 5)
def index(request):
    blogs = Blog.objects.all()
    return render(request, 'index.html', context={'blogs': blogs})


def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'blog_detail.html', context={'blog': blog})


@require_http_methods(['GET', 'POST'])
def pub_blog(request):
    if not request.user.is_authenticated:
        return render(request, 'pub_blog.html', {'need_login': True})

    categories = BlogCategory.objects.all()

    if request.method == 'GET':
        return render(request, 'pub_blog.html', {'categories': categories})

    # POST 请求处理
    form = PubBlogForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')
        category_id = form.cleaned_data.get('category')
        blog = Blog.objects.create(
            title=title,
            content=content,
            category_id=category_id,
            author=request.user
        )
        return JsonResponse({
            'code': 200,
            'message': '博客发布成功',
            'data': {"blog_id": blog.id}
        })
    else:
        print(form.errors)
        return JsonResponse({
            'code': 400,
            'message': '博客发布失败',
            'errors': form.errors
        }, status=400)


@require_POST
@login_required()
def pub_comment(request):
    blog_id = request.POST.get('blog_id')
    comment = request.POST.get('comment')
    parent_id = request.POST.get('parent_id', '')
    BlogComment.objects.create(
        blog_id=blog_id,
        content=comment,
        author=request.user,
        parent_id=int(parent_id) if parent_id else None
    )
    return redirect(reverse('blog:blog_detail', args=[blog_id]))


@require_GET
def search(request):
    q = request.GET.get('q')
    blogs = Blog.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).all()
    return render(request, 'index.html', context={'blogs': blogs})
    
    
# 富文本编辑器不走常规的 CSRF 校验，用 @csrf_exempt 豁免，但加上 @login_required 保证安全
@csrf_exempt
@login_required
def upload_editor_file(request):
    if request.method != 'POST':
        return JsonResponse({"errno": 1, "message": "仅允许POST请求"})
    
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({"errno": 1, "message": "没有接收到文件"})

    # 1. 获取文件名和后缀
    filename = file.name
    ext = filename.split('.')[-1].lower()
    
    # 2. ★ 校验文件后缀白名单（支持常见图片和视频）
    allowed_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'mp4', 'webm']
    if ext not in allowed_exts:
        return JsonResponse({"errno": 1, "message": f"不支持的文件格式: .{ext}"})

    # 3. ★ 校验文件大小（限制为 10MB）
    if file.size > 10 * 1024 * 1024:
        return JsonResponse({"errno": 1, "message": "文件大小不能超过 10MB"})

    # 4. 生成唯一文件名
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 5. 按年/月划分文件夹
    date_path = timezone.now().strftime("%Y/%m")
    file_dir = os.path.join(settings.MEDIA_ROOT, 'upload', date_path)
    
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
        
    file_path = os.path.join(file_dir, new_filename)
    
    # 6. 写入硬盘
    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)
            
    # 7. 拼接访问 URL
    file_url = f"/media/upload/{date_path}/{new_filename}"
    
    # 8. 返回成功
    return JsonResponse({
        "errno": 0, 
        "data": {
            "url": file_url,
            "alt": filename,
            "href": ""
        }
    })
    
@login_required # 必须登录才能操作
@require_POST   # 安全起见，限制为 POST 请求
def toggle_like(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    # 判断当前用户是否已经在点赞列表里
    if request.user in blog.likes.all():
        blog.likes.remove(request.user) # 取消点赞
        is_liked = False
    else:
        blog.likes.add(request.user)    # 新增点赞
        is_liked = True
        
    # 返回最新状态和总点赞数给前端
    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'total_likes': blog.total_likes()
    })
    
@login_required
@require_POST
def toggle_collection(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    # 判断当前用户是否已经在收藏列表里
    if request.user in blog.collections.all():
        blog.collections.remove(request.user) # 取消收藏
        is_collected = False
    else:
        blog.collections.add(request.user)    # 新增收藏
        is_collected = True
        
    # 返回最新状态和总收藏数给前端
    return JsonResponse({
        'status': 'success',
        'is_collected': is_collected,
        'total_collections': blog.total_collections()
    })
    
@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    # 2. 查询这里也要改！
    comment = get_object_or_404(BlogComment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        is_liked = False
    else:
        comment.likes.add(request.user)
        is_liked = True
        
    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'total_likes': comment.total_likes()
    })

