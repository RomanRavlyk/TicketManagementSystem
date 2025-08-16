from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from ticket.views import (UserTicketViewSet, AdminTicketViewSet,
                          SupportTicketViewSet, SupportTicketMarksViewSet)


ticket_router = DefaultRouter()

ticket_router.register(r'user', UserTicketViewSet, basename="ticket")
ticket_router.register(r'admin', AdminTicketViewSet, basename="ticket_admin")
ticket_router.register(r'support', SupportTicketViewSet, basename="ticket_support")

support_router = NestedDefaultRouter(ticket_router, r'support', lookup='ticket')
support_router.register(r'marks', SupportTicketMarksViewSet, basename="marks")

urlpatterns = []

urlpatterns += ticket_router.urls
urlpatterns += support_router.urls
