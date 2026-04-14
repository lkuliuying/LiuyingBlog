from django import template

register = template.Library()


@register.inclusion_tag('comments/comment_tree.html', takes_context=True)
def render_comment_tree(context, comments):
    # 判断传入的是原始 QuerySet（模型对象）还是已经构建好的嵌套列表（字典）
    if comments and isinstance(comments[0], dict):
        tree = comments  # 已经是树结构，直接使用
    else:
        tree = build_tree(comments)  # 平铺的 QuerySet，构建成树
    return {
        'tree': tree,
        'request': context['request'],
    }


def build_tree(comments):
    """将平铺的评论 QuerySet 构建成嵌套列表"""
    comment_dict = {}
    for c in comments:
        comment_dict[c.id] = {
            'comment': c,
            'children': []
        }
    tree = []
    for c in comments:
        if c.parent_id and c.parent_id in comment_dict:
            comment_dict[c.parent_id]['children'].append(comment_dict[c.id])
        else:
            tree.append(comment_dict[c.id])
    return tree