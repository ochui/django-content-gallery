import json

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from .. import models

from .models import TestModel, AnotherTestModel, WrongTestModel
from .utils import get_image_in_memory_data

class AjaxRequestMixin:

    def send_ajax_request(self, url):
        return self.client.get(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )


class TestChoices(AjaxRequestMixin, TestCase):

    @staticmethod
    def create_url(pk):
        return reverse('gallery:choices', args=(pk,))

    @classmethod
    def setUpClass(cls):
        cls.obj1 = TestModel.objects.create(name='Test object 1')
        cls.obj2 = TestModel.objects.create(name='Test object 2')
        cls.another_obj = AnotherTestModel.objects.create(
            name='Another object'
        )
        cls.wrong_obj = WrongTestModel.objects.create(name='Wrong object')
        ctype = ContentType.objects.get_for_model(TestModel)
        cls.url = cls.create_url(ctype.pk)

    @classmethod
    def tearDownClass(cls):
        cls.obj1.delete()
        cls.obj2.delete()
        cls.another_obj.delete()
        cls.wrong_obj.delete()

    def test_not_ajax(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_not_existing_content_type(self):
        url = self.create_url(0)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_wrong_content_type(self):
        ctype = ContentType.objects.get_for_model(WrongTestModel)
        url = self.create_url(ctype.pk)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_invisible_content_object(self):
        ctype = ContentType.objects.get_for_model(AnotherTestModel)
        url = self.create_url(ctype.pk)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 403)

    def test_correct_response(self):
        resp = self.send_ajax_request(self.url)
        self.assertEqual(resp.status_code, 200)
        choices = json.loads(resp.content.decode("utf-8"))
        self.assertEqual(len(choices), 2)
        obj1 = {
            'name': self.obj1.name,
            'id': str(self.obj1.pk)
        }
        obj2 = {
            'name': self.obj2.name,
            'id': str(self.obj2.pk)
        }
        self.assertIn(obj1, choices)
        self.assertIn(obj2, choices)


class TestGalleryData(AjaxRequestMixin, TestCase):

    @staticmethod
    def create_url(**kwargs):
        return reverse('gallery:gallery_data', kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        cls.ctype = ContentType.objects.get_for_model(TestModel)
        cls.object = TestModel.objects.create(name="Test object")
        cls.image1 = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=cls.ctype,
            object_id=cls.object.id
        )
        cls.image2 = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=1,
            content_type=cls.ctype,
            object_id=cls.object.id
        )
        cls.another_object = TestModel.objects.create(
            name="Another test object"
        )
        cls.another_image = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=cls.ctype,
            object_id=cls.another_object.id
        )
        cls.url = cls.create_url(
            app_label='tests',
            content_type=cls.ctype.model,
            object_id=cls.object.pk
        )

    @classmethod
    def tearDownClass(cls):
        cls.image1.delete()
        cls.image2.delete()
        cls.object.delete()
        cls.another_image.delete()
        cls.another_object.delete()

    def test_not_ajax(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)
