# Create, read, update, delete, batch create events
# Uses versioning on updates and creates
# Validates permissions using `has_permission()


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Event, Permission, EventVersion
from app.schemas import EventSchema
from app.utils.permissions import has_permission
from datetime import datetime
import json

bp = Blueprint("events", __name__)
event_schema = EventSchema()
event_list_schema = EventSchema(many=True)

@bp.route("/", methods=["POST"])
@jwt_required()
def create_event(): #Creates a new event, assigns the user as owner, and stores the initial version.
    user_id = int(get_jwt_identity())
    data = request.json
    event = Event(
        title=data["title"],
        description=data["description"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]),
        location=data.get("location"),
        is_recurring=data.get("is_recurring", False),
        recurrence_pattern=data.get("recurrence_pattern"),
        created_by=user_id
    )
    db.session.add(event)
    db.session.commit()
    
    perm = Permission(user_id=user_id, event_id=event.id, role="Owner")
    db.session.add(perm)
    db.session.commit()

    version = EventVersion(
        event_id=event.id,
        version_data=json.dumps(event_schema.dump(event)),
        created_by=user_id
    )
    db.session.add(version)
    db.session.commit()

    return jsonify(event_schema.dump(event)), 201

@bp.route("/", methods=["GET"])
@jwt_required()
def list_events(): #Lists all events the user has access to.
    user_id = int(get_jwt_identity())
    perms = Permission.query.filter_by(user_id=user_id).all()
    event_ids = [p.event_id for p in perms]
    events = Event.query.filter(Event.id.in_(event_ids)).all()
    return jsonify(event_list_schema.dump(events)), 200

@bp.route("/<int:event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id): #Returns a specific event by ID if the user has permission.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner", "Editor", "Viewer"]):
        return jsonify({"msg": "Permission denied"}), 403
    event = Event.query.get_or_404(event_id)
    return jsonify(event_schema.dump(event)), 200

@bp.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event(event_id): #Updates an event and saves the new version in version history.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner", "Editor"]):
        return jsonify({"msg": "Permission denied"}), 403
    event = Event.query.get_or_404(event_id)
    data = request.json
    for field in ["title", "description", "start_time", "end_time", "location", "is_recurring", "recurrence_pattern"]:
        if field in data:
            setattr(event, field, data[field])
    db.session.commit()

    version = EventVersion(
        event_id=event.id,
        version_data=json.dumps(event_schema.dump(event)),
        created_by=user_id
    )
    db.session.add(version)
    db.session.commit()

    return jsonify(event_schema.dump(event)), 200

@bp.route("/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id): #Deletes an event if the user is the owner.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner"]):
        return jsonify({"msg": "Permission denied"}), 403
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"msg": "Event deleted"}), 200

@bp.route("/batch", methods=["POST"])
@jwt_required()
def batch_create(): #Creates multiple events in a single request and assigns ownership to the user.
    user_id = int(get_jwt_identity())
    events_data = request.json.get("events", [])
    created_events = []
    for data in events_data:
        event = Event(
            title=data["title"],
            description=data["description"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            location=data.get("location"),
            is_recurring=data.get("is_recurring", False),
            recurrence_pattern=data.get("recurrence_pattern"),
            created_by=user_id
        )
        db.session.add(event)
        db.session.flush()
        db.session.add(Permission(user_id=user_id, event_id=event.id, role="Owner"))
        db.session.add(EventVersion(
            event_id=event.id,
            version_data=json.dumps(event_schema.dump(event)),
            created_by=user_id
        ))
        created_events.append(event)
    db.session.commit()
    return jsonify(event_list_schema.dump(created_events)), 201