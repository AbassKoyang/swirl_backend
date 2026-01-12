from rest_framework import generics, permissions
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from apps.blogs.models import Post
from apps.blogs.serializers import PostSerializer
from apps.core.models import Follow
from .throttles import FeedRateThrottle, FeedAnonRateThrottle


class PersonalizedFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [FeedRateThrottle]

    def get_queryset(self):
        user = self.request.user
        
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        
        following_ids = list(following_ids) + [user.id]
        
        queryset = Post.objects.filter(
            author_id__in=following_ids,
            status='draft',
            is_deleted=False
        ).select_related('author', 'category').prefetch_related('tags')
        
        return queryset.order_by('-created_at')


class TrendingFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_throttles(self):
        if self.request.user.is_authenticated:
            return [FeedRateThrottle()]
        return [FeedAnonRateThrottle()]

    def get_queryset(self):
        period = self.request.query_params.get('period', '24h')
        
        now = timezone.now()
        if period == '1h':
            threshold = now - timedelta(hours=1)
        elif period == '7d':
            threshold = now - timedelta(days=7)
        elif period == '30d':
            threshold = now - timedelta(days=30)
        else: 
            threshold = now - timedelta(hours=24)
        
        queryset = Post.objects.filter(
            status='draft',
            is_deleted=False,
            created_at__gte=threshold
        ).select_related('author', 'category').prefetch_related('tags')
    
        queryset = queryset.extra(
            select={'engagement_score': 'reaction_count + comment_count + bookmark_count'}
        ).order_by('-engagement_score', '-created_at')
        
        return queryset


class RecentFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_throttles(self):
        if self.request.user.is_authenticated:
            return [FeedRateThrottle()]
        return [FeedAnonRateThrottle()]

    def get_queryset(self):
        queryset = Post.objects.is_draft().select_related('author', 'category').prefetch_related('tags')
        
        return queryset.order_by('-created_at')


class CombinedFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [FeedRateThrottle]

    def get_queryset(self):
        user = self.request.user
        
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        following_ids = list(following_ids) + [user.id]
        
        personalized_posts = Post.objects.filter(
            author_id__in=following_ids,
            status='published',
            is_deleted=False
        )
        
        threshold = timezone.now() - timedelta(hours=24)
        trending_posts = Post.objects.filter(
            status='published',
            is_deleted=False,
            created_at__gte=threshold
        ).extra(
            select={'engagement_score': 'reaction_count + comment_count + bookmark_count'}
        ).order_by('-engagement_score')[:10]
        
        trending_ids = list(trending_posts.values_list('id', flat=True))

        all_posts = Post.objects.is_draft().filter(
            Q(id__in=personalized_posts.values_list('id', flat=True)) |
            Q(id__in=trending_ids),
        ).select_related('author', 'category').prefetch_related('tags')
        
        return all_posts.order_by('-created_at')

