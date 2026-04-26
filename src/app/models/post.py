from django.db import models
from django.core.exceptions import ValidationError

class Post(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.content and not self.image:
            raise ValidationError("The post cannot be empty. Please add text or an image.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)