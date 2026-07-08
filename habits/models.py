from django.db import models
from django.contrib.auth.models import User
from squads.models import Squad


class Habit(models.Model):
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='habits')
    title = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.squad.name})"


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    is_done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'user', 'date')

    def __str__(self):
        status = "✓" if self.is_done else "✗"
        return f"{self.user.username} - {self.habit.title} - {self.date} {status}"
