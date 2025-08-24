from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from comment.views import CommentViewSet, AdminCommentViewSet
from ticket.views import (UserTicketViewSet, AdminTicketViewSet,
                          SupportTicketViewSet, SupportTicketMarksViewSet)


ticket_router = DefaultRouter()

ticket_router.register(r'user', UserTicketViewSet, basename="ticket")
ticket_router.register(r'admin', AdminTicketViewSet, basename="ticket_admin")
ticket_router.register(r'support', SupportTicketViewSet, basename="ticket_support")

nested_comment_user_router = NestedDefaultRouter(ticket_router, r'user', lookup='ticket')
nested_comment_user_router.register(r'comments', CommentViewSet, basename="user_comments")

nested_comment_admin_router = NestedDefaultRouter(ticket_router, r'admin', lookup='ticket')
nested_comment_admin_router.register(r'comments', AdminCommentViewSet, basename="admin_comments")

support_router = NestedDefaultRouter(ticket_router, r'support', lookup='ticket')
support_router.register(r'marks', SupportTicketMarksViewSet, basename="marks")

urlpatterns = []

urlpatterns += ticket_router.urls
urlpatterns += support_router.urls
urlpatterns += nested_comment_user_router.urls
urlpatterns += nested_comment_admin_router.urls
