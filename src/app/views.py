import os

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

User = get_user_model()

class UserInviteView(APIView):
    def post(self, request):
        email = request.data.get('email')
        invite_code = request.data.get('invite_code')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not email or not invite_code:
            return Response(
                {"error": "Email and invite_code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': False
            }
        )

        cache.set(f"invite:{invite_code}", email, timeout=86400)

        activation_link = f"{os.getenv("HOST")}/activate/?code={invite_code}"

        try:
            send_mail(
                subject='Account Registration Confirmation',
                message=f'Welcome! To activate your account, please follow this link: {activation_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {"error": f"Email delivery failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "Invite created and email sent successfully"},
            status=status.HTTP_201_CREATED
        )

class UserActivateView(APIView):
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

            return Response(
                {"message": "Account activated successfully", "status": "active"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )