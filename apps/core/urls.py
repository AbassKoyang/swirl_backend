from django.urls import path
from . import views
from apps.blogs.views import ListUserBookmarksView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('auth/register/', views.RegisterUser.as_view(), name='register'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view()),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmView.as_view()),
    path('auth/google_login/', views.google_login, name='google-login'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/<int:id>/', views.RetrieveUser.as_view(), name='retrieve-user'),
    path('users/<int:id>/update/', views.UpdateUser.as_view(), name='update-user'),
    path('users/<int:id>/delete/', views.DeleteUser.as_view(), name='delete-user'),
    path('users/<int:id>/bookmarks/', ListUserBookmarksView.as_view(), name='user-bookmarks'),
    path('users/<int:id>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    path('users/<int:id>/followers/', views.ListFollowersView.as_view(), name='list-followers'),
    path('users/<int:id>/following/', views.ListFollowingView.as_view(), name='list-following'),
]