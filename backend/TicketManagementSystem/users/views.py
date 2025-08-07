from .models import CustomUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer