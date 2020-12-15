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


__all__ = ('Reader',)


from util import get_logger, MQTTClient, conf
from .device import Device
from .serial_adapter import ReadError
import threading
import time
import json
import mgw_dc


logger = get_logger(__name__.split(".", 1)[-1])


class Reader(threading.Thread):
    __srv_name = "getMeasurements"

    def __init__(self, device: Device, mqtt_client: MQTTClient):
        super().__init__(name="reader-{}".format(device.id), daemon=True)
        self.__device = device
        self.__mqtt_client = mqtt_client

    def run(self) -> None:
        logger.info("starting reader for '{}'".format(self.__device.id))
        count = 0
        try:
            while True:
                try:
                    data = self.__device.get_measurements()
                    try:
                        self.__mqtt_client.publish(
                            topic=mgw_dc.com.gen_event_topic(self.__device.id, Reader.__srv_name),
                            payload=json.dumps(data),
                            qos=1
                        )
                    except Exception as ex:
                        logger.error("can't publish data for '{}' - {}".format(self.__device.id, ex))
                except ReadError as ex:
                    count += 1
                    if count > 3:
                        raise ex
                    time.sleep(1)
        except Exception as ex:
            logger.error("can't read from '{}' - {}".format(self.__device.id, ex))
        self.__device.adapter = None
        self.__device.state = mgw_dc.dm.device_state.offline
        try:
            self.__mqtt_client.publish(
                topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                payload=json.dumps(mgw_dc.dm.gen_set_device_msg(self.__device)),
                qos=1
            )
        except Exception as ex:
            logger.warning("can't update state of '{}' - {}".format(self.__device.id, ex))
        logger.info("reader for '{}' quit".format(self.__device.id))
