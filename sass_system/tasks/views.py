from rest_framework import viewsets, status
from .models import Task, ActivityLog
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .service import TaskService

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task with activity logging."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(project__company=user.company)

    def perform_create(self, serializer):
        task = serializer.save()
        # Simple creation log
        ActivityLog.objects.create(
            user=self.request.user,
            task=task,
            action=f"created task: {task.title}"
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Validate the data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_instance = TaskService.execute(
            user=request.user,
            instance=instance,
            validated_data=serializer.validated_data
        )

        return Response(self.get_serializer(updated_instance).data,status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Log deletion information (task set to NULL in ActivityLog.task so logs persist)
        ActivityLog.objects.create(user=request.user, task=instance, action=f"deleted task: {instance.title}")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

