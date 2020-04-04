import ubinascii, machine
from utime import sleep
from umqtt.simple import MQTTClient


class Mqtt():
    """
    Class obtain connecting to mqtt broker and sending data.
    """    

    def __init__(self, ip, user="", password=""):
        client_id = ubinascii.hexlify(machine.unique_id())
        self._mqtt = MQTTClient(client_id=client_id, server=ip, user=user, password=password)
        self.disconnect()

    def is_connected(self):
        """
        :return: Return True if is connection on mqtt broker.
        :rtype: bool
        """        
        return self.publish()

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
        print("\nMQTT:")
        try:
            _ret = self._mqtt.connect()
            print(_ret)
            if _ret == 0:
                print("\tConnected.")
                return True
            raise OSError
        except:
            print("\tUnable to connect.")
            return False

    def publish(self, topic="test", msg="test"):
        """
        Sending message data to current topic.
        This function is useful for check connection, too.
        
        :param topic: topic, defaults to ""
        :type topic: str, optional
        :param msg: message to send, defaults to ""
        :type msg: str, optional
        :return: Return True if publishing message was successfully.
        :rtype: bool
        """        
        try:
            self._mqtt.publish(topic, msg)
            return True
        except:
            return False
