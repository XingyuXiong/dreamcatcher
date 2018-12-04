from django.test import TestCase, Client
from .models import Angel, Group
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
            'data': json.dumps({
                'back': '/some/path'
            })
        }).json()
        self.assertTrue(resp['success'])
        self.assertFalse(resp['data']['logged_in'])

    def test_logged_in(self):
        c = Client()
        session = c.session
        session['angel_id'] = self.angel.id
        session.save()
        resp = c.get('/angel/login', {
            'data': json.dumps({
                'back': '/some/path'
            })
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
        resp = c.post(
            '/angel/edit',
            json.dumps({
                'nickname': 'Cowsay'
            }),
            content_type='application/json',
        ).json()
        self.assertFalse(resp['success'])


class TestCaseWithAngel(TestCase):
    def setUp(self):
        super().setUp()
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
        super().tearDown()


class TestAngel2(TestCaseWithAngel):
    def test_logout(self):
        resp = self.client.post('/angel/logout').json()
        self.assertTrue(resp['success'])

    def test_get_angel(self):
        resp = self.client.get(
            '/angel',
            {
                'data': json.dumps({
                    'id_list': [self.angel.id]
                }),
            },
            follow=True,
        ).json()
        self.assertTrue(resp['success'])
        self.assertEqual(resp['data'][0]['nickname'], self.angel.nickname)

        resp = self.client.get(
            '/angel',
            {
                'data': json.dumps({
                    'id_list': [4294967295]
                })
            },
            follow=True,
        ).json()
        self.assertTrue(resp['success'])
        self.assertEqual(resp['data'], [])

    def test_update(self):
        resp = self.client.post(
            '/angel/edit',
            json.dumps({
                'nickname': 'Catsay'
            }),
            content_type='application/json').json()
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


class TestAvatar(TestCaseWithAngel):
    def test_avatar_too_small(self):
        avatar_image = Image.new('RGB', (127, 640))
        avatar_file = BytesIO()
        avatar_image.save(avatar_file, 'JPEG')
        upload_file = BytesIO(avatar_file.getbuffer())
        avatar_file.close()
        resp = self.client.post('/angel/edit', {'avatar': upload_file}).json()
        upload_file.close()
        self.assertFalse(resp['success'])

    def test_file_too_large(self):
        avatar_image = Image.new('RGB', (16000, 6400))
        avatar_file = BytesIO()
        avatar_image.save(avatar_file, 'JPEG')
        upload_file = BytesIO(avatar_file.getbuffer())
        avatar_file.close()
        resp = self.client.post('/angel/edit', {'avatar': upload_file}).json()
        upload_file.close()
        self.assertFalse(resp['success'])


class TestGroup(TestCaseWithAngel):
    def setUp(self):
        super().setUp()
        group = Group(leader=self.angel)
        group.save()
        self.group = group
        self.angel.group = group
        self.angel.save()

    def tearDown(self):
        self.group.delete()
        super().tearDown()

    def test_edit_group(self):
        resp = self.client.post(
            f'/angel/group/{self.group.id}/edit',
            json.dumps({
                'name': 'Test Group'
            }),
            content_type='application/json').json()
        self.assertTrue(resp['success'])
        self.assertEqual(resp['data']['name'],
                         Group.objects.get(id=self.group.id).name)

        resp = self.client.post(
            f'/angel/group/{self.group.id}/edit',
            json.dumps({
                'description': 'The description for Test Group.'
            }),
            content_type='application/json').json()
        self.assertTrue(resp['success'])

        resp = self.client.get(
            '/angel/group',
            {
                'data': json.dumps({
                    'id_list': [self.group.id]
                })
            },
            follow=True,
        ).json()
        self.assertTrue(resp['success'])
        self.assertEqual(resp['data'][0]['description'],
                         Group.objects.get(id=self.group.id).description)

        resp = self.client.post(
            f'/angel/group/{self.group.id}/edit',
            json.dumps({
                'deleted_angels': [self.angel.id],
            }),
            content_type='application/json').json()
        self.assertFalse(resp['success'])

        new_leader = Angel(
            registered_name="Someone",
            registered_id="12346",
            nickname="Catsay",
            identifier="XJTU-abcdeg",
        )
        new_leader.save()
        group = Group.objects.get(id=self.group.id)
        group.leader = new_leader
        group.save()
        new_leader.group = group
        new_leader.save()

        session = self.client.session
        session['angel_id'] = new_leader.id
        session.save()

        resp = self.client.post(
            f'/angel/group/{self.group.id}/edit',
            json.dumps({
                'deleted_angels': [self.angel.id],
            }),
            content_type='application/json').json()
        self.assertTrue(resp['success'])
        self.assertIsNone(Angel.objects.get(id=self.angel.id).group)
