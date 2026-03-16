from django.db import models
from accounts.models import User
from projects.models import Project
from common.Constant.status_constants import StatusTypeConst

class Task(models.Model):
    status = models.CharField(
        max_length=25, 
        null=True, 
        choices=StatusTypeConst.get_choices(),
        default=StatusTypeConst.TODO.value
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    due_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True
    )
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)