
from django.db.models import F
from rest_framework import generics, filters, permissions, pagination
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from .permissions import IsCommentOwner, IsOwner, IsBookmarkOwner
from .throttles import (
    PostCreateRateThrottle, PostUpdateRateThrottle, PostReadRateThrottle, PostReadAnonRateThrottle,
    CommentCreateRateThrottle, ReactionRateThrottle, BookmarkRateThrottle
)
from apps.notifications.utils import create_notification

from .serializers import CommentSerializer, PostSerializer, CategorySerializer, ReactionSerializer, BookmarkSerializer, TagSerializer

from .models import Post, Category, Comment, Reaction, Bookmark, Tag
from apps.core.models import User
# Create your views here

class PostsListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.active()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_throttles(self):
        if self.request.method == 'GET':
            if self.request.user.is_authenticated:
                return [PostReadRateThrottle()]
            return [PostReadAnonRateThrottle()]
        return [PostCreateRateThrottle()]
    

    def get_queryset(self):
        qs = super().get_queryset().select_related("author")
        status = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        if status == 'draft':
            qs = qs.is_draft()
        elif status  == 'published':
            qs = qs.is_published()
        if category:
            qs = qs.filter(post__category=category)
        return qs

    def perform_create(self, serializer):
        print(serializer.validated_data)
        validated_data = serializer.validated_data
        tag_names = validated_data.pop("tags", [])
        tags = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=name.lower().strip(),
                defaults={"slug": name.lower().replace(" ", "-")}
            )
            tags.append(tag)
        serializer.save(author=self.request.user, tags=tags)

class PostsUpdateView(generics.UpdateAPIView):
    queryset= Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]
    throttle_classes = [PostUpdateRateThrottle]

    lookup_field = 'pk'
    lookup_url_kwarg='id'

    def perform_update(self, serializer):
        instance = serializer.save();
        instance.save()

class PostDeleteView(generics.DestroyAPIView):
    queryset= Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'
    lookup_url_kwarg='id'

    def perform_destroy(self, serializer):
        instance = serializer.save();
        instance.is_deleted = True
        instance.save()

class PostRetrieveView(generics.RetrieveAPIView):
    queryset= Post.objects.all()
    serializer_class = PostSerializer
    throttle_classes = [PostReadRateThrottle]
    lookup_field = 'slug'
    lookup_url_kwarg='slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views count
        Post.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        # Refresh instance to get updated views_count
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_throttles(self):
        if self.request.method == 'GET':
            return [PostReadRateThrottle()]
        return [CommentCreateRateThrottle()]

    def get_queryset(self):
        post_id = self.kwargs["id"]
        return super().get_queryset().filter(post_id=post_id,parent__isnull=True).select_related('user')

    def perform_create(self, serializer):
        post_id = self.kwargs["id"]
        post = generics.get_object_or_404(Post, pk=post_id)
        comment = serializer.save(post=post, user=self.request.user)
        Post.objects.filter(pk=post_id).update(
            comment_count=F("comment_count") + 1
        )
        create_notification(
            user=post.author,
            actor=self.request.user,
            action_type='comment',
            target_object=post
        )

class RetrieveCommentView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views count
        Comment.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        # Refresh instance to get updated views_count
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views count
        Comment.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        # Refresh instance to get updated views_count
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwner]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwner]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

    def perform_destroy(self, instance):
        parent = instance.parent
        if parent:
            Comment.objects.filter(pk=parent.pk).update(
                reply_count=F("reply_count") - 1
        )
        instance.delete()

class RepliesListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [CommentCreateRateThrottle]

    def get_queryset(self):
        return Comment.objects.filter(parent_id=self.kwargs['id']).select_related('user')

    def perform_create(self, serializer):
        user = self.request.user
        parent = generics.get_object_or_404(Comment, pk=self.kwargs['id'])
        reply = serializer.save(
            user=user,
            parent=parent,
            post=parent.post
        )
        
        Comment.objects.filter(pk=parent.pk).update(
            reply_count=F("reply_count") + 1
        )
        create_notification(
            user=parent.user,
            actor=user,
            action_type='reply',
            target_object=parent
        )

class PostReactionListCreateView(generics.ListCreateAPIView):
    serializer_class = ReactionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_throttles(self):
        if self.request.method == 'GET':
            return [PostReadRateThrottle()]
        return [ReactionRateThrottle()]
    
    def get_queryset(self):
        reaction_type = self.request.query_params
        post_id = self.kwargs['id']
        post = generics.get_object_or_404(Post, pk=post_id)
        if reaction_type == 'upvote':
            return Reaction.objects.filter(object_id=post.id, reaction_type=reaction_type).select_related('user')
        elif reaction_type == 'downvote':
            return Reaction.objects.filter(object_id=post.id, reaction_type=reaction_type).select_related('user')
        
        return Reaction.objects.filter(object_id=post.id).select_related('user')
    
    def perform_create(self, serializer):
        post_id = self.kwargs['id']
        post = generics.get_object_or_404(Post, pk=post_id)
        post_type = ContentType.objects.get_for_model(Post)
        reaction_type = serializer.validated_data['reaction_type']
        reaction = Reaction.objects.filter(
            user=self.request.user,
            content_type=post_type,
            object_id=post.id
        ).first()

        if reaction and reaction.reaction_type == reaction_type:
            Post.objects.filter(
                pk=post_id,
                reaction_count__gt=0
            ).update(
                reaction_count=F("reaction_count") - 1
            )
            reaction.delete()
        elif reaction and reaction.reaction_type != reaction_type:
            reaction.reaction_type = reaction_type
            reaction.save(update_fields=["reaction_type"])
        else:
            reaction = serializer.save(
                user=self.request.user,
                content_type=post_type,
                object_id=post.id
            )
            Post.objects.filter(pk=post_id).update(
                reaction_count=F("reaction_count") + 1
            )
            create_notification(
                user=post.author,
                actor=self.request.user,
                action_type='reaction',
                target_object=post
            )

class CommentReactionListCreateView(generics.ListCreateAPIView):
    serializer_class = ReactionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_throttles(self):
        if self.request.method == 'GET':
            return [PostReadRateThrottle()]
        return [ReactionRateThrottle()]
    
    def get_queryset(self):
        reaction_type = self.request.query_params
        comment_id = self.kwargs['id']
        comment = generics.get_object_or_404(Comment, pk=comment_id)
        if reaction_type == 'upvote':
            return Reaction.objects.filter(object_id=comment.id, reaction_type=reaction_type).select_related('user')
        elif reaction_type == 'downvote':
            return Reaction.objects.filter(object_id=comment.id, reaction_type=reaction_type).select_related('user')
        
        return Reaction.objects.filter(object_id=comment.id).select_related('user')

    def perform_create(self, serializer):
        comment_id = self.kwargs['id']
        comment = generics.get_object_or_404(Comment, pk=comment_id)
        comment_type = ContentType.objects.get_for_model(Comment)
        reaction_type = serializer.validated_data['reaction_type']
        reaction = Reaction.objects.filter(
            user=self.request.user,
            content_type=comment_type,
            object_id=comment.id
        ).first()

        if reaction and reaction.reaction_type == reaction_type:
            Comment.objects.filter(
                pk=comment_id,
                reaction_count__gt=0
            ).update(
                reaction_count=F("reaction_count") - 1
            )
            reaction.delete()
        elif reaction and reaction.reaction_type != reaction_type:
            reaction.reaction_type = reaction_type
            reaction.save(update_fields=["reaction_type"])
        else:
            reaction = serializer.save(
                user=self.request.user,
                content_type=comment_type,
                object_id=comment.id
            )
            Comment.objects.filter(pk=comment_id).update(
                reaction_count=F("reaction_count") + 1
            )
            create_notification(
                user=comment.user,
                actor=self.request.user,
                action_type='reaction',
                target_object=comment
            )

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class BookmarkCreateView(generics.CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [BookmarkRateThrottle]


    def perform_create(self, serializer):
        post_id = self.kwargs['id']
        post = generics.get_object_or_404(Post, pk=post_id)
        if post:
            bookmark = serializer.save(user=self.request.user, post=post)
            Post.objects.filter(
                pk=post_id).update(
                bookmark_count=F("bookmark_count") + 1
            )
            # Create notification for post author
            create_notification(
                user=post.author,
                actor=self.request.user,
                action_type='bookmark',
                target_object=post
            )

class BookmarkDeleteView(generics.DestroyAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookmarkOwner]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

    def perform_destroy(self, instance):
        post_id = self.kwargs['id']
        post = generics.get_object_or_404(Post, pk=post_id)
        if post:
            Post.objects.filter(
                pk=post_id,
                bookmark_count__gt=0
            ).update(
                bookmark_count=F("bookmark_count") - 1
            )
            instance.delete()

class ListUserBookmarksView(generics.ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookmarkOwner]
    def  get_queryset(self):
        userId = self.kwargs['id']
        user = generics.get_object_or_404(User, pk=userId)
        return Bookmark.objects.filter(user=user).select_related('post').select_related('user')
        
class ListUserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def  get_queryset(self):
        userId = self.kwargs['id']
        user = generics.get_object_or_404(User, pk=userId)
        return Post.objects.filter(author=user).select_related('author')