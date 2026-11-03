"""
Comprehensive automated tests for AgrivisionAI / PlantMD.
Tests validators, class configurations, softmax normalization,
health check endpoints, Ajax image uploads, and plant disease views.
"""

import io
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.common.classes_config import get_class_names, get_disease_details, get_plant_config
from apps.common.predictor import apply_softmax_if_needed
from apps.common.validators import validate_uploaded_image
import numpy as np


def create_dummy_image_file(name="leaf.jpg", fmt="JPEG", size=(100, 100), color=(34, 139, 34)) -> SimpleUploadedFile:
    """Helper to generate an in-memory valid image file for upload testing."""
    stream = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(stream, format=fmt)
    stream.seek(0)
    content_type = f"image/{fmt.lower()}"
    if fmt.upper() == "JPEG":
        content_type = "image/jpeg"
    return SimpleUploadedFile(name, stream.read(), content_type=content_type)


class InputValidationTests(TestCase):
    """Test image upload validation rules and security limits."""

    def test_valid_image(self):
        uploaded = create_dummy_image_file("sample.jpg", "JPEG")
        is_valid, err = validate_uploaded_image(uploaded)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_none_file(self):
        is_valid, err = validate_uploaded_image(None)
        self.assertFalse(is_valid)
        self.assertIn("No image file", err)

    def test_invalid_extension(self):
        fake_file = SimpleUploadedFile("malicious.exe", b"binarycontent", content_type="application/octet-stream")
        is_valid, err = validate_uploaded_image(fake_file)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported file extension", err)

    def test_corrupt_image_content(self):
        corrupt = SimpleUploadedFile("broken.png", b"not-a-valid-png-stream", content_type="image/png")
        is_valid, err = validate_uploaded_image(corrupt)
        self.assertFalse(is_valid)
        self.assertIn("corrupt or not a recognized image", err)

    def test_file_exceeding_size_limit(self):
        uploaded = create_dummy_image_file("huge.jpg", "JPEG")
        uploaded.size = 15 * 1024 * 1024  # 15 MB
        is_valid, err = validate_uploaded_image(uploaded)
        self.assertFalse(is_valid)
        self.assertIn("exceeds the maximum allowed size", err)


class ClassesConfigTests(TestCase):
    """Test centralized disease taxonomy and configuration."""

    def test_hibiscus_classes_loaded(self):
        classes = get_class_names('hibiscus')
        self.assertEqual(len(classes), 8)
        # Verify exact alignment with apps/hibiscus/hibiscus.ipynb:
        expected = [
            'Citrus Spot',
            'Early Mild Spotting',
            'Fungal Infected',
            'Healthy',
            'Mild Edge Damage',
            'Senescent',
            'Slightly Diseased',
            'Wrinkled Leaf',
        ]
        self.assertEqual(classes, expected)
        for placeholder in ['1', '2', '4', '5', '6']:
            self.assertNotIn(placeholder, classes)

    def test_zucchini_classes_loaded(self):
        classes = get_class_names('zucchini')
        self.assertEqual(len(classes), 9)
        self.assertIn('Yellow Mosaic Virus', classes)
        self.assertIn('Downy Mildew', classes)
        # Verify placeholders and typos fixed
        for placeholder in ['1', '4', '5', '7', 'Downy Midew']:
            self.assertNotIn(placeholder, classes)

    def test_disease_details_and_treatment(self):
        details = get_disease_details('zucchini', 0)
        self.assertEqual(details['class'], 'Yellow Mosaic Virus')
        self.assertTrue(len(details['treatment']) > 0)
        self.assertEqual(details['status'], 'Diseased')


class SoftmaxSafeguardTests(TestCase):
    """Test softmax normalization behavior for logits vs probabilities."""

    def test_already_softmax_probabilities_unchanged(self):
        probs = np.array([[0.1, 0.7, 0.2]])
        result = apply_softmax_if_needed(probs)
        np.testing.assert_allclose(result, probs, atol=1e-5)

    def test_raw_logits_converted_to_probabilities(self):
        logits = np.array([[12.5, 3.2, -1.0]])
        result = apply_softmax_if_needed(logits)
        self.assertAlmostEqual(float(np.sum(result)), 1.0, places=4)
        self.assertTrue(result[0, 0] > result[0, 1] > result[0, 2])


class PredictorArchitectureTests(TestCase):
    """Test model-specific preprocessing strategies and automatic architecture detection."""

    def test_zucchini_preprocess_preserves_raw_rgb_range(self):
        """EfficientNet models require raw [0, 255] RGB float32 inputs."""
        from apps.zucchini.source.predictor import predictor
        test_img = create_dummy_image_file("zucchini_leaf.jpg", color=(40, 180, 40))
        tensor = predictor.preprocess(test_img)
        self.assertEqual(tensor.shape, (1, 224, 224, 3))
        # Value range must be in [0, 255], strictly non-negative
        self.assertTrue(np.all(tensor >= 0.0))
        self.assertTrue(np.all(tensor <= 255.0))
        # Mode must resolve to raw
        self.assertEqual(predictor.get_preprocess_mode(), "raw")

    def test_hibiscus_preprocess_scales_to_mobilenet_range(self):
        """MobileNetV2 expects [-1, 1] range."""
        from apps.hibiscus.source.predictor import predictor
        test_img = create_dummy_image_file("hibiscus_leaf.jpg", color=(40, 180, 40))
        tensor = predictor.preprocess(test_img)
        self.assertEqual(tensor.shape, (1, 224, 224, 3))
        self.assertTrue(np.all(tensor >= -1.05))
        self.assertTrue(np.all(tensor <= 1.05))
        self.assertEqual(predictor.get_preprocess_mode(), "mobilenet_v2")


class EndpointsAndViewsTests(TestCase):
    """Test HTTP endpoints, views, rendering, and Ajax interactions."""

    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('models', data)
        self.assertIn('hibiscus', data['models'])
        self.assertIn('zucchini', data['models'])

    def test_homepage_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hibiscus Leaf Disease")
        self.assertContains(response, "Zucchini Leaf Disease")
        self.assertContains(response, "Tea Leaf Disease")
        self.assertContains(response, "Papaya Leaf Disease")

    def test_hibiscus_get_view(self):
        response = self.client.get('/hibiscus/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hibiscus Leaf")

    def test_zucchini_get_view(self):
        response = self.client.get('/zucchini/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zucchini Leaf")

    def test_tea_leaf_get_view(self):
        response = self.client.get('/tea-leaf/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tea Leaf")

    def test_papaya_get_view(self):
        response = self.client.get('/papaya/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Papaya Leaf")

    def test_post_with_invalid_file(self):
        fake_file = SimpleUploadedFile("bad.txt", b"not an image", content_type="text/plain")
        response = self.client.post('/hibiscus/', {'image': fake_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsupported file extension")

    def test_post_json_api_mode(self):
        fake_file = SimpleUploadedFile("bad.txt", b"not an image", content_type="text/plain")
        response = self.client.post('/hibiscus/?format=json', {'image': fake_file})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('error', data)

    def test_post_ajax_success_returns_image_and_prediction(self):
        """Verify Ajax submission responds with JSON containing prediction and base64 image URL."""
        image = create_dummy_image_file("hibiscus_test.jpg", "JPEG")
        response = self.client.post(
            '/hibiscus/',
            {'image': image},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('result', data)
        result = data['result']
        self.assertIn('class', result)
        self.assertIn('confidence', result)
        self.assertIn('image_url', result)
        self.assertTrue(result['image_url'].startswith('data:image/jpeg;base64,'))
        self.assertIn('top_scores', result)

    def test_post_ajax_invalid_file_returns_error(self):
        """Verify Ajax submission with invalid file returns HTTP 400 and error message."""
        fake_file = SimpleUploadedFile("bad.txt", b"plain text", content_type="text/plain")
        response = self.client.post(
            '/zucchini/',
            {'image': fake_file},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('error', data)

    def test_post_ajax_zucchini_success_returns_valid_prediction(self):
        """Verify Zucchini Ajax prediction returns valid diagnosis without collapsing or placeholders."""
        image = create_dummy_image_file("zucchini_sample.jpg", "JPEG", color=(34, 139, 34))
        response = self.client.post(
            '/zucchini/',
            {'image': image},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        result = data['result']
        self.assertIn('class', result)
        self.assertIn('confidence', result)
        self.assertIn('treatment', result)
        self.assertIn('description', result)
        # Verify not placeholder string
        for placeholder in ['1', '4', '5', '7']:
            self.assertNotEqual(result['class'], placeholder)
