import uuid


def is_uuid4(value):
    try:
        uuid.UUID(value, version=4)
    except ValueError:
        return False
    return True
