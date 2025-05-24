from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Event, EventVersion
from app.utils.permissions import has_permission
import json
import difflib

bp = Blueprint("versioning", __name__)

@bp.route("/<int:event_id>/history/<int:version_id>", methods=["GET"])
@jwt_required()
def get_version(event_id, version_id): #Retrieves a specific version of the event.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner", "Editor", "Viewer"]):
        return jsonify({"msg": "Permission denied"}), 403
    version = EventVersion.query.filter_by(event_id=event_id, id=version_id).first_or_404()
    return jsonify(json.loads(version.version_data)), 200

@bp.route("/<int:event_id>/rollback/<int:version_id>", methods=["POST"])
@jwt_required()
def rollback(event_id, version_id): #Rolls back the event to a previous version and creates a new version entry.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner"]):
        return jsonify({"msg": "Permission denied"}), 403
    version = EventVersion.query.filter_by(event_id=event_id, id=version_id).first_or_404()
    data = json.loads(version.version_data)
    event = Event.query.get_or_404(event_id)
    for key, value in data.items():
        if hasattr(event, key):
            setattr(event, key, value)
    db.session.commit()

    new_version = EventVersion(
        event_id=event.id,
        version_data=json.dumps(data),
        created_by=user_id
    )
    db.session.add(new_version)
    db.session.commit()

    return jsonify({"msg": "Rolled back"}), 200

@bp.route("/<int:event_id>/changelog", methods=["GET"])
@jwt_required()
def changelog(event_id): #Shows a chronological changelog of all updates to an event.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner", "Editor", "Viewer"]):
        return jsonify({"msg": "Permission denied"}), 403
    versions = EventVersion.query.filter_by(event_id=event_id).order_by(EventVersion.created_at).all()
    return jsonify([
        {"id": v.id, "created_by": v.created_by, "created_at": v.created_at.isoformat()}
        for v in versions
    ]), 200

@bp.route("/<int:event_id>/diff/<int:version_id1>/<int:version_id2>", methods=["GET"])
@jwt_required()
def version_diff(event_id, version_id1, version_id2): #Shows the differences between two versions of an event.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner", "Editor", "Viewer"]):
        return jsonify({"msg": "Permission denied"}), 403
    v1 = EventVersion.query.filter_by(event_id=event_id, id=version_id1).first_or_404()
    v2 = EventVersion.query.filter_by(event_id=event_id, id=version_id2).first_or_404()
    data1 = json.loads(v1.version_data)
    data2 = json.loads(v2.version_data)

    diffs = {}
    for key in data1:
        if key in data2 and data1[key] != data2[key]:
            diffs[key] = {
                "from": data1[key],
                "to": data2[key],
                "diff": list(difflib.unified_diff(
                    [str(data1[key])],
                    [str(data2[key])],
                    lineterm=""
                ))
            }
    return jsonify(diffs), 200