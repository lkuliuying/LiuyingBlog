from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liuyingauth', '0003_userprofile_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='captchamodel',
            name='captcha',
            field=models.CharField(max_length=6),
        ),
        migrations.AlterField(
            model_name='captchamodel',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='captchamodel',
            name='failed_attempts',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='captchamodel',
            name='last_sent_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name='captchamodel',
            options={'verbose_name': '邮箱验证码', 'verbose_name_plural': '邮箱验证码'},
        ),
    ]
