from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Permission, Event
from app import db
from app.utils.permissions import has_permission

bp = Blueprint("collaboration", __name__)

@bp.route("/<int:event_id>/share", methods=["POST"])
@jwt_required()
def share_event(event_id): #Allows the owner to share an event with users and assign roles.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner"]):
        return jsonify({"msg": "Permission denied"}), 403
    users = request.json.get("users", [])
    for user in users:
        perm = Permission(user_id=user["user_id"], event_id=event_id, role=user["role"])
        db.session.add(perm)
    db.session.commit()
    return jsonify({"msg": "Permissions updated"}), 200

@bp.route("/<int:event_id>/permissions", methods=["GET"])
@jwt_required()
def list_permissions(event_id): # Lists all user permissions for a specific event.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner"]):
        return jsonify({"msg": "Permission denied"}), 403
    perms = Permission.query.filter_by(event_id=event_id).all()
    return jsonify([{"user_id": p.user_id, "role": p.role} for p in perms]), 200

@bp.route("/<int:event_id>/permissions/<int:perm_user_id>", methods=["PUT"])
@jwt_required()
def update_permission(event_id, perm_user_id): #Updates a user's role for a shared event.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner"]):
        return jsonify({"msg": "Permission denied"}), 403
    perm = Permission.query.filter_by(event_id=event_id, user_id=perm_user_id).first()
    if not perm:
        return jsonify({"msg": "User not found"}), 404
    perm.role = request.json.get("role")
    db.session.commit()
    return jsonify({"msg": "Permission updated"}), 200

@bp.route("/<int:event_id>/permissions/<int:perm_user_id>", methods=["DELETE"])
@jwt_required()
def remove_permission(event_id, perm_user_id): #Removes a user's access to the event.
    user_id = int(get_jwt_identity())
    if not has_permission(user_id, event_id, ["Owner"]):
        return jsonify({"msg": "Permission denied"}), 403
    Permission.query.filter_by(event_id=event_id, user_id=perm_user_id).delete()
    db.session.commit()
    return jsonify({"msg": "Permission removed"}), 200