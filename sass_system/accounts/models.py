from django.db import models
from django.contrib.auth.models import AbstractUser
from common.Constant.role_constants import RoleTypeConst

class Company(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.CharField(
        max_length=25, 
        null=True, 
        choices=RoleTypeConst.get_choices(),
        default=RoleTypeConst.MEMBER.value
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )