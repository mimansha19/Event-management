# Marshmallow schemas for serializing and deserializing event and user objects
from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Str()

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    location = fields.Str()
    is_recurring = fields.Bool()
    recurrence_pattern = fields.Str()