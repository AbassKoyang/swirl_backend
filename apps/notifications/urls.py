from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list-notifications'),
    path('<int:id>/read/', views.MarkNotificationReadView.as_view(), name='mark-notification-read'),
]

