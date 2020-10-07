import ubinascii, machine
from utime import sleep
from umqtt.simple import MQTTClient


class Mqtt:
    """
    Class obtain connecting to mqtt broker and sending data.
    """

    def __init__(self, ip, user="", password="", keepalive=0):
        client_id = ubinascii.hexlify(machine.unique_id())
        self._mqtt = MQTTClient(
            client_id=client_id,
            server=ip,
            user=user,
            password=password,
            keepalive=keepalive,
        )
        self.disconnect()

    def set_last_will(self, topic, msg, retain, qos):
        self._mqtt.set_last_will(topic, msg, retain, qos)

    def is_connected(self):
        """
        :return: Return True if is connection on mqtt broker.
        :rtype: bool
        """
        return self.publish(allow_print=False)

    def disconnect(self):
        try:
            self._mqtt.disconnect()
        except:
            pass

    def connect(self):
        """
        Trying connect to mqqt broker.
        If successfull then return.
        :return: Return True if connecting is OK.
        :rtype: bool
        """
        print("\nMQTT conecting...")
        try:
            _ret = self._mqtt.connect()
            print(_ret)
            if _ret == 0:
                print("\tMQTT connected to broker.")
                return True
            raise OSError
        except:
            print("\tMQTT unable to connect broker.")
            return False

    def publish(self, topic="test", msg="test", allow_print=True, retain=False, qos=0):
        """
        Sending message data to current topic.
        This function is useful for check connection, too.
        
        :param topic: topic, defaults to ""
        :type topic: str, optional
        :param msg: message to send, defaults to ""
        :type msg: str, optional
        :param allow_print: allow print sending process. In error always print
        :type allow_print: bool, optional
        :type retain: bool, defaults to False
        :type qos: int 0-2, defaults to 0
        :return: Return True if publishing message was successfully.
        :rtype: bool
        """
        try:
            if allow_print:
                print("\tSending message '{}' to topic '{}'".format(msg, topic))
            self._mqtt.publish(topic=topic, msg=msg, retain=retain, qos=qos)
            if allow_print:
                print("\t\tSending OK")
            return True
        except Exception as ex:
            print("\t\tSending ERROR: {}".format(ex))
            return False
