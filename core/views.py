from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import  AllowAny
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response
from .serializers import RegisterSerializer

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
                raise APIException('The Email address already exists. Return to Sign In' , status.HTTP_400_BAD_REQUEST)
            else:
                raise APIException(serializer.errors , status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'detail':'Registration success.'}, status.HTTP_201_CREATED)
