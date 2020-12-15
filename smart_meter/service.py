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


from util import get_logger
import datetime


logger = get_logger(__name__.split(".", 1)[-1])


def get_meas_lgzxzmf100ac(data: dict):
    return {
        "OBIS_1_8_0": {
            "value": float(data["1.8.0"][0]),
            "unit": data["1.8.0"][1]
        },
        "OBIS_16_7": {
            "value": float(data["16.7"][0]),
            "unit": data["16.7"][1]
        },
        "time": '{}Z'.format(datetime.datetime.utcnow().isoformat())
    }
