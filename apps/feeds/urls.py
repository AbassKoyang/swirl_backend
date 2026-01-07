from django.urls import path
from . import views

urlpatterns = [
    path('personalized/', views.PersonalizedFeedView.as_view(), name='personalized-feed'),
    path('trending/', views.TrendingFeedView.as_view(), name='trending-feed'),
    path('recent/', views.RecentFeedView.as_view(), name='recent-feed'),
    path('combined/', views.CombinedFeedView.as_view(), name='combined-feed'),
]

