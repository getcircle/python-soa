import uuid


def is_uuid4(value):
    try:
        uuid.UUID(value, version=4)
    except ValueError:
        return False
    return True


def is_uuid4_list(value):
    try:
        results = map(is_uuid4, value)
    except TypeError:
        return False
    return all(results)
