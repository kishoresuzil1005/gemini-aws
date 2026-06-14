from datetime import datetime, timedelta

CACHE = {
    "data": None,
    "expires": None
}

def get_cached_cost():
    if (
        CACHE["data"] is not None and
        CACHE["expires"] is not None and
        datetime.utcnow() < CACHE["expires"]
    ):
        return CACHE["data"]

    return None

def save_cached_cost(data):
    CACHE["data"] = data
    CACHE["expires"] = datetime.utcnow() + timedelta(hours=6)
