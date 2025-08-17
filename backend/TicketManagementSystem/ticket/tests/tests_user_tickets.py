import unittest
from .utils import BaseTest
from rest_framework.reverse import reverse


# @unittest.skip('skip')
class UserTicketTests(BaseTest):

    def setUp(self):
        self.authenticate(self.user_data1)

    def test_user_create_ticket(self):
        ticket_data = {
            "title": "Example Ticket",
            "description": "Some description",
        }

        response = self.client.post(self.user_ticket_url, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Example Ticket")

    def test_user_create_ticket_wrong_title(self):
        ticket_data = {
            "title": "Some title",
            "description": "Some description",
        }

        response = self.client.post(self.user_ticket_url, data=ticket_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_user_create_ticket_without_title(self):
        ticket_data = {
            # "title": "Example title",
            "description": "Some description",
        }

        response = self.client.post(self.user_ticket_url, data=ticket_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_user_create_ticket_without_desc(self):
        ticket_data = {
            "title": "Example title",
            # "description": "Some description",
        }

        response = self.client.post(self.user_ticket_url, data=ticket_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_user_retrieve_ticket(self):
        response = self.client.get(self.user_ticket_url_detail)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.ticket1.id)

    def test_user_retrieve_wrong_ticket(self):
        wrong_url = reverse('ticket-detail', kwargs={'id': 321})
        response = self.client.get(wrong_url)

        self.assertEqual(response.status_code, 404)

    def test_user_retrieve_not_own_ticket(self):
        self.authenticate(self.user_data2)
        wrong_url = reverse('ticket-detail', kwargs={'id': self.ticket1.id})
        response = self.client.get(wrong_url)

        self.assertEqual(response.status_code, 403)

    def test_user_list_tickets(self):
        response = self.client.get(self.user_ticket_url)
        self.assertEqual(response.status_code, 200)

    def test_user_only_own_list_tickets(self):
        self.authenticate(self.user_data2)
        response = self.client.get(self.user_ticket_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_user_ticket_update(self):
        ticket_data = {
            "description": "Some description",
        }

        response = self.client.put(self.user_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["description"], ticket_data["description"])

    def test_user_ticket_partial_update(self):
        ticket_data = {
            "description": "Some description",
        }

        response = self.client.patch(self.user_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["description"], ticket_data["description"])

    def test_user_ticket_update_existing_title(self):
        ticket_data = {
            "title": "Example Ticket",
            "description": "Some description",
        }

        response = self.client.post(self.user_ticket_url, data=ticket_data, format='json')

        ticket_data1 = {
            "title": "Example Ticket",
            "description": "Some description",
        }

        response1 = self.client.put(self.user_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response1.status_code, 400)

    def test_user_ticket_partial_update_existing_title(self):
        ticket_data = {
            "title": "Example Ticket",
            "description": "Some description",
        }

        response = self.client.post(self.user_ticket_url, data=ticket_data, format='json')

        ticket_data1 = {
            "title": "Example Ticket",
            "description": "Some description",
        }
        response1 = self.client.patch(self.user_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response1.status_code, 400)

    def test_user_update_not_own_ticket(self):
        self.authenticate(self.user_data2)
        ticket_data = {
            "description": "Some description",
        }

        response = self.client.put(self.user_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_patch_not_own_ticket(self):
        self.authenticate(self.user_data2)
        ticket_data = {
            "description": "Some description",
        }

        response = self.client.patch(self.user_ticket_url_detail, data=ticket_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_user_delete_ticket(self):
        response = self.client.delete(self.user_ticket_url_detail)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Ticket has been closed")

    def test_user_delete_not_own_ticket(self):
        self.authenticate(self.user_data2)
        response = self.client.delete(self.user_ticket_url_detail)

        self.assertEqual(response.status_code, 403)
