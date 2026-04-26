from rest_framework import serializers
from .user import UserSerializer
from ..models.group import Group

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'members']