from rest_framework import viewsets, status
from .models import Task, ActivityLog
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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

        # capture old values for a small diff
        old_values = {
            'status': instance.status,
            'title': instance.title,
            'description': instance.description,
            'project_id': instance.project_id,
            'assigned_to_id': instance.assigned_to_id,
            'due_date': instance.due_date,
        }

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new = serializer.instance
        diffs = []
        if old_values['status'] != new.status:
            diffs.append(f"status: {old_values['status']} -> {new.status}")
        if old_values['title'] != new.title:
            diffs.append(f"title: {old_values['title']} -> {new.title}")
        if old_values['description'] != new.description:
            diffs.append("description: changed")
        if old_values['project_id'] != new.project_id:
            diffs.append(f"project_id: {old_values['project_id']} -> {new.project_id}")
        if old_values['assigned_to_id'] != new.assigned_to_id:
            diffs.append(f"assigned_to_id: {old_values['assigned_to_id']} -> {new.assigned_to_id}")
        if old_values['due_date'] != new.due_date:
            diffs.append(f"due_date: {old_values['due_date']} -> {new.due_date}")

        action = "updated task"
        if diffs:
            action = f"updated task: {new.title} | " + "; ".join(diffs)

        ActivityLog.objects.create(user=request.user, task=new, action=action)

        return Response(self.get_serializer(new).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Log deletion information (task set to NULL in ActivityLog.task so logs persist)
        ActivityLog.objects.create(user=request.user, task=instance, action=f"deleted task: {instance.title}")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

