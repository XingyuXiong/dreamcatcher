from django.test import TestCase, Client, override_settings
from .models import Angel
import json
from PIL import Image
from io import BytesIO


class TestAngel(TestCase):
    def setUp(self):
        a = Angel(
            registered_name="Correctizer",
            registered_id="12345",
            nickname="Cowsay",
            identifier="XJTU-abcdef",
        )
        a.save()
        self.angel = a

    def tearDown(self):
        self.angel.delete()

    def test_not_logged_in(self):
        c = Client()
        resp = c.get('/angel/login', {
            'data': json.dumps({'back': '/some/path'})
        }).json()
        self.assertTrue(resp['success'])
        self.assertFalse(resp['data']['logged_in'])

    def test_logged_in(self):
        c = Client()
        session = c.session
        session['angel_id'] = self.angel.id
        session.save()
        resp = c.get('/angel/login', {
            'data': json.dumps({'back': '/some/path'})
        }).json()
        self.assertTrue(resp['success'])
        self.assertTrue(resp['data']['logged_in'])
        angel = resp['data']['angel']
        self.assertEqual(angel['id'], self.angel.id)
        self.assertEqual(angel['nickname'], self.angel.nickname)

    def test_no_back(self):
        c = Client()
        resp = c.get('/angel/login').json()
        self.assertFalse(resp['success'])

    def test_login_required(self):
        c = Client()
        resp = c.post('/angel/edit', {'nickname': 'Cowsay'}).json()
        self.assertFalse(resp['success'])


class TestAngel2(TestCase):
    def setUp(self):
        a = Angel(
            registered_name="Correctizer",
            registered_id="12345",
            nickname="Cowsay",
            identifier="XJTU-abcdef",
        )
        a.save()
        self.angel = a
        c = Client()
        session = c.session
        session['angel_id'] = a.id
        session.save()
        self.client = c

    def tearDown(self):
        self.angel.delete()

    def test_update(self):
        resp = self.client.post('/angel/edit', {'nickname': 'Catsay'}).json()
        self.assertTrue(resp['success'])
        angel = Angel.objects.get(id=self.angel.id)
        self.assertEqual(angel.nickname, 'Catsay')

    def test_update_no_field(self):
        resp = self.client.post('/angel/edit').json()
        self.assertFalse(resp['success'])

    def test_update_avatar(self):
        avatar_image = Image.new('RGB', (640, 640))
        avatar_file = BytesIO()
        avatar_image.save(avatar_file, 'JPEG')
        upload_file = BytesIO(avatar_file.getbuffer())
        avatar_file.close()
        resp = self.client.post('/angel/edit', {'avatar': upload_file}).json()
        upload_file.close()
        self.assertTrue(resp['success'])

        angel = Angel.objects.get(id=self.angel.id)
        self.assertEqual(angel.avatar.url, resp['data']['avatar'])
