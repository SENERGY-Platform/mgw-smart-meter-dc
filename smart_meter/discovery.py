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


__all__ = ("Discovery", )


from util import get_logger, conf, MQTTClient
from .serial_adapter import SerialAdapter, ReadError
from .reader import Reader
from .device import Device
import threading
import os
import time
import json
import typing
import mgw_dc


logger = get_logger(__name__.split(".", 1)[-1])


def get_ports() -> list:
    ports = list()
    for port in os.listdir(conf.Discovery.base_path):
        if conf.Discovery.port_filter in port:
            ports.append(os.path.join(conf.Discovery.base_path, port))
    return ports


def probe_ports(ports: list) -> list:
    smart_meters = list()
    for port in ports:
        try:
            srl_adptr = SerialAdapter(port)
            mfr_id, sm_id = srl_adptr.identify()
            if mfr_id and sm_id:
                logger.info("found smart meter '{}' with id '{}' on '{}'".format(mfr_id, sm_id, port))
                smart_meters.append(("{}{}".format(conf.Discovery.device_id_prefix, sm_id), mfr_id, srl_adptr))
        except ReadError:
            pass
    return smart_meters


class Discovery(threading.Thread):
    def __init__(self, mqtt_client: MQTTClient):
        super().__init__(name="discovery", daemon=True)
        self.__device_pool: typing.Dict[str, Device] = dict()
        self.__mqtt_client = mqtt_client
        self.__refresh_flag = False
        self.__lock = threading.Lock()

    def __add_devices(self, smart_meters: typing.List[typing.Tuple[str, str, SerialAdapter]]):
        for sm_id, mfr_id, srl_adptr in smart_meters:
            try:
                if sm_id in self.__device_pool:
                    device = self.__device_pool[sm_id]
                else:
                    device = Device(id=sm_id, mfr_id=mfr_id)
                logger.info("found '{}' on '{}'".format(sm_id, srl_adptr.source))
                device.state = mgw_dc.dm.device_state.online
                self.__mqtt_client.publish(
                    topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                    payload=json.dumps(mgw_dc.dm.gen_set_device_msg(device)),
                    qos=1
                )
                device.adapter = srl_adptr
                if sm_id not in self.__device_pool:
                    self.__device_pool[sm_id] = device
                reader = Reader(device=device, mqtt_client=self.__mqtt_client)
                reader.start()
            except Exception as ex:
                logger.error("can't add '{}' - {}".format(sm_id, ex))

    def __clean_devices(self):
        for device in self.__device_pool.values():
            if not device.adapter:
                logger.info("removing '{}'".format(device.id))
                try:
                    self.__mqtt_client.publish(
                        topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                        payload=json.dumps(mgw_dc.dm.gen_delete_device_msg(device)),
                        qos=1
                    )
                    del self.__device_pool[device.id]
                except Exception as ex:
                    logger.error("can't remove '{}' - {}".format(device.id, ex))

    def run(self) -> None:
        if not self.__mqtt_client.connected():
            time.sleep(3)
        logger.info("starting {} ...".format(self.name))
        while True:
            if self.__refresh_flag:
                self.__refresh_devices()
            try:
                ports = get_ports()
                logger.debug("available ports: {}".format(ports))
                active_ports = [device.adapter.source for device in self.__device_pool.values() if device.adapter and type(device.adapter) is SerialAdapter]
                logger.debug("active ports {}".format(active_ports))
                inactive_ports = list(set(ports) - set(active_ports))
                logger.debug("inactive ports {}".format(inactive_ports))
                self.__add_devices(probe_ports(inactive_ports))
                self.__clean_devices()
            except Exception as ex:
                logger.error("discovery failed - {}".format(ex))
            time.sleep(conf.Discovery.delay)

    def __refresh_devices(self):
        with self.__lock:
            self.__refresh_flag = False
        for device in self.__device_pool.values():
            try:
                self.__mqtt_client.publish(
                    topic=mgw_dc.dm.gen_device_topic(conf.Client.id),
                    payload=json.dumps(mgw_dc.dm.gen_set_device_msg(device)),
                    qos=1
                )
            except Exception as ex:
                logger.error("setting device '{}' failed - {}".format(device.id, ex))

    def schedule_refresh(self):
        with self.__lock:
            self.__refresh_flag = True
