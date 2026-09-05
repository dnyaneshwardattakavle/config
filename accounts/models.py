from django.db import models
from django.contrib.auth.models import AbstractUser


class user(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.TextField(help_text="Comma separated skills")
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username