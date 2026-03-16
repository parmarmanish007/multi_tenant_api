from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CompanySerializer, UserSerializer
from .models import Company
from django.contrib.auth import get_user_model
from common.permissions import IsAdminUserRole
from rest_framework_simplejwt.views import TokenObtainPairView
from .jwt_serializer import CustomTokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
