from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserViewSet, AdminUserListORCreateView, AdminUserUpdateAPIView


user_router = DefaultRouter()

user_router.register(r"users", UserViewSet, basename="users")

admin_urlpatterns = [
    path('users/<int:id>/', AdminUserUpdateAPIView.as_view(), name='admin_change_user'),
    path('users/', AdminUserListORCreateView.as_view(), name='admin_create_user'),
    # path('users/active_count/', .as_view(), name='admin_count_active'),

]

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', include(admin_urlpatterns), name='admin_pane_for_users'),
]

urlpatterns += user_router.urls