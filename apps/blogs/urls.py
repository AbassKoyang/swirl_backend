from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostsListCreateView.as_view(), name='list-create-post'),
    path('posts/<slug:slug>/', views.PostRetrieveView.as_view(), name='retrieve-post'),
    path('posts/<int:id>/update/', views.PostsUpdateView.as_view(), name='update-post'),
    path('posts/<int:id>/delete/', views.PostDeleteView.as_view(), name='delete-post'),
    path('posts/<int:id>/comments/', views.CommentsListCreateView.as_view(), name='list-create-post-comments'),
    path('posts/<int:id>/reactions/', views.PostReactionListCreateView.as_view(), name='list-create-post-reactions'),
    path('posts/<int:id>/bookmark/', views.BookmarkCreateView.as_view(), name='create-post-bookmark'),
    path('bookmarks/<int:id>/delete/', views.BookmarkDeleteView.as_view(), name='delete-bookmark'),
    path('comments/<int:id>/', views.RetrieveCommentView.as_view(), name='retrieve-comment'),
    path('comments/<int:id>/delete/', views.DeleteCommentView.as_view(), name='delete-comment'),
    path('comments/<int:id>/update/', views.UpdateCommentView.as_view(), name='update-comment'),
    path('comments/<int:id>/replies/', views.RepliesListCreateView.as_view(), name='reply-comment'),
    path('comments/<int:id>/reactions/', views.CommentReactionListCreateView.as_view(), name='list-create-comment-reactions'),
    path('categories/', views.CategoryListCreateView.as_view(), name='list-create-category'),
    path('tags/', views.TagListCreateView.as_view(), name='list-create-tag'),
]
