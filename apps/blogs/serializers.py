from rest_framework import serializers

from apps.core.serializers import UserSummarySerializer
from .models import Category, Comment, Post, Reaction, Bookmark

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', ]
    def create(self, validated_data):
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Post
        fields = ['id', 'content', 'title', 'author', 'tags', 'category', 'category_id', 'slug', 'thumbnail', 'status', 'comment_count', 'reaction_count', 'bookmark_count', 'views_count', 'created_at', 'updated_at' ]
        read_only_fields = ['author', 'category', 'comment_count', 'reaction_count', 'bookmark_count', 'views_count']
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class PostSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'thumbnail', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    post = PostSummarySerializer(read_only=True)

    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        source="parent",
        required=False
    )
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'parent_id', 'reply_count', 'reaction_count', 'views_count', 'created_at', 'updated_at']
        read_only_fields = ['post', 'user', 'reply_count', 'reaction_count', 'views_count', 'created_at', 'updated_at']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']

class BookmarkSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    post = PostSummarySerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'post', 'created_at']
