# core/session_serializers.py
# Custom JSON serializer that supports date/datetime/time and Decimal by converting to strings

import json
import datetime
import decimal


class JSONDateDecimalSerializer:
    """JSON serializer for Django sessions that converts non-JSON types to strings.

    - date/datetime/time -> ISO 8601 string
    - Decimal -> string
    """

    def dumps(self, obj):
        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime, datetime.time)):
                return o.isoformat()
            if isinstance(o, decimal.Decimal):
                return str(o)
            # Fallback: raise TypeError to surface unexpected types
            raise TypeError(
                f"Object of type {o.__class__.__name__} is not JSON serializable"
            )

        # Use latin-1 encoding to match Django's JSONSerializer behavior
        return json.dumps(obj, separators=(",", ":"), default=default).encode("latin-1")

    def loads(self, data):
        # We keep strings as-is; if needed, views can parse ISO strings back to dates/decimals
        return json.loads(data.decode("latin-1"))
