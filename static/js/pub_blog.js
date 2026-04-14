window.onload = function () {
    const {createEditor, createToolbar} = window.wangEditor

    const editorConfig = {
        placeholder: 'Type here...',
        onChange(editor) {
            const html = editor.getHtml()
            console.log('editor content', html)
        },
        // ★ 正确的拼写和位置
               MENU_CONF: {
            uploadImage: {
                server: '/upload_editor/',
                fieldName: 'file',
                allowedFileTypes: ['image/*'], 
                maxFileSize: 10 * 1024 * 1024, // 图片限制 10MB
                onError(file, err, res) {
                    alert('上传失败: ' + err.message)
                }
            }
        }
    }

    const editor = createEditor({
        selector: '#editor-container',
        html: '<p><br></p>',
        mode: 'default', 
        config: editorConfig // ★ 引用上面的配置
    })

    const toolbarConfig = {}

    createToolbar({
        editor,
        selector: '#toolbar-container',
        config: toolbarConfig,
        mode: 'default', 
    })

    $("#submit-btn").click(function (event){
        event.preventDefault();
        let title = $("input[name='title']").val();
        let category = $("#category-select").val();
        let content = editor.getHtml();
        let csrfmiddlewaretoken = $("input[name='csrfmiddlewaretoken']").val();
        
        $.ajax({
            url: '/blog/pub',
            method: 'POST',
            data: {
                title: title,
                category: category,
                content: content,
                csrfmiddlewaretoken: csrfmiddlewaretoken
            },
            success: function (result) {
                if (result.code === 200) {
                    alert('发布成功');
                    let blog_id = result['data']['blog_id'];
                    window.location.href = '/blog/detail/'+blog_id;
                } else {
                    alert(result['message']);
                }
            },
            error: function (error) {
                alert('网络错误，请稍后重试');
            }
        });
    });
}