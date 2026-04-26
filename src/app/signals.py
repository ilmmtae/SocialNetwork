from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.likes import Like
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Like)
def send_like_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.post.author
        sender_user = instance.user

        logger.info(
            f"NOTIFICATION: User {sender_user.username} liked your post (ID: {instance.post.id}). "
            f"Sending to: {recipient.email}"
        )