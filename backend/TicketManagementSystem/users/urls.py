from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (AdminListORCreateUserView, AdminChangeUserAPIView, AdminUsersByRoleStatsView,
                    AdminUsersActiveInactiveStatsView, AdminUsersRegisteredStatsView,
                    UserRegisterView, UserGetMeView, UserUpdateView, UserDeleteView)


user_router = DefaultRouter()

# user_router.register()

users_urlpatterns = [
    path('', UserRegisterView.as_view(), name='register_user'),
    path('me/', UserGetMeView.as_view(), name='get_user_me'),
    path('<int:id>/', UserUpdateView.as_view(), name='change_user'),
    path('me/delete/', UserDeleteView.as_view(), name='delete_user'),
]

admin_urlpatterns = [
    path('users/<int:id>/', AdminChangeUserAPIView.as_view(), name='admin_change_user'),
    path('users/', AdminListORCreateUserView.as_view(), name='admin_create_user'),
    path('users/active_count/', AdminUsersActiveInactiveStatsView.as_view(), name='admin_count_active'),
    path('users/registered_count/', AdminUsersRegisteredStatsView.as_view(), name='admin_count_registered'),
    path('users/roles_count/', AdminUsersByRoleStatsView.as_view(), name='admin_count_roles'),

]

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', include(admin_urlpatterns), name='admin_panel_for_users'),
    path('users/', include(users_urlpatterns), name='users'),
]

urlpatterns += user_router.urls