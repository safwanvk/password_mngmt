from django.urls import path

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (PasswordViewSet, OrganizationViewSet, registration,
                    OrganizationJoinMemberAPIView, OrganizationAddPasswordsAPIView,
                    ShareViewSet, get_permissions,
                    SharedPasswordView, UserViewSet, authUser)

router = routers.SimpleRouter()
router.register(r'passwords', PasswordViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'shares', ShareViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('register/', registration, name='user_registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('organizations/<int:organization_id>/join-as-member/', OrganizationJoinMemberAPIView.as_view(), name='join_as_staff'),
    path('organizations/<int:organization_id>/add-passwords/', OrganizationAddPasswordsAPIView.as_view(), name='add_passwords'),
    path('permissions/', get_permissions),
    path('shared_passwords/<int:password_id>/', SharedPasswordView.as_view(), name='shared_passwords'),
    path('users/me/', authUser, name='auth_user'),
]+ router.urls
