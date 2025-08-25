"""
Marshmallow schemas for request validation in the study framework.
"""

from marshmallow import Schema, fields, ValidationError

class LoginSchema(Schema):
    """Schema for login requests."""
    uid = fields.String(required=True)
    password = fields.String(required=True)
    device = fields.String(required=True)
    auth_key = fields.String()

class LoginCodeSchema(Schema):
    """Schema for login code requests."""
    code = fields.String(required=False)
    uid = fields.String(required=False)
    device = fields.String(required=True)
    auth_key = fields.String()

class BasicUserSchema(Schema):
    """Schema for basic user requests."""
    uid = fields.String(required=True)
    auth_key = fields.String()

class UserPingSchema(Schema):
    """Schema for user ping requests."""
    uid = fields.String(required=True)
    device = fields.String(required=True)
    device_type = fields.String()
    # empatica_connected = fields.Number()  # REMOVED (outdated, no longer used)
    auth_key = fields.String()

class EMASchema(Schema):
    """Schema for EMA requests."""
    uid = fields.String(required=True)
    auth_key = fields.String()
    timestamp = fields.String(required=True)
    event_id = fields.Number(required=True)
    event = fields.String(required=True)
    device_type = fields.String(required=True)

class UploadFileSchema(Schema):
    """Schema for file upload requests."""
    uid = fields.String(required=True)
    auth_key = fields.String()
    file = fields.Field()

class DebugSchema(Schema):
    """Schema for debug requests."""
    uid = fields.String(required=True)
    timestamp = fields.String(required=True)
    message = fields.String(required=True)
    auth_key = fields.String()

class UserInfoSchema(Schema):
    """Schema for user info update requests."""
    uid = fields.String(required=True)
    info_key = fields.String(required=True)
    info_value = fields.String(required=True)
    auth_key = fields.String()

class SocialMediaSchema(Schema):
    """Schema for social media requests."""
    uid = fields.String(required=True)
    account_type = fields.String(required=True)
    data_check = fields.Number(required=True)
    auth_key = fields.String()
    type = fields.String(required=True)
