from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import UserViewSet


user_router = DefaultRouter()

user_router.register(r"users", UserViewSet, basename="token")

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
urlpatterns += user_router.urls