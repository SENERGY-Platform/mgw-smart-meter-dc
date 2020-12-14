"""
   Copyright 2020 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("MQTTClient", )


from .logger import getLogger
from .config import conf
import paho.mqtt.client
import time
import mgw_dc


logger = getLogger(__name__.split(".", 1)[-1])


class MQTTClient:
    def __init__(self):
        self.__client = paho.mqtt.client.Client(
            client_id=conf.Client.id,
            clean_session=conf.Client.clean_session
        )
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.__client.will_set(topic=mgw_dc.dm.gen_last_will_topic(conf.Client.id), payload="1", qos=2)
        if conf.Logger.enable_mqtt:
            self.__client.enable_logger(logger)
        self.on_connect = None
        self.on_message = None

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("connected to '{}'".format(conf.MsgBroker.host))
            self.__client.subscribe(mgw_dc.dm.gen_refresh_topic(), 1)
            self.on_connect()
        else:
            logger.error("could not connect to '{}' - {}".format(conf.MsgBroker.host, paho.mqtt.client.connack_string(rc)))

    def __on_disconnect(self, client, userdata, rc):
        if rc == 0:
            logger.info("disconnected from '{}'".format(conf.MsgBroker.host))
        else:
            logger.warning("disconnected from '{}' unexpectedly".format(conf.MsgBroker.host))

    def __on_message(self, client, userdata, message: paho.mqtt.client.MQTTMessage):
        self.on_message(message.topic, message.payload)

    def start(self):
        while True:
            try:
                self.__client.connect(conf.MsgBroker.host, conf.MsgBroker.port, keepalive=conf.Client.keep_alive)
                self.__client.loop_forever()
                break
            except Exception as ex:
                logger.error(
                    "could not connect to '{}' on '{}' - {}".format(conf.MsgBroker.host, conf.MsgBroker.port, ex)
                )
                time.sleep(5)

    def subscribe(self, topic: str, qos: int) -> None:
        res = self.__client.subscribe(topic=topic, qos=qos)
        if res[0] is paho.mqtt.client.MQTT_ERR_SUCCESS:
            logger.debug("subscribed to '{}'".format(topic))
        else:
            raise RuntimeError(paho.mqtt.client.error_string(res[0]).replace(".", "").lower())

    def unsubscribe(self, topic: str) -> None:
        res = self.__client.unsubscribe(topic=topic)
        if res[0] is paho.mqtt.client.MQTT_ERR_SUCCESS:
            logger.debug("unsubscribed from '{}'".format(topic))
        else:
            raise RuntimeError(paho.mqtt.client.error_string(res[0]).replace(".", "").lower())

    def publish(self, topic: str, payload: str, qos: int) -> None:
        msg_info = self.__client.publish(topic=topic, payload=payload, qos=qos, retain=False)
        if msg_info.rc == paho.mqtt.client.MQTT_ERR_SUCCESS:
            logger.debug("published '{}' - (q{}, m{})".format(payload, qos, msg_info.mid))
        else:
            raise RuntimeError(paho.mqtt.client.error_string(msg_info.rc).replace(".", "").lower())
