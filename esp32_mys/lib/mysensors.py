import utime
import network
from lib import mtypes
from lib.utils import millis
import machine


class MySensors():
    def __init__(self, mysensors_cfg, debug=False):
        self._debug_enabled = debug
        self._node_id = mysensors_cfg['id']
        self._mqtt_cfg = mysensors_cfg['mqtt']
        self._mqtt_client = network.mqtt(
            "esp32_{}".format(millis()),
            self._mqtt_cfg['broker'],
            user=self._mqtt_cfg['user'],
            password=self._mqtt_cfg['password'],
            port=self._mqtt_cfg['port'],
            cleansession=True,
            connected_cb=self._mqtt_connected_cb,
            disconnected_cb=self._mqtt_disconnected_cb,
            subscribed_cb=self._mqtt_subscribed_cb,
            data_cb=self._mqtt_data_cb,
            autoreconnect=True
        )
        self._mqtt_stopped = True
        self._msg_cb = None
        self._presentation_cb = None
        self.NODE_SENSOR_ID = 255  # special child id used for internal messages
        self.BROADCAST_NODE_ID = 255  # special node id used for internal messages

    def _debug(self, msg):
        if self._debug_enabled:
            print(msg)

    def begin(self):
        if self._mqtt_stopped:
            self._debug("[MQTT] Connecting ...")
            self._mqtt_client.start()
            self._mqtt_stopped = False

    def end(self):
        if not self._mqtt_stopped:
            self._mqtt_client.stop()
            self._mqtt_stopped = True
            self._debug("[MQTT] Terminated ...")

    @property
    def connected(self):
        return True if "Connected" in self._mqtt_client.status() else False

    def register_on_message_cb(self, msg_cb):
        self._msg_cb = msg_cb

    def register_presentation_cb(self, presentation_cb):
        self._presentation_cb = presentation_cb

    def _mqtt_connected_cb(self, task):
        self._debug("[MQTT] Connected!")
        # it seems that it doesn't like here to do the subscribe - it's much more cleaner this way but ...
        self._mqtt_client.subscribe("{}/#".format(self._mqtt_cfg['in_topic_prefix']), self._mqtt_cfg['qos'])
        if self._presentation_cb is not None:
            self._presentation_cb()

    def _mqtt_disconnected_cb(self, task):
        self._debug("[MQTT] Disconnected!")

    def _mqtt_subscribed_cb(self, task):
        self._debug("[MQTT] Subscribed to topic: {} ...".format(self._mqtt_cfg['in_topic_prefix']))

    def _mqtt_data_cb(self, msg):
        topic = msg[1]
        payload = msg[2]
        node_id, child_id, cmd_type, ack, sub_type, payload = self._mys_mycontroller_in(topic, payload)

        # process internal messages here
        if cmd_type == mtypes.M_INTERNAL:
            if sub_type == mtypes.I_PRESENTATION:
                self._debug("[MYSENSORS] Received I_PRESENTATION internal command on topic: {}".format(topic))
                if self._presentation_cb is not None:
                    self._presentation_cb()
            elif sub_type == mtypes.I_DISCOVER_REQUEST:
                self._debug("[MYSENSORS] Received I_DISCOVER_REQUEST internal command on topic: {}".format(topic))
                self.send_discovery_response()
            elif sub_type == mtypes.I_HEARTBEAT_REQUEST:
                self._debug("[MYSENSORS] Received I_HEARTBEAT_REQUEST internal command on topic: {}".format(topic))
                self.send_heartbeat()
            elif sub_type == mtypes.I_REBOOT:
                self._debug("[MYSENSORS] Received I_REBOOT internal command on topic: {}".format(topic))
                self._mqtt_client.stop()
                machine.reset()
            else:
                self._debug("[MYSENSORS] Received unknown data: %s on topic: {}".format(payload, topic))
            return

        # call user callback to pass received MySensors data for this node id only
        if self._msg_cb is not None and node_id == self._node_id:
            data = {
                'node_id': node_id,
                'child_id': child_id,
                'cmd_type': cmd_type,
                'ack': ack,
                'sub_type': sub_type,
                'payload': payload
            }
            self._msg_cb(data)

    def _mys_mycontroller_in(self, topic, payload):
        mqtt_topic_data = topic.split('/')
        node_id = int(mqtt_topic_data[1])
        child_id = int(mqtt_topic_data[2])
        cmd_type = int(mqtt_topic_data[3])
        ack = int(mqtt_topic_data[4])
        sub_type = int(mqtt_topic_data[5])
        return (node_id, child_id, cmd_type, ack, sub_type, payload)

    def _mys_mycontroller_out(self, data):
        if self._mqtt_client is not None and self.connected:
            topic = "%s/%s/%s/%s/%s/%s" % (self._mqtt_cfg['out_topic_prefix'],
                                           self._node_id,
                                           data['child_sensor_id'],
                                           data['msg_type'], data['ack'],
                                           data['sub_type'])
            self._debug("[MQTT] Publishing: %s on topic: %s" % (data['payload'], topic))
            self._mqtt_client.publish(topic, str(data['payload']), self._mqtt_cfg['qos'])

    def _send_presentation(self, child_sensor_id, child_sub_type, child_sensor_alias, ack=0):
        data = {}
        data['child_sensor_id'] = child_sensor_id
        data['msg_type'] = mtypes.M_PRESENTATION
        data['ack'] = ack
        data['sub_type'] = child_sub_type  # e.g. mtypes.S_BINARY
        data['payload'] = child_sensor_alias
        self._mys_mycontroller_out(data)

    def present(self, id, type, alias='Unknown', ack=0):
        # present this node as a MySensors node first
        self._send_presentation(self.NODE_SENSOR_ID, mtypes.S_ARDUINO_NODE, '', ack)
        self._send_presentation(id, type, alias, ack)

    def send_sketch_info(self, version='Unknown', ack=0):
        data = {}
        data['child_sensor_id'] = self.NODE_SENSOR_ID
        data['msg_type'] = mtypes.M_INTERNAL
        data['ack'] = ack
        data['sub_type'] = mtypes.I_SKETCH_NAME
        data['payload'] = version
        self._mys_mycontroller_out(data)

    def send_sketch_version(self, version='Unknown', ack=0):
        data = {}
        data['child_sensor_id'] = self.NODE_SENSOR_ID
        data['msg_type'] = mtypes.M_INTERNAL
        data['ack'] = ack
        data['sub_type'] = mtypes.I_SKETCH_VERSION
        data['payload'] = version
        self._mys_mycontroller_out(data)

    def send_heartbeat(self, ack=0):
        data = {}
        data['child_sensor_id'] = self.NODE_SENSOR_ID
        data['msg_type'] = mtypes.M_INTERNAL
        data['ack'] = ack
        data['sub_type'] = mtypes.I_HEARTBEAT_RESPONSE
        data['payload'] = millis()
        self._mys_mycontroller_out(data)

    def send_battery_level(self, value, ack=0):
        data = {}
        data['child_sensor_id'] = self.NODE_SENSOR_ID
        data['msg_type'] = mtypes.M_INTERNAL
        data['ack'] = ack
        data['sub_type'] = mtypes.I_BATTERY_LEVEL
        data['payload'] = value
        self._mys_mycontroller_out(data)

    def send_discovery_response(self, parent_node_id=0, ack=0):
        data = {}
        data['child_sensor_id'] = self.NODE_SENSOR_ID
        data['msg_type'] = mtypes.M_INTERNAL
        data['ack'] = ack
        data['sub_type'] = mtypes.I_DISCOVER_RESPONSE
        data['payload'] = parent_node_id
        self._mys_mycontroller_out(data)

    def send(self, my_message, ack=0):
        data = {}
        data['child_sensor_id'] = my_message.sensor
        data['msg_type'] = mtypes.M_SET
        data['ack'] = ack
        data['sub_type'] = my_message.type  # e.g. mtypes.V_STATUS
        data['payload'] = my_message.payload
        self._mys_mycontroller_out(data)
