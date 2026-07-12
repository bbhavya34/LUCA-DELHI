from .models import ActivityLog


def log_activity(user, action, instance=None):
    try:
        ActivityLog.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            action=action,
            model_name=instance.__class__.__name__ if instance else "",
            object_id=str(instance.pk) if instance and instance.pk else "",
        )
    except Exception:
        return None
