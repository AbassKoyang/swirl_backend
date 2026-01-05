from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from .serializers import UserSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.views import APIView
from .permissions import IsProfileOwner

from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

# Create your views here.

class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UpdateUser(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,IsProfileOwner]
    lookup_field = 'pk'
    lookup_url_kwarg='id'

class RetrieveUser(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    lookup_field = 'pk'
    lookup_url_kwarg='id'


class DeleteUser(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,IsProfileOwner]

    lookup_field = 'pk'
    lookup_url_kwarg='id'


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    token = request.data.get("token")
    if not token:
        return Response({"error": "Token not provided","status":False}, status=status.HTTP_400_BAD_REQUEST)
    try:
        id_info = id_token.verify_oauth2_token(
        token, 
        google_requests.Request(), 
        settings.GOOGLE_OAUTH_CLIENT_ID
    )   
        email = id_info['email']
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        profile_pic_url = id_info.get('picture', '')
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.first_name = first_name
            user.last_name = last_name
            user.registration_method = 'google'
            user.profile_pic_url = profile_pic_url
            user.bio = ''
            user.phone_number = ''
            user.address = ''
            user.city = ''
            user.state = ''
            user.country = ''
            user.website = ''
            user.linkedin = ''
            user.instagram = ''
            user.twitter = ''
            user.github = ''
            user.save()
        else:
            if user.registration_method != 'google':
                return Response({
                    "error": "User needs to sign in through email",
                    "status": False
                }, status=status.HTTP_403_FORBIDDEN)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "status": True
            },
            status=status.HTTP_200_OK
        )
    except ValueError:
        return Response({"error": "Invalid token","status":False}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_link = f"http://localhost:5500/reset-password?uid={uid}&token={token}"

            send_mail(
                subject="Password Reset",
                message=f"Reset your password: {reset_link}",
                from_email="no-reply@example.com",
                recipient_list=[email],
            )

        return Response(
            {"message": "If the email exists, a reset link has been sent."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK
        )

