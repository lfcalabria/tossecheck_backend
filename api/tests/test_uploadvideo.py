from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from api.models import *

class TestUploadVideo(TestCase):
    def setUp(self):
        self.client = Client()
        self.pet = baker.make(Pet)
        self.url = '/api/v1/upload/video/'

    def test_upload_success(self):
        """POST with valid file and pet_uuid returns 201."""
        video_file = SimpleUploadedFile(
            "test.mp4", b"file_content", content_type="video/mp4"
        )
        data = {'pet_uuid': str(self.pet.uuid), 'file': video_file}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_upload_missing_pet_uuid(self):
        """POST without pet_uuid returns 400."""
        video_file = SimpleUploadedFile(
            "test.mp4", b"content", content_type="video/mp4"
        )
        data = {'file': video_file}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_upload_missing_file(self):
        """POST without file returns 400."""
        data = {'pet_uuid': str(self.pet.uuid)}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_upload_method_not_allowed_get(self):
        """GET returns 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_upload_method_not_allowed_put(self):
        """PUT returns 405."""
        response = self.client.put(self.url, data={}, format='multipart')
        self.assertEqual(response.status_code, 405)

    def test_upload_method_not_allowed_delete(self):
        """DELETE returns 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_upload_sem_extensao(self):
        """Arquivo sem extensão → fallback .mp4."""
        video_file = SimpleUploadedFile(
            "arquivo_sem_ext", b"file_content", content_type="video/mp4"
        )
        data = {'pet_uuid': str(self.pet.uuid), 'file': video_file}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_upload_exception_generica(self):
        """Erro inesperado no upload → except Exception → 400."""
        from unittest.mock import patch
        video_file = SimpleUploadedFile(
            "test.mp4", b"file_content", content_type="video/mp4"
        )
        data = {'pet_uuid': str(self.pet.uuid), 'file': video_file}
        with patch('api.views.VideoPet.objects.create', side_effect=Exception('Erro inesperado')):
            response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
