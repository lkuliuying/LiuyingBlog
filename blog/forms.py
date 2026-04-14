from django import forms

class PubBlogForm(forms.Form):
    title = forms.CharField(max_length=200,min_length=2,error_messages={
                               'required':'标题不能为空',
                               'min_length':'标题长度不能小于2',
                               'max_length':'标题长度不能大于200'
                             })
    content = forms.CharField(min_length=10,error_messages={
                               'required':'内容不能为空',
                               'min_length':'内容长度不能小于10'
                             })
    category = forms.IntegerField(error_messages={
                               'required':'分类不能为空'
                             })