from rest_framework import generics, filters, permissions
from django.db.models import Q

from apps.blogs.models import Post, Comment, Bookmark, Category
from apps.blogs.serializers import PostSerializer, CommentSerializer, BookmarkSerializer
from .throttles import SearchRateThrottle, SearchAnonRateThrottle


class PostSearchView(generics.ListAPIView):
    """
    Search endpoint for posts with advanced filtering options.
    
    Query parameters:
    - q: Search query (searches in title, content, author name, category name, tags)
    - status: Filter by status (draft/published)
    - category: Filter by category ID or slug
    - author: Filter by author ID
    - tags: Filter by tag names (comma-separated)
    - ordering: Order results (e.g., '-created_at', 'title', '-reaction_count')
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    def get_throttles(self):
        if self.request.user.is_authenticated:
            return [SearchRateThrottle()]
        return [SearchAnonRateThrottle()]
    search_fields = ['title', 'content', 'author__email', 'author__first_name', 'author__last_name', 
                     'category__name', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'title', 'reaction_count', 'comment_count', 'bookmark_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Post.objects.active().select_related('author', 'category').prefetch_related('tags')
        
        search_query = self.request.query_params.get('q', None)
        status = self.request.query_params.get('status', None)
        category = self.request.query_params.get('category', None)
        author_id = self.request.query_params.get('author', None)
        tags = self.request.query_params.get('tags', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query) |
                Q(author__email__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        if status:
            queryset = queryset.filter(status=status)
        
        if category:
            try:
                category_id = int(category)
                category = generics.get_object_or_404(Category, pk=category_id)
                queryset = queryset.filter(category=category)
            except ValueError:
                pass        
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__name__in=tag_list).distinct()
        
        return queryset


class CommentSearchView(generics.ListAPIView):
    """
    Search endpoint for comments with advanced filtering options.
    
    Query parameters:
    - q: Search query (searches in comment content, user name, post title)
    - post: Filter by post ID
    - user: Filter by user ID
    - parent: Filter by parent comment ID (to get replies only)
    - ordering: Order results (e.g., '-created_at', 'created_at')
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    def get_throttles(self):
        if self.request.user.is_authenticated:
            return [SearchRateThrottle()]
        return [SearchAnonRateThrottle()]
    search_fields = ['content', 'user__email', 'user__first_name', 'user__last_name', 'post__title']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Comment.objects.all().select_related('user', 'post', 'parent')
        
        search_query = self.request.query_params.get('q', None)
        post_id = self.request.query_params.get('post', None)
        user_id = self.request.query_params.get('user', None)
        parent_id = self.request.query_params.get('parent', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(content__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(post__title__icontains=search_query)
            ).distinct()
        
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        else:
            pass
        
        return queryset


class BookmarkSearchView(generics.ListAPIView):
    """
    Search endpoint for user bookmarks with advanced filtering options.
    
    Query parameters:
    - q: Search query (searches in post title, post content, post author name)
    - user: Filter by user ID (defaults to authenticated user if not provided)
    - ordering: Order results (e.g., '-created_at', 'created_at')
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SearchRateThrottle]

    def get_queryset(self):
        queryset = Bookmark.objects.filter(user=self.request.user)
        
        queryset = queryset.select_related('user', 'post', 'post__author', 'post__category').prefetch_related('post__tags')
        
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(post__title__icontains=search_query) |
                Q(post__content__icontains=search_query) |
                Q(post__author__first_name__icontains=search_query) |
                Q(post__author__last_name__icontains=search_query) |
                Q(post__author__email__icontains=search_query) |
                Q(post__category__name__icontains=search_query) |
                Q(post__tags__name__icontains=search_query)
            ).distinct()
        
        queryset = queryset.order_by('-created_at')
        
        return queryset

