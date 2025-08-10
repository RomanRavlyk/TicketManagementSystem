from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from ..models import CustomUser

#UserTests
class UsersAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "username": "some_user1",
            "email": "some_example1@mail.com",
            "password": "Dsdasj2dskl1"
        }

        user = CustomUser.objects.create_user(
            username=cls.user_data["username"],
            email=cls.user_data["email"],
            password=cls.user_data["password"]
        )
        cls.id = user.id

        cls.list_url = reverse('user-list')
        cls.detail_url = reverse('user-detail', kwargs={'id': cls.id})

    def setUp(self):
        token_response = self.client.post(reverse('token_obtain_pair'), {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }, format='json')
        access_token = token_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_registration(self):
        data = {
            "username": "some_user2",
            "email": "some_example2@mail.com",
            "password": "Dsdasj2dskl1"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_token(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get('access'))

    def test_user_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_user_update(self):
        update_data = {
            "username": "some_user2",
            "email": "some_example2@mail.com",
            "password": "Dsdasj2dskl1"
        }
        response = self.client.put(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], update_data['username'])

    def test_user_delete(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_weak_password_register(self):
        data = {
            "username": "some_user2",
            "email": "some_example2@mail.com",
            "password": "12345678"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_weak_password_update(self):
        update_data = {
            "username": "some_user2",
            "email": "some_example3@mail.com",
            "password": "12345678"
        }
        response = self.client.put(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_delete_unexisting_user(self):
        wrong_url = reverse('user-detail', kwargs={'id': 200})
        response = self.client.delete(wrong_url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_user_retrieve(self):
        other_user = CustomUser.objects.create_user(
            username="some_user2",
            email="some_example2@mail.com",
            password="Dsdasj2dskl1"
        )


        url = reverse('user-detail', kwargs={'id': other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_destroy(self):
        other_user = CustomUser.objects.create_user(
            username="some_user2",
            email="some_example2@mail.com",
            password="Dsdasj2dskl1"
        )
        url = reverse('user-detail', kwargs={'id': other_user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_create_duplicate_username(self):
        user_data = {
            "username": "some_user1",
            "email": "some_example2@mail.com",
            "password": "Dsdasj2dskl1"
        }

        response = self.client.post(self.list_url, user_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_email(self):
        user_data = {
            "username": "some_user2",
            "email": "some_example1@mail.com",
            "password": "Dsdasj2dskl1"
        }

        response = self.client.post(self.list_url, user_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_wrong_email(self):
        user_data = {
            "username": "some_user2",
            "email": "incorrect_email",
            "password": "Dsdasj2dskl1"
        }

        response = self.client.post(self.list_url, user_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_user_deleted_after_remove(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(id=self.id).exists())

    def test_user_cant_change_id(self):
        user_data = {
            "id": 293102,
            "username": "some_user2",
            "email": "some_example1@mail.com",
            "password": "Dsdasj2dskl1"
        }

        response = self.client.put(self.detail_url, user_data, format='json')
        self.assertNotEqual(response.data['id'], 293102)

    def test_password_message(self):
        update_data = {
            "username": "some_user2",
            "email": "some_example3@mail.com",
            "password": "12345678"
        }
        response = self.client.post(self.list_url, update_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(['This password is too common.',
                          'This password is entirely numeric.'],
                           response.data["password_errors"])