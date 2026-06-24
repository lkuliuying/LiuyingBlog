"""富文本内容净化工具。

wangEditor 产出 HTML 直接入库，列表/详情页前端用 v-html 渲染，
所以必须在写库前过滤掉危险标签与属性，杜绝存储型 XSS。

允许的标签覆盖博客常用排版需求：标题、段落、列表、引用、代码、链接、图片、表格等。
"""
import re

import bleach
from bleach.css_sanitizer import CSSSanitizer

# 允许的标签白名单
ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'blockquote', 'br', 'caption', 'cite', 'code',
    'col', 'colgroup', 'dd', 'del', 'div', 'dl', 'dt', 'em', 'figcaption',
    'figure', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
    'ins', 'kbd', 'li', 'mark', 'ol', 'p', 'pre', 'q', 's', 'samp',
    'small', 'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td',
    'tfoot', 'th', 'thead', 'tr', 'u', 'ul', 'video', 'source',
]

# 允许的属性白名单
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title'],
    'abbr': ['title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'video': ['src', 'controls', 'width', 'height', 'poster'],
    'source': ['src', 'type'],
    'code': ['class'],  # highlight.js 用 class="language-xxx"
    'pre': ['class'],
    'span': ['class'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
    'col': ['span'],
    'colgroup': ['span'],
}

# 允许的 CSS 属性（限定在 style="" 内）
ALLOWED_CSS_PROPERTIES = [
    'color', 'background-color', 'text-align', 'text-decoration',
    'font-weight', 'font-style', 'font-size', 'line-height',
    'margin', 'margin-left', 'margin-right', 'margin-top', 'margin-bottom',
    'padding', 'padding-left', 'padding-right', 'padding-top', 'padding-bottom',
    'border', 'border-color', 'border-style', 'border-width', 'border-radius',
    'width', 'height', 'max-width', 'max-height',
    'display', 'float', 'vertical-align',
]

# 链接协议白名单
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

# CSSSanitizer 实例：bleach.clean 的 css_sanitizer 参数需要对象而非列表
_CSS_SANITIZER = CSSSanitizer(allowed_css_properties=ALLOWED_CSS_PROPERTIES)

# 匹配 <a href="http(s)://..."> 形式，统一补 rel="noopener noreferrer"
_EXTERNAL_LINK_RE = re.compile(
    r'(<a\b[^>]*\bhref=["\']https?://[^"\']*["\'])([^>]*>)',
    re.IGNORECASE,
)


def sanitize_html(html: str) -> str:
    """净化富文本 HTML，移除危险标签/属性/协议。

    传入 None 或空字符串返回空串，避免在序列化器里再判空。
    """
    if not html:
        return ''

    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        css_sanitizer=_CSS_SANITIZER,
        strip=True,
    )
    # 给外链补 rel="noopener noreferrer"，防止 reverse tabnabbing
    cleaned = _EXTERNAL_LINK_RE.sub(
        lambda m: m.group(1) + ' rel="noopener noreferrer"' + m.group(2),
        cleaned,
    )
    return cleaned
