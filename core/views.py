from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import  AllowAny, IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Password, Organization, User
from .serializers import RegisterSerializer, PasswordSerializer, OrganizationSerializer

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# Create your views here.
# User Registration
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes((AllowAny, ))
def registration(request):
    if request.method == "POST":
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            if 'email' in serializer.errors :
                raise APIException('The Email address already exists.' , status.HTTP_400_BAD_REQUEST)
            else:
                raise APIException(serializer.errors , status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'detail':'Registration success.'}, status.HTTP_201_CREATED)

class PasswordViewSet(viewsets.ModelViewSet):
    queryset = Password.objects.all()
    serializer_class = PasswordSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return super().get_queryset().filter(id__in=self.request.user.passwords)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsAuthenticated,)
    
class OrganizationJoinMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_id):
        """ Join as member """
        try:
            if request.data.get('email', None) is None:
                return Response({'message':'email is required'}, status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email = request.data['email'])
            try:
                organization = Organization.objects.get(id=organization_id)
                user.organizations.add(organization)
                user.save()
            except:
                # No Organization found
                return Response({'error': 'No Organization found.'}, status.HTTP_404_NOT_FOUND)
            return Response({'message':'Successfully joined as member.'}, status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message':'User does not exist. Please add as a new member.'}, status.HTTP_404_NOT_FOUND)

class OrganizationAddPasswordsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_id):
        """ Add passwords """
        if request.data.get('passwords', None) is None:
            return Response({'message':'passwords is required'}, status.HTTP_400_BAD_REQUEST)
        passwords = request.data['passwords']
        if len(passwords) == Password.objects.filter(id__in=passwords).count():
            try:
                organization = Organization.objects.get(id=organization_id)
                organization.passwords.add(*passwords)
                organization.save()
            except:
                # No Organization found
                return Response({'error': 'No Organization found.'}, status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':'Passwords does not exist.'}, status.HTTP_404_NOT_FOUND)
        return Response({'message':'Successfully added passwords.'}, status.HTTP_200_OK)