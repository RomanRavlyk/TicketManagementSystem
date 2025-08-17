from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from ticket.models import SupportTicketMarks, Ticket
from users.models import CustomUser


class BaseTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_data1 = {
            "username": "some_user1",
            "email": "some_example1@mail.com",
            "password": "Dsdasj2dskl1",
            "role": "USER"
        }

        cls.user_data2 = {
            "username": "some_user2",
            "email": "some_example2@mail.com",
            "password": "Dsdasj2dskl1",
            "role": "SUPPORT"
        }

        cls.user_data3 = {
            "username": "admin",
            "email": "admin@mail.com",
            "password": "Dsdasj2dskl1",
            "role": "ADMIN"
        }



        user1 = CustomUser.objects.create_user(
            username=cls.user_data1["username"],
            email=cls.user_data1["email"],
            password=cls.user_data1["password"],
            role=cls.user_data1["role"]
        )

        user2 = CustomUser.objects.create_user(
            username=cls.user_data2["username"],
            email=cls.user_data2["email"],
            password=cls.user_data2["password"],
            role=cls.user_data2["role"]
        )

        user3 = CustomUser.objects.create_user(
            username=cls.user_data3["username"],
            email=cls.user_data3["email"],
            password=cls.user_data3["password"],
            role=cls.user_data3["role"]
        )



        cls.user1 = user1
        cls.user2 = user2
        cls.user3 = user3

        cls.ticket_data1 = {
            "title": "Some title",
            "description": "Some description",
            "status": "OPEN",
            "priority": "MEDIUM",
            "created_by": cls.user1,
            "completed_by": cls.user2,
        }

        ticket1 = Ticket.objects.create(
            title=cls.ticket_data1["title"],
            description=cls.ticket_data1["description"],
            status=cls.ticket_data1["status"],
            priority=cls.ticket_data1["priority"],
            created_by=user1,
            completed_by=cls.user2,
        )

        ticket1.assigned_to.add(user2)

        cls.ticket_data2 = {
            "title": "Some title1",
            "description": "Some description",
            "status": "OPEN",
            "priority": "MEDIUM",
            "created_by": cls.user1,
            "completed_by": cls.user2,
        }

        ticket2 = Ticket.objects.create(
            title=cls.ticket_data2["title"],
            description=cls.ticket_data2["description"],
            status=cls.ticket_data2["status"],
            priority=cls.ticket_data2["priority"],
            created_by=user1,
            completed_by=cls.user2,
        )

        ticket2.assigned_to.add(user3)
        cls.ticket1 = ticket1
        cls.ticket2 = ticket2

        cls.mark_data1 = {
            "ticket": ticket1,
            "support_user": cls.user2,
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        mark1 = SupportTicketMarks.objects.create(
            ticket=cls.mark_data1["ticket"],
            support_user=cls.mark_data1["support_user"],
            support_status=cls.mark_data1["support_status"],
            comment=cls.mark_data1["comment"]
        )

        cls.mark_data2 = {
            "ticket": ticket2,
            "support_user": cls.user3,
            "support_status": "IN_PROGRESS",
            "comment": "Some comment"
        }

        mark2 = SupportTicketMarks.objects.create(
            ticket=cls.mark_data2["ticket"],
            support_user=cls.mark_data2["support_user"],
            support_status=cls.mark_data2["support_status"],
            comment=cls.mark_data2["comment"]
        )

        cls.mark1 = mark1
        cls.mark2 = mark2

        cls.user_ticket_url = reverse("ticket-list")
        cls.support_ticket_url = reverse("ticket_support-list")
        cls.support_ticket_marks_url = reverse("marks-list", kwargs={"ticket_id": cls.ticket1.id})
        cls.admin_ticket_url = reverse("ticket_admin-list")

        cls.user_ticket_url_detail = reverse("ticket-detail", kwargs={"id": cls.ticket1.id})
        cls.support_ticket_url_detail = reverse("ticket_support-detail", kwargs={"id": cls.ticket1.id})
        cls.support_ticket_marks_url_detail = reverse("marks-detail",
                                                      kwargs={"ticket_id": cls.ticket1.id, "id": cls.mark1.id})
        cls.admin_ticket_url_detail = reverse("ticket_admin-detail", kwargs={"id": cls.ticket1.id})
        cls.admin_ticket_url_marks = reverse('ticket_admin-marks', kwargs={"id": cls.ticket1.id})
        cls.admin_ticket_url_marks_detail = reverse('ticket_admin-marks-detail',
                                                    kwargs={"id": cls.ticket1.id, "mark_id": cls.mark1.id})

    def authenticate(self, user_data):
        token_response = self.client.post(reverse('token_obtain_pair'), {
            "username": user_data["username"],
            "password": user_data["password"],
        }, format='json')
        access_token = token_response.data.get('access')
        if not access_token:
            raise ValueError(f"Cannot authenticate user {user_data['username']}: {token_response.data}")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    # def setUp(self):
    #     token_response = self.client.post(reverse('token_obtain_pair'), {
    #         "username": self.user_data["username"],
    #         "password": self.user_data["password"],
    #     }, format='json')
    #     access_token = token_response.data.get('access')
    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
