from django.test import TestCase
from model_bakery import baker
from api.models import VideoPet
from api.serializers import VideoPetSerializer

class TestVideoPetSerializer(TestCase):
    def setUp(self):
        self.video = baker.make(VideoPet)

    def test_contains_expected_fields(self):
        serializer = VideoPetSerializer(instance=self.video)
        expected_fields = {'id', 'uuid', 'pet_uuid', 'arquivo', 'data_upload'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = VideoPetSerializer(instance=self.video)
        self.assertIn('id', serializer.data)
        self.assertIn('uuid', serializer.data)
        self.assertIn('data_upload', serializer.data)