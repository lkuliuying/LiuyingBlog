from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Blog
from .serializers import BlogSerializer

@api_view(['GET'])
def api_blog_list(request):
    """获取博客列表接口"""
    blogs = Blog.objects.all().order_by('-pub_time')
    # 1. 序列化（把Python对象转成JSON字典）
    serializer = BlogSerializer(blogs, many=True)
    # 2. 因为我们在settings里配了分页，所以要用分页类包装一下
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    # 3. 按每页10条进行分页
    result_page = paginator.paginate_queryset(serializer.data, request)
    # 4. 返回标准的带分页信息的JSON
    return paginator.get_paginated_response(result_page)