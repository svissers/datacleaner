from flask.json import JSONEncoder
from datetime import date, datetime, time


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat().replace('T', ' ')
            if isinstance(obj, time):
                return obj.isoformat()
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
