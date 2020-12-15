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


__all__ = ("Device", )


from util import conf
from .serial_adapter import SerialAdapter
import typing
import mgw_dc


LGZxZMF100AC = ("Landis+Gyr E350 ({})", conf.Senergy.dt_landis_gyr_E350)


class Device(mgw_dc.dm.Device):
    __type_map = {
        "LGZ0ZMF100AC": LGZxZMF100AC,
        "LGZ1ZMF100AC": LGZxZMF100AC,
        "LGZ2ZMF100AC": LGZxZMF100AC,
        "LGZ3ZMF100AC": LGZxZMF100AC,
        "LGZ4ZMF100AC": LGZxZMF100AC
    }

    def __init__(self, id: str, mfr_id: str):
        super().__init__(
            id,
            Device.__type_map[mfr_id][0].format(id.replace(conf.Discovery.device_id_prefix, "")),
            Device.__type_map[mfr_id][1]
        )
        self.adapter: typing.Optional[SerialAdapter] = None
