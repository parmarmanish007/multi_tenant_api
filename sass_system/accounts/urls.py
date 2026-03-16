from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, UserViewSet

router = DefaultRouter()
router.register("company", CompanyViewSet, basename='company')
router.register("users", UserViewSet, basename='users')

urlpatterns = router.urls