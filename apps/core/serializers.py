from rest_framework import generics, serializers
from .models import User, Follow
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_following = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'profile_pic_url', 'banner_url', 'bio', 'followers_count', 'following_count', 'about', 'phone_number', 'address', 'city', 'state', 'country', 'website', 'linkedin', 'instagram', 'twitter', 'github', 'registration_method', 'is_following', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def get_is_following(self, obj):
        request = self.context.get('request')
        user_id = obj.id
        user = generics.get_object_or_404(User, pk=user_id)
        if not request or not request.user.is_authenticated:
            return False

        return Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_pic_url', 'bio', 'about']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self):
        uid = self.validated_data["uid"]
        token = self.validated_data["token"]
        password = self.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            raise serializers.ValidationError("Invalid reset link")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token")

        user.set_password(password)
        user.save()
        return user

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSummarySerializer(read_only=True)
    following = UserSummarySerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'following', 'created_at']
