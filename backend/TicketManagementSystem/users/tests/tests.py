import datetime
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from ..models import CustomUser
import unittest
#UserTests

# @unittest.skip('skip')
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
                           response.data)

#ADMIN TESTS
class AdminPanelTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_data = {
            "username": "admin",
            "email": "admin_mail@example.com",
            "password": "Dsdasj2dskl1"
        }

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
        cls.user_id = user.id

        admin = CustomUser.objects.create_superuser(
            username=cls.admin_data["username"],
            email=cls.admin_data["email"],
            password=cls.admin_data["password"]
        )

        cls.admin_id = admin.id

        cls.change_user_url = reverse("admin_change_user", kwargs={"id": cls.user_id})
        cls.create_user_url = reverse("admin_create_user")
        cls.count_active_url = reverse("admin_count_active")
        cls.count_registered_url = reverse("admin_count_registered")
        cls.count_roles_url = reverse("admin_count_roles")


    def setUp(self):
        token_response = self.client.post(reverse('token_obtain_pair'), {
            "username": self.admin_data["username"],
            "password": self.admin_data["password"],
        }, format='json')
        access_token = token_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_super_user_created(self):
        admin_get_url = reverse('admin_change_user', kwargs={'id': self.admin_id})
        response = self.client.get(self.change_user_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.filter(id=self.admin_id).exists())

    def test_admin_create_user(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "user_email@example.com",
            "role": "USER",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
        }

        response = self.client.post(self.create_user_url, user, format='json')
        self.assertEqual(response.status_code, 200)
        created_user = CustomUser.objects.get(id=response.data['id'])

        for field, value in user.items():
            if field == 'password':
                continue

            if hasattr(created_user, field):
                self.assertEqual(getattr(created_user, field), value)

    def test_admin_create_used_username(self):
        user_data = {
            "username": "some_user1",
            "email": "some_example12@mail.com",
            "password": "Dsdasj2dskl1"
        }

        response = self.client.post(self.create_user_url, user_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_create_used_email(self):
        user_data = {
            "username": "some_user12",
            "email": "some_example1@mail.com",
            "password": "Dsdasj2dskl1"
        }

        response = self.client.post(self.create_user_url, user_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_create_user_weak_password(self):
        user = {
            "username": "user",
            "password": "12345678",
            "email": "user_email@example.com",
            "role": "USER",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
        }

        response = self.client.post(self.create_user_url, user, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_create_user_wrong_email(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "some_wrong_email",
            "role": "USER",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
        }

        response = self.client.post(self.create_user_url, user, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_create_super_user(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "user_email@example.com",
            "role": "ADMIN",
            "is_active": True,
        }

        response = self.client.post(self.create_user_url, user, format='json')

        created_user = CustomUser.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(created_user.is_superuser, True),
        self.assertEqual(created_user.is_staff, True),
        self.assertEqual(created_user.role, "ADMIN"),

    def test_admin_create_support_user(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "user_email@example.com",
            "role": "SUPPORT",
            "is_active": True,
        }

        response = self.client.post(self.create_user_url, user, format='json')

        created_user = CustomUser.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(created_user.is_staff, True),
        self.assertEqual(created_user.role, "SUPPORT"),

    def test_admin_get_users_list(self):
        response = self.client.get(self.create_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.all().count(), 2)

    def test_admin_retrieve_user(self):
        response = self.client.get(self.change_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.filter(id=self.admin_id).exists())

    def test_admin_retrieve_unexisting_user(self):
        wrong_url = reverse('admin_change_user', kwargs={'id': 801432042379034219123892317912})

        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_admin_change_user(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "user_email@example.com",
            "role": "ADMIN",
            "is_active": True,
        }

        response = self.client.patch(self.change_user_url, user, format='json')
        self.assertEqual(response.status_code, 200)

        created_user = CustomUser.objects.get(id=self.user_id)

        self.assertEqual(created_user.username, user["username"])

    def test_admin_change_unexisting_user(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "user_email@example.com",
            "role": "ADMIN",
            "is_active": True,
        }

        wrong_url = reverse("admin_change_user", kwargs={"id": 9302341123901239})

        response = self.client.patch(wrong_url, user, format='json')
        self.assertEqual(response.status_code, 404)


    def test_admin_change_user_weak_password(self):
        user = {
            "username": "user",
            "password": "12345678",
            "email": "user_email@example.com",
            "role": "ADMIN",
            "is_active": True,
        }

        response = self.client.patch(self.change_user_url, user, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(['This password is too common.',
                          'This password is entirely numeric.'],
                           response.data)

    def test_admin_change_user_wrong_email(self):
        user = {
            "username": "user",
            "password": "Dsdasj2dskl1",
            "email": "wrong_email",
            "role": "USER",
            "is_active": True,
        }

        response = self.client.patch(self.change_user_url, user, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(["Enter a valid email address."],
                           response.data["email"])

    def test_admin_change_used_email(self):
        user = {
            "username": "some_user1",
            "password": "Dsdasj2dskl1",
            "email": "admin_mail@example.com",
            "role": "USER",
            "is_active": True,
        }

        response = self.client.patch(self.change_user_url, user, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(["This email is already in use."],
                           response.data["email"])

    def test_admin_change_used_username(self):
        user = {
            "username": "admin",
            "password": "Dsdasj2dskl1",
            "email": "user_email@example.com",
            "role": "USER",
            "is_active": True,
        }

        response = self.client.patch(self.change_user_url, user, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(["This username is already in use."],
                           response.data["username"])

    # def test_admin_registered_stats(self):
    #     now = timezone.now()
    #
    #     CustomUser.objects.create_user(username="user1", email="u1@example.com", password="pass",
    #                                    date_joined=now - datetime.timedelta(days=10))
    #
    #     CustomUser.objects.create_user(username="user2", email="u2@example.com", password="Dsdasj2dskl1",
    #                                    date_joined=now - datetime.timedelta(days=5))
    #
    #     CustomUser.objects.create_user(username="user3", email="u3@example.com", password="Dsdasj2dskl1",
    #                                    date_joined=now - datetime.timedelta(days=1))
    #
    #     start_date = (now - datetime.timedelta(days=7)).date().isoformat()
    #     end_date = now.date().isoformat()
    #
    #     data = {
    #         "start_date": start_date,
    #         "end_date": end_date
    #     }
    #     response = self.client.post(self.count_registered_url, data, format='json')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['count'], 2)
    #     self.assertEqual(response.data['start_date'], start_date)
    #     self.assertEqual(response.data['end_date'], end_date)

    # def test_admin_users_by_roles(self):
    #     response = self.client.get(self.count_roles_url)
    #
    #     print("RESPONSE DATA BY ROLES: ", )
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data[0]["count"], 1)
    #     self.assertEqual(response.data[1]["count"], 1)

    def test_admin_delete_user(self):
        response = self.client.delete(self.change_user_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_delete_unexisting_user(self):
        wrong_url = reverse("admin_change_user", kwargs={"id": 901234942302341123901239})

        response = self.client.delete(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_admin_active_inactive_count(self):
        response = self.client.get(self.count_active_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["Active"], 2)
        self.assertEqual(response.data["Inactive"], 0)

