import unittest

from .utils import BaseTest
from rest_framework.reverse import reverse

from ..models import Ticket, SupportTicketMarks
from users.models import CustomUser


@unittest.skip('skip')
class UserAdminTests(BaseTest):

    def setUp(self):
        self.authenticate(self.user_data3)

    def test_admin_create_ticket(self):
        ticket_data = {
            "title": "Example title",
            "description": "Example description",
            "created_by": self.user1.id,
            "assigned_to": [self.user2.id],
        }

        response = self.client.post(self.admin_ticket_url, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], ticket_data['title'])
        self.assertEqual(response.data['description'], ticket_data['description'])
        self.assertEqual(response.data['created_by']['id'], self.user1.id)
        self.assertIn(self.user2.id, [u['id'] for u in response.data['assigned_to']])

    def test_admin_list_tickets(self):
        response = self.client.get(self.admin_ticket_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_admin_retrieve_ticket(self):
        response = self.client.get(self.admin_ticket_url_detail, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 1)

    def test_admin_retrieve_unexisting_ticket(self):
        response = self.client.get(self.admin_ticket_url_detail, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 1)

    def test_admin_put_ticket(self):
        ticket_data = {
            "title": "Example title",
            "description": "Example description",
            "status": "CLOSED",
            "priority": "LOW",
        }

        response = self.client.put(self.admin_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "CLOSED")
        self.assertEqual(response.data['priority'], "LOW")

    def test_admin_patch_ticket(self):
        ticket_data = {
            "title": "Example title",
            "description": "Example description",
            "status": "CLOSED",
            "priority": "LOW",
        }

        response = self.client.patch(self.admin_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "CLOSED")
        self.assertEqual(response.data['priority'], "LOW")

    def test_admin_put_unexisting_ticket(self):
        ticket_data = {
            "title": "Example title",
            "description": "Example description",
            "status": "CLOSED",
            "priority": "LOW",
        }
        wrong_url = reverse('ticket_admin-detail', kwargs={"id": 32121321})
        response = self.client.put(wrong_url, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_admin_patch_unexisting_ticket(self):
        ticket_data = {
            "title": "Example title",
            "description": "Example description",
            "status": "CLOSED",
            "priority": "LOW",
        }
        wrong_url = reverse('ticket_admin-detail', kwargs={"id": 32121321})
        response = self.client.patch(wrong_url, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_admin_delete_ticket(self):
        response = self.client.delete(self.admin_ticket_url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Ticket has been deleted")

    def test_admin_delete_unexisting_ticket(self):
        wrong_url = reverse('ticket_admin-detail', kwargs={"id": 32121321})
        response = self.client.delete(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_admin_create_mark(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        response = self.client.post(self.admin_ticket_url_marks, data=mark_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data)

    def test_admin_get_marks(self):
        response = self.client.get(self.admin_ticket_url_marks)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_admin_get_mark(self):
        response = self.client.get(self.admin_ticket_url_marks_detail)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_admin_get_unexisting_mark(self):
        wrong_url = reverse('ticket_admin-marks-detail', kwargs={"id": self.ticket1.id, "mark_id": 123})
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_admin_put_marks(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment22"
        }

        response = self.client.put(self.admin_ticket_url_marks_detail, data=mark_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["comment"], "Some comment22")

    def test_admin_patch_marks(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment22"
        }

        response = self.client.patch(self.admin_ticket_url_marks_detail, data=mark_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["comment"], "Some comment22")

    def test_admin_put_unexisting_mark(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment22"
        }
        wrong_url = reverse('ticket_admin-marks-detail', kwargs={"id": self.ticket1.id, "mark_id": 123})
        response = self.client.put(wrong_url, data=mark_data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_admin_patch_unexisting_mark(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment22"
        }
        wrong_url = reverse('ticket_admin-marks-detail', kwargs={"id": self.ticket1.id, "mark_id": 123})
        response = self.client.patch(wrong_url, data=mark_data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_admin_delete_mark(self):
        response = self.client.delete(self.admin_ticket_url_marks_detail)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["message"], "Mark deleted")

    def test_admin_delete_unexisting_mark(self):
        wrong_url = reverse('ticket_admin-marks-detail', kwargs={"id": self.ticket1.id, "mark_id": 123})
        response = self.client.delete(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_user_without_permission_can_use_admin_get_tickets(self):
        self.authenticate(self.user_data1)

        response = self.client.get(self.admin_ticket_url)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_post_tickets(self):
        self.authenticate(self.user_data1)
        some_data = {"support_status": "IN_PROGRESS"}

        response = self.client.post(self.admin_ticket_url, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_put_tickets(self):
        self.authenticate(self.user_data1)
        some_data = {"support_status": "IN_PROGRESS"}

        response = self.client.put(self.admin_ticket_url_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_patch_tickets(self):
        self.authenticate(self.user_data1)
        some_data = {"support_status": "IN_PROGRESS"}

        response = self.client.patch(self.admin_ticket_url_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_delete_tickets(self):
        self.authenticate(self.user_data1)
        response = self.client.delete(self.admin_ticket_url_detail)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_get_ticket_marks(self):
        self.authenticate(self.user_data1)
        response = self.client.get(self.admin_ticket_url_marks)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_post_ticket_marks(self):
        self.authenticate(self.user_data1)

        some_data = {"support_status": "IN_PROGRESS"}
        response = self.client.post(self.admin_ticket_url_marks, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_put_ticket_marks(self):
        self.authenticate(self.user_data1)

        some_data = {"support_status": "IN_PROGRESS"}
        response = self.client.put(self.admin_ticket_url_marks_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_patch_ticket_marks(self):
        self.authenticate(self.user_data1)

        some_data = {"support_status": "IN_PROGRESS"}
        response = self.client.patch(self.admin_ticket_url_marks_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_admin_delete_ticket_marks(self):
        self.authenticate(self.user_data1)
        response = self.client.delete(self.admin_ticket_url_marks_detail)
        self.assertEqual(response.status_code, 403)
