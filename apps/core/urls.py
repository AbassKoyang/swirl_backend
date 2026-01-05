from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/register/', views.RegisterUser.as_view(), name='register'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view()),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmView.as_view()),
    path('auth/google_login/', views.google_login, name='google-login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/<int:id>/', views.RetrieveUser.as_view(), name='retrieve-user'),
    path('users/<int:id>/update/', views.UpdateUser.as_view(), name='update-user'),
    path('users/<int:id>/delete/', views.DeleteUser.as_view(), name='delete-user')
]