from .models import ActivityLog

class TaskService:
    @staticmethod
    def execute(user, instance, validated_data):
        """
        the difference between old and new values 
        and creates an ActivityLog entry.
        """
        # Capture old values before the update
        old_values = {
            'status': instance.status,
            'title': instance.title,
            'description': instance.description,
            'project_id': instance.project_id,
            'assigned_to_id': instance.assigned_to_id,
            'due_date': instance.due_date,
        }

        # Perform the actual update on the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Compare with new values
        diffs = []
        if old_values['status'] != instance.status:
            diffs.append(f"status: {old_values['status']} -> {instance.status}")
        if old_values['title'] != instance.title:
            diffs.append(f"title: {old_values['title']} -> {instance.title}")
        if old_values['description'] != instance.description:
            diffs.append("description: changed")
        if old_values['project_id'] != instance.project_id:
            diffs.append(f"project_id: {old_values['project_id']} -> {instance.project_id}")
        if old_values['assigned_to_id'] != instance.assigned_to_id:
            diffs.append(f"assigned_to_id: {old_values['assigned_to_id']} -> {instance.assigned_to_id}")
        if old_values['due_date'] != instance.due_date:
            diffs.append(f"due_date: {old_values['due_date']} -> {instance.due_date}")

        action = "updated task"
        if diffs:
            action = f"updated task: {instance.title} | " + "; ".join(diffs)

        # Create log
        ActivityLog.objects.create(user=user, task=instance, action=action)
        
        return instance