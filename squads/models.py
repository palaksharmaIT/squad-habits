from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta


class Squad(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_squads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SquadMember(models.Model):
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('squad', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.squad.name}"


class InviteLink(models.Model):
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='invites')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"Invite for {self.squad.name}"
    

  
    
