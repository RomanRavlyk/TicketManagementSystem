from rest_framework.routers import DefaultRouter

from ticket.views import UserTicketViewSet

ticket_router = DefaultRouter()
ticket_router.register('', UserTicketViewSet, basename="ticket")
# ticket_router.register('support/', SupportTicketViewSet, basename="ticket")
# ticket_router.register('admin/', AdminTicketViewSet, basename="ticket")

urlpatterns = [

]

urlpatterns += ticket_router.urls