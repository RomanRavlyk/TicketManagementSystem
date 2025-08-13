from backend.TicketManagementSystem.users.models import CustomUser
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

    title = models.CharField(max_length=30, blank=False)
    description = models.TextField(max_length=250)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tickets_created")
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets_assigned") #SUPPORT
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

