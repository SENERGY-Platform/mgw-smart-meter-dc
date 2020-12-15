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


__all__ = ("SerialAdapter", "ReadError", "IdentError", "DataError")


from util import get_logger
import time
import serial


logger = get_logger(__name__.split(".", 1)[-1])


class ReadError(Exception):
    pass


class IdentError(ReadError):
    pass


class DataError(ReadError):
    pass


def parse_data_telegram(data):
    readings = dict()
    readings_list = data.split('\r\n')
    for reading in readings_list:
        if '(' in reading:
            key, value = reading.split('(')
            if '*' in value:
                value, unit = value.split('*')
                unit = unit.replace(')', '')
            else:
                value = value.replace(')', '')
                unit = None
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            readings[key] = (value, unit)
    return readings


class SerialAdapter:
    init_telegram = '\x2f\x3f\x21\x0d\x0a'.encode()     # '/?! CR LF'
    ack_telegram = '\x06\x30\x35\x30\x0d\x0a'.encode()  # 'ACK 050 CR LF'

    def __init__(self, port):
        self.source = port
        self.__serial_con = serial.Serial()
        self.__serial_con.port = self.source
        self.__serial_con.parity = serial.PARITY_EVEN
        self.__serial_con.stopbits = serial.STOPBITS_ONE
        self.__serial_con.bytesize = serial.SEVENBITS
        self.__serial_con.timeout = 1

    def __read(self):
        try:
            self.__serial_con.baudrate = 300

            # open serial port
            self.__serial_con.open()

            # write initial telegram
            self.__serial_con.write(SerialAdapter.init_telegram)

            # read identification telegram
            ident_telegram = self.__serial_con.readall()
            if not ident_telegram:
                logger.error("missing identification telegram on '{}'".format(self.__serial_con.port))
                self.__serial_con.close()
                raise IdentError
            logger.debug(ident_telegram)

            # write acknowledgement telegram
            self.__serial_con.write(SerialAdapter.ack_telegram)

            # change baudrate
            time.sleep(0.5)
            self.__serial_con.baudrate = 9600

            # read data telegram
            data_telegram = self.__serial_con.readall()
            if not data_telegram or len(data_telegram.decode()) < 20:
                logger.error("missing or malformed data telegram on '{}'".format(self.__serial_con.port))
                self.__serial_con.close()
                raise DataError
            logger.debug(data_telegram)

            # close serial port
            self.__serial_con.close()

            return ident_telegram.decode(), data_telegram.decode()
        except IOError as ex:
            logger.error(ex)
            raise ReadError

    def read(self):
        _, dt = self.__read()
        return parse_data_telegram(dt)

    def identify(self):
        mfr_id, dt = self.__read()
        mfr_id = mfr_id.replace("\r", "")
        mfr_id = mfr_id.replace("\n", "")
        mfr_id = mfr_id.replace("!", "")
        mfr_id = mfr_id.replace("?", "")
        mfr_id = mfr_id.replace("/", "")
        mfr_id = mfr_id.split(".")
        if type(mfr_id) is list:
            mfr_id = mfr_id[0]
        dt = parse_data_telegram(dt)
        meter_ids = list()
        for key, val in dt.items():
            if key in ("C.1.0", "C.1.1", "0.0") and not str(val[0]).isspace() and not str(val[0]) in meter_ids:
                meter_ids.append(str(val[0]))
        meter_ids.sort()
        return mfr_id, "".join(meter_ids)
