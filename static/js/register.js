$(function() {
    function bindCaptchaBtnClick(){
        $('#captcha-btn').click(function () {
            let $this = $(this)
            let email = $("input[name='email']").val()
            if (!email) {
                alert('请先输入邮箱！');
                return;
            }

            $this.off('click')

            $.ajax({
                url: '/auth/captcha',
                data: { email: email },
                method: 'get',
                success: function (result) {
                    if (result.code === 200) {
                        alert('验证码发送成功！');
                        let countdown = 60;
                        let timer = setInterval(function(){
                            if(countdown <= 0){
                                $this.text('获取验证码');
                                clearInterval(timer);
                                bindCaptchaBtnClick();
                            } else {
                                countdown--;
                                $this.text(countdown + '秒后重新获取');
                            }
                        }, 1000);
                    } else {
                        alert(result.message || '验证码发送失败');
                        bindCaptchaBtnClick();
                    }
                },
                error: function (error) {
                    console.log(error);
                    alert('网络错误，请稍后重试');
                    bindCaptchaBtnClick();
                }
            });
        });
    }
    bindCaptchaBtnClick();
});
