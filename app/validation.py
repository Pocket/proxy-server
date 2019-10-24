from uuid import UUID


def is_valid_pocket_id(u):
    try:
        u = u.lstrip('{')
        u = u.rstrip('}')
        u = u.lower()
        parsed = UUID(u)
    except ValueError:
        return False

    return u == str(parsed)
