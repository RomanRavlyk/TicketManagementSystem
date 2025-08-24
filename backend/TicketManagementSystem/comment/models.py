from users.models import CustomUser
from django.db import models
from ticket.models import Ticket


class Comment(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    comment_text = models.TextField(max_length=500)
    created_on = models.DateTimeField(auto_now_add=True)