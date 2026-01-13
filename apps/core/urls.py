from django.urls import path
from . import views
from apps.blogs.views import ListUserBookmarksView, ListUserPostsView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('auth/register/', views.RegisterUser.as_view(), name='register'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('auth/google_login/', views.google_login, name='google-login'),

    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/refresh/', views.CookieTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),

    path('users/<int:id>/', views.RetrieveUser.as_view(), name='retrieve-user'),
    path('users/<int:id>/update/', views.UpdateUser.as_view(), name='update-user'),
    path('users/<int:id>/delete/', views.DeleteUser.as_view(), name='delete-user'),
    path('users/<int:id>/bookmarks/', ListUserBookmarksView.as_view(), name='user-bookmarks'),
    path('users/<int:id>/posts/', ListUserPostsView.as_view(), name='user-posts'),
    path('users/<int:id>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    path('users/<int:id>/followers/', views.ListFollowersView.as_view(), name='list-followers'),
    path('users/<int:id>/following/', views.ListFollowingView.as_view(), name='list-following'),
    path("users/<int:id>/is-following/", views.IsFollowingView.as_view(), name='is-following'),
]