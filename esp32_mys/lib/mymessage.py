

class MyMessage():
    def __init__(self, sensor, type):
        self._sensor = sensor
        self._type = type
        self._payload = None

    def set_type(self, type):
        self._type = type
        return self

    def set_sensor(self, sensor):
        self._sensor = sensor
        return self

    def set(self, payload):
        self._payload = payload
        return self

    def get(self):
        return self._payload

    @property
    def sensor(self):
        return self._sensor

    @property
    def type(self):
        return self._type

    @property
    def payload(self):
        return self._payload
