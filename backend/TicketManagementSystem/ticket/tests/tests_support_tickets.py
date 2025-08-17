from .utils import BaseTest
from rest_framework.reverse import reverse
import unittest
from ..models import Ticket
from users.models import CustomUser


# @unittest.skip('skip')
class UserSupportTests(BaseTest):

    def setUp(self):
        self.authenticate(self.user_data2)

    def test_support_cant_create_ticket(self):
        response = self.client.post(self.support_ticket_url)

        self.assertEqual(response.status_code, 405)

    def test_support_tickets_list(self):
        response = self.client.get(self.support_ticket_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['id'], self.ticket1.id)

    def test_support_cant_see_unowned_tickets_in_list(self):
        response = self.client.get(self.support_ticket_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_support_retrieve(self):
        response = self.client.get(self.support_ticket_url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.ticket1.id)

    def test_support_cant_retrieve_unexisting_tickets(self):
        wrong_url = reverse('ticket_support-detail', kwargs={'id': 312})
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_support_cant_retrieve_unowned_tickets(self):
        wrong_url = reverse('ticket_support-detail', kwargs={'id': self.ticket2.id})

        response = self.client.get(wrong_url)

        self.assertEqual(response.status_code, 403)

    def test_support_put(self):
        ticket_data = {
            'status': "CLOSED",
        }

        response = self.client.put(self.support_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "CLOSED")

    def test_support_cant_patch(self):
        response = self.client.patch(self.support_ticket_url_detail)
        self.assertEqual(response.status_code, 405)

    def test_support_cant_put_unexisting_tickets(self):
        ticket_data = {
            'status': "CLOSED",
        }
        wrong_url = reverse('ticket_support-detail', kwargs={'id': 312})

        response = self.client.put(wrong_url, data=ticket_data, format='json')

        self.assertEqual(response.status_code, 404)

    def test_support_cant_put_unowned_tickets(self):
        ticket_data = {
            'status': "CLOSED",
        }
        wrong_url = reverse('ticket_support-detail', kwargs={'id': self.ticket2.id})

        response = self.client.put(wrong_url, data=ticket_data, format='json')

        self.assertEqual(response.status_code, 403)

    def test_support_destroy(self):
        response = self.client.delete(self.support_ticket_url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Ticket has been closed', response.data['message'])

    def test_support_cant_destroy_unexisting_tickets(self):
        wrong_url = reverse('ticket_support-detail', kwargs={'id': 312})
        response1 = self.client.delete(wrong_url)
        self.assertEqual(response1.status_code, 404)

    def test_support_cant_destroy_unowned_tickets(self):
        wrong_url = reverse('ticket_support-detail', kwargs={'id': self.ticket2.id})
        response1 = self.client.delete(wrong_url)
        self.assertEqual(response1.status_code, 403)

    def test_support_create_mark(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        response = self.client.post(self.support_ticket_marks_url, data=mark_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_support_cant_create_marks_unowned_tickets(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        wrong_url = reverse('marks-list', kwargs={'ticket_id': self.ticket2.id})

        response = self.client.post(wrong_url, data=mark_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_support_can_list_all_marks(self):
        response1 = self.client.get(self.support_ticket_marks_url)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data["count"], 2)

    def test_support_can_retrieve_unowned_marks(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': self.mark2.id})
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data["id"], self.mark2.id)

    def test_support_cant_retrieve_unexisting_marks(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': 123})
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 404)

    def test_support_put_marks(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        response = self.client.put(self.support_ticket_marks_url_detail, data=mark_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_support_patch_marks(self):
        mark_data = {
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        response = self.client.patch(self.support_ticket_marks_url_detail, data=mark_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_support_cant_put_unowned_marks(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': self.mark2.id})

        response = self.client.put(url)
        self.assertEqual(response.status_code, 403)

    def test_support_cant_patch_unowned_marks(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': self.mark2.id})

        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_support_cant_put_unexisting_marks(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': 312})

        response = self.client.put(url)
        self.assertEqual(response.status_code, 404)

    def test_support_cant_patch_unexisting_marks(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': 321})

        response = self.client.patch(url)
        self.assertEqual(response.status_code, 404)

    def test_support_delete_mark(self):
        response = self.client.delete(self.support_ticket_marks_url_detail)
        self.assertEqual(response.status_code, 200)

    def test_support_delete_unexisting_mark(self):
        wrong_url = reverse("marks-detail", kwargs={"ticket_id": self.ticket1.id, "id": 321})
        response = self.client.delete(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_support_cant_delete_unowned_mark(self):
        url = reverse('marks-detail', kwargs={'ticket_id': self.mark2.ticket.id, 'id': self.mark2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_get_tickets(self):
        self.authenticate(self.user_data1)

        response = self.client.get(self.support_ticket_url)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_put_tickets(self):
        self.authenticate(self.user_data1)
        some_data = {"support_status": "IN_PROGRESS"}

        response = self.client.put(self.support_ticket_url_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_patch_tickets(self):
        self.authenticate(self.user_data1)
        some_data = {"support_status": "IN_PROGRESS"}

        response = self.client.patch(self.support_ticket_url_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_delete_tickets(self):
        self.authenticate(self.user_data1)
        response = self.client.delete(self.support_ticket_url_detail)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_get_ticket_marks(self):
        self.authenticate(self.user_data1)
        response = self.client.get(self.support_ticket_marks_url)
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_post_ticket_marks(self):
        self.authenticate(self.user_data1)

        some_data = {"support_status": "IN_PROGRESS"}
        response = self.client.post(self.support_ticket_marks_url, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_put_ticket_marks(self):
        self.authenticate(self.user_data1)

        some_data = {"support_status": "IN_PROGRESS"}
        response = self.client.put(self.support_ticket_marks_url_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_patch_ticket_marks(self):
        self.authenticate(self.user_data1)

        some_data = {"support_status": "IN_PROGRESS"}
        response = self.client.patch(self.support_ticket_marks_url_detail, data=some_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_can_use_support_delete_ticket_marks(self):
        self.authenticate(self.user_data1)
        response = self.client.delete(self.support_ticket_marks_url_detail)
        self.assertEqual(response.status_code, 403)

    def test_support_take_ticket(self):
        response = self.client.post(self.support_take_url)
        self.assertEqual(response.status_code, 200)

    def test_support_assign_unexisting_ticket(self):
        wrong_url = reverse("ticket_support-take", kwargs={"id": 321})
        response = self.client.post(wrong_url)
        self.assertEqual(response.status_code, 404)

    def test_support_release_ticket(self):
        response = self.client.post(self.support_take_url)
        response = self.client.post(self.support_release_url)
        self.assertEqual(response.status_code, 200)

    def test_support_release_unexisting_ticket(self):
        wrong_url = reverse("ticket_support-release", kwargs={"id": 321})
        response = self.client.post(wrong_url)
        self.assertEqual(response.status_code, 404)