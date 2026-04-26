import logging
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Post, Like
from .serializer import PostSerializer, UserInviteSerializer


logger = logging.getLogger(__name__)
User = get_user_model()


class UserInviteView(APIView):
    @extend_schema(
        request=UserInviteSerializer,
        responses={201: {"message": "Invite created and email sent successfully"}},
        description="Creates a user invite and sends an activation link to the provided email address."
    )
    def post(self, request):
        serializer = UserInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data['email']
        invite_code = data['invite_code']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'is_active': False
            }
        )

        cache.set(f"invite:{invite_code}", email, timeout=86400)

        host = getattr(settings, 'HOST', 'http://127.0.0.1:8000')
        activation_link = f"{host}/activate/?code={invite_code}"

        try:
            send_mail(
                subject='Account Registration Confirmation',
                message=f'Welcome! To activate your account, please follow this link: {activation_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Activation email sent to {email}")
        except Exception as e:
            logger.error(f"Email delivery failed: {str(e)}")
            return Response(
                {"error": "Email delivery failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "Invite created and email sent successfully"},
            status=status.HTTP_201_CREATED
        )


class UserActivateView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='code', description='Activation code from email', required=True, type=str),
        ],
        responses={200: {"message": "Account activated successfully"}},
        description="Activates a user account using the unique code stored in the cache."
    )
    def get(self, request):
        invite_code = request.query_params.get('code')

        if not invite_code:
            return Response(
                {"error": "Activation code is missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = cache.get(f"invite:{invite_code}")

        if not email:
            return Response(
                {"error": "Invalid or expired activation code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            cache.delete(f"invite:{invite_code}")

            logger.info(f"User {email} activated successfully")
            return Response(
                {"message": "Account activated successfully", "status": "active"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    @extend_schema(
        description="Retrieve a list of all posts or create a new post instance."
    )
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LikeToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={201: {"message": "Like added"}, 204: {"message": "Like removed"}},
        description="Toggles a like on a post. If like exists, deletes it. If not, creates it."
    )
    def post(self, request, post_id):
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "Like added"}, status=status.HTTP_201_CREATED)