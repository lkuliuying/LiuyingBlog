import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class EditorUploadTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='editor',
            password='safe-test-password',
        )
        self.client.force_authenticate(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_upload_local_image_returns_wangeditor_payload(self):
        image = SimpleUploadedFile(
            'cover.png',
            (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
                b'\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde'
            ),
            content_type='image/png',
        )

        response = self.client.post(
            '/api/uploads/editor/',
            {'file': image},
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['url'].startswith('/media/upload/'))
        self.assertEqual(response.data['data']['alt'], 'cover.png')

    def test_rejects_non_image_file(self):
        text = SimpleUploadedFile(
            'notes.txt',
            b'not an image',
            content_type='text/plain',
        )

        response = self.client.post(
            '/api/uploads/editor/',
            {'file': text},
            format='multipart',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errno'], 1)
