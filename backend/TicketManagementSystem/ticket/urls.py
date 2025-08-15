from rest_framework.routers import DefaultRouter

from ticket.views import (UserTicketViewSet, AdminTicketViewSet,
                          SupportTicketViewSet, SupportTicketMarksViewSet)

ticket_router = DefaultRouter()
ticket_router.register('user', UserTicketViewSet, basename="ticket")
ticket_router.register('support', SupportTicketViewSet, basename="ticket_support")
ticket_router.register('support/marks/', SupportTicketMarksViewSet, basename="ticket_support_marks")
ticket_router.register('admin', AdminTicketViewSet, basename="ticket_admin")

urlpatterns = [

]

urlpatterns += ticket_router.urls
