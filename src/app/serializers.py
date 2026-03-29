from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Group

User = get_user_model()

class UserInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    invite_code = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'created_at', 'likes_count']

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'members']