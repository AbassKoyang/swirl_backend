from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostSearchView.as_view(), name='search-posts'),
    path('categories/', views.CategorySearchView.as_view(), name='search-categories'),
    path('comments/', views.CommentSearchView.as_view(), name='search-comments'),
    path('bookmarks/', views.BookmarkSearchView.as_view(), name='search-bookmarks'),
]

