from django.urls import path
from .views import registration
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (PasswordViewSet, OrganizationViewSet,
                    OrganizationJoinMemberAPIView)

router = routers.SimpleRouter()
router.register(r'passwords', PasswordViewSet)
router.register(r'organizations', OrganizationViewSet)

urlpatterns = [
    path('register/', registration, name='user_registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('organizations/<int:organization_id>/join-as-member/', OrganizationJoinMemberAPIView.as_view(), name='join_as_staff'),
]+ router.urls
