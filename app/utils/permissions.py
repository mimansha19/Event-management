# Check if a user has the necessary role for a specific event
def has_permission(user_id, event_id, role):
    from app.models import Permission
    perm = Permission.query.filter_by(user_id=user_id, event_id=event_id).first()
    return perm and perm.role in role