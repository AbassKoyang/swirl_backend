from django.conf import settings
from django.db.models import F
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .models import User, Follow
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .permissions import IsProfileOwner
from .throttles import AuthRateThrottle, AuthAnonRateThrottle, UserActionRateThrottle, ReadOnlyRateThrottle
from apps.notifications.utils import create_notification
from apps.notifications.models import Notification


from .serializers import (
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    FollowSerializer
)

# Create your views here.

class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonRateThrottle]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response({
            "status": True,
            "user": UserSerializer(user).data
        })

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24,
            path='/'
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24,
            path='/'
        )
        return response
    
    def perform_create(self, serializer):
        user = serializer.save()
        try:
            Notification.objects.create(
                user=user,
                actor=user,
                action_type='sign_up',
                content_type=None,
                object_id=None
            )
        except Exception:
            pass 

class ListUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReadOnlyRateThrottle]

    def get_queryset(self):
        return User.objects.all()

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
    throttle_classes = [ReadOnlyRateThrottle]

    lookup_field = 'pk'
    lookup_url_kwarg='id'


class DeleteUser(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,IsProfileOwner]

    lookup_field = 'pk'
    lookup_url_kwarg='id'

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    # Throttling handled by AuthAnonRateThrottle in CustomTokenObtainPairView
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
            try:
                from apps.notifications.models import Notification
                Notification.objects.create(
                    user=user,
                    actor=user,
                    action_type='sign',
                    content_type=None,
                    object_id=None
                )
            except Exception:
                pass 
        else:
            if user.registration_method != 'google':
                return Response({
                    "error": "User needs to sign in through email",
                    "status": False
                }, status=status.HTTP_403_FORBIDDEN)
      
        refresh = RefreshToken.for_user(user)

        response = Response({
            "status": True,
            "message": "Google login successful"
        })

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 30,
            path='/'
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=(60 * 60 * 24) * 7,
            path='/'
        )

        return response
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

            reset_link = f"https://inspirely.vercel.app/reset-password?uid={uid}&token={token}"
            print(reset_link)

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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({
            "status": True,
            "message": "Logged out successfully"
        })
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


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


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes =[AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data["access"]
            refresh = response.data["refresh"]

            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=False, 
                samesite="Lax",
                max_age=60 * 30,
                path='/'
            )

            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=(60 * 60 * 24) * 7,
                path='/'
            )
            response.data = {
                "status": True,
                "message": "Login successful"
            }

        
        if response.status_code == 200:
            email = request.data.get('email')
            if email:
                try:
                    user = User.objects.get(email=email)
                    has_notifications = Notification.objects.filter(user=user).exists()
                    if not has_notifications:
                        create_notification(
                            user=user,
                            actor=user,
                            action_type='sign_up',
                            target_object=None
                        )
                    else:
                        create_notification(
                            user=user,
                            actor=user,
                            action_type='log_in',
                            target_object=None
                        )

                except (User.DoesNotExist, Exception):
                    pass
        
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"detail": "No refresh token"}, status=401)

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            response.set_cookie(
                key="access_token",
                value=response.data["access"],
                httponly=True,
                secure=False, 
                samesite="Lax",
                max_age=60 * 30,
                path='/'
            )

            response.set_cookie(
                key="refresh_token",
                value=response.data["refresh"],
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=(60 * 60 * 24) * 7,
                path='/'
            )
            response.data = {
                "status": True,
                "message": "Token refreshed"
            }

        return response

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserActionRateThrottle]

    def post(self, request, **kwargs):
        user_id = self.kwargs['id']
        user_to_follow = get_object_or_404(User, pk=user_id)
        
        if user_to_follow == request.user:
            return Response(
                {"error": "You cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            return Response(
                {"message": "You are already following this user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        User.objects.filter(
                pk=user_id).update(
                followers_count=F("followers_count") + 1
        )
        User.objects.filter(
                pk=request.user.id,
                ).update(following_count=F("following_count") + 1)

        create_notification(
            user=user_to_follow,
            actor=request.user,
            action_type='follow',
            target_object=user_to_follow
        )
        
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        user_id = self.kwargs['id']
        user_to_unfollow = get_object_or_404(User, pk=user_id)
        
        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow.delete()
            User.objects.filter(
            pk=user_id).update(
            followers_count=F("followers_count") - 1
            )
            User.objects.filter(
            pk=request.user.id,
            following_count__gt=0
            ).update(following_count=F("following_count") - 1)

            return Response(
                {"message": "Successfully unfollowed user"},
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {"error": "You are not following this user"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ListFollowersView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReadOnlyRateThrottle]

    def get_queryset(self):
        user_id = self.kwargs['id']
        user = get_object_or_404(User, pk=user_id)
        return Follow.objects.filter(following=user).select_related('follower', 'following')


class ListFollowingView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReadOnlyRateThrottle]

    def get_queryset(self):
        user_id = self.kwargs['id']
        user = get_object_or_404(User, pk=user_id)
        return Follow.objects.filter(follower=user).select_related('follower', 'following')

class IsFollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        user_id = self.kwargs['id']
        target_user = get_object_or_404(User, pk=user_id)

        is_following = Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).exists()

        return Response(
            {
                "is_following": is_following
            },
            status=status.HTTP_200_OK
        )


