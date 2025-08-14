from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (AdminListORCreateUserView, AdminChangeUserAPIView, AdminUsersByRoleStatsView,
                    AdminUsersActiveInactiveStatsView, AdminUsersRegisteredStatsView,
                    UserViewSet, UsersMeView)

user_router = DefaultRouter()

user_router.register(r'', UserViewSet, basename='user')

admin_urlpatterns = [
    path('<int:id>/', AdminChangeUserAPIView.as_view(), name='admin_change_user'),
    path('', AdminListORCreateUserView.as_view(), name='admin_create_user'),
    path('active_count/', AdminUsersActiveInactiveStatsView.as_view(), name='admin_count_active'),
    path('registered_count/', AdminUsersRegisteredStatsView.as_view(), name='admin_count_registered'),
    path('roles_count/', AdminUsersByRoleStatsView.as_view(), name='admin_count_roles'),
]

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', include(admin_urlpatterns), name='admin_panel_for_users'),
    path('me/', UsersMeView.as_view(), name='users_me'),
]

urlpatterns += user_router.urls
