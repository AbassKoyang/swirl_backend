from django.contrib.auth.models import ContentType
from rest_framework import generics, serializers

from apps.core.serializers import UserSerializer, UserSummarySerializer
from .models import Category, Comment, Post, Reaction, Bookmark, Tag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', 'posts_count']
    def create(self, validated_data):
        return super().create(validated_data)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']
    def create(self, validated_data):
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = serializers.ListField(
            child=serializers.CharField(),
            write_only=True
        )
    tag_objects = TagSerializer(
        source="tags",
        many=True,
        read_only=True
    )    
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()  

    class Meta:
        model = Post
        fields = ['id', 'content', 'subtitle', 'title', 'author', 'tags', 'tag_objects', 'category', 'category_id', 'slug', 'thumbnail', 'status', 'comment_count', 'reaction_count', 'bookmark_count', 'views_count', 'word_count', 'paragraph_count', 'read_time', 'is_liked', 'is_bookmarked', 'created_at', 'updated_at' ]
        read_only_fields = ['author', 'category', 'comment_count', 'reaction_count', 'bookmark_count', 'views_count']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def get_is_liked(self, obj):
        request = self.context.get('request')
        post_id = obj.id
        post = generics.get_object_or_404(Post, pk=post_id)
        post_type = ContentType.objects.get_for_model(Post)
        if not request or not request.user.is_authenticated:
            return False

        return Reaction.objects.filter(
            user=request.user,
            content_type=post_type,
            object_id=post.id
        ).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        post_id = obj.id
        post = generics.get_object_or_404(Post, pk=post_id)
        if not request or not request.user.is_authenticated:
            return False

        return Bookmark.objects.filter(
            user=request.user,
            post=post
        ).exists()

class PostSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'thumbnail', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    post = PostSummarySerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        source="parent",
        required=False
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'parent_id', 'is_liked', 'reply_count', 'reaction_count', 'views_count', 'created_at', 'updated_at']
        read_only_fields = ['post', 'user', 'reply_count', 'reaction_count', 'views_count', 'created_at', 'updated_at']

    def validate_parent(self, parent):
        if parent.parent is not None:
            raise serializers.ValidationError(
                "You cannot reply to a reply."
            )
        return parent

    def get_is_liked(self, obj):
        request = self.context.get('request')
        comment_id = obj.id
        comment = generics.get_object_or_404(Comment, pk=comment_id)
        comment_type = ContentType.objects.get_for_model(Comment)
        if not request or not request.user.is_authenticated:
            return False

        return Reaction.objects.filter(
            user=request.user,
            content_type=comment_type,
            object_id=comment.id
        ).exists()

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']

class BookmarkSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'post', 'created_at']
