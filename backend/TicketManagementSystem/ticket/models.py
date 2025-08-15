from users.models import CustomUser
from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        CLOSED = "CLOSED", "Closed"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=30, blank=False, unique=True)
    description = models.TextField(max_length=250)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tickets_created")

    assigned_to = models.ManyToManyField(CustomUser, blank=True, related_name='assigned_supports')  # SUPPORTS

    completed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="tickets_assigned") # SUPPORT, who completed ticket

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class SupportTicketMarks(models.Model):
    class SUPPORT_STATUS(models.TextChoices):
        NEEDS_CLARIFICATION = 'NEEDS_CLARIFICATION', 'Needs Clarification'
        WAITING_FOR_USER_RESPONSE = 'WAITING_FOR_USER', 'Waiting for User'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="ticket_mark")
    support_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="support_user")
    support_status = models.CharField(max_length=30, choices=SUPPORT_STATUS)
    comment = models.TextField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
