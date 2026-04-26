from rest_framework import serializers

class UserInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    invite_code = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)