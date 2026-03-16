from rest_framework import serializers
from .models import Task
from common.Constant.status_constants import StatusTypeConst

class TaskSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=StatusTypeConst.get_choices())

    class Meta:
        model = Task
        fields = "__all__"