from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class CaptchaEmailTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('liuyingauth.api_views.send_mail')
    def test_captcha_email_contains_html_and_plain_text_versions(self, mocked_send_mail):
        response = self.client.post(
            reverse('liuyingauth:captcha'),
            {'email': 'reader@example.com'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        mocked_send_mail.assert_called_once()

        call_kwargs = mocked_send_mail.call_args.kwargs
        self.assertIn('5 分钟内有效', call_kwargs['message'])
        self.assertIn('html_message', call_kwargs)
        self.assertIn('流萤博客', call_kwargs['html_message'])
        self.assertIn('本次验证码', call_kwargs['html_message'])
        self.assertIn('background-color:#10aeb5', call_kwargs['html_message'])
        self.assertIn('background-color:#e7ecee', call_kwargs['html_message'])
