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

__all__ = ("conf",)


import simple_env_var


@simple_env_var.configuration
class Conf:

    @simple_env_var.section
    class MsgBroker:
        host = "message-broker"
        port = 1883

    @simple_env_var.section
    class Logger:
        level = "info"
        enable_mqtt = False

    @simple_env_var.section
    class Client:
        clean_session = False
        keep_alive = 10
        id = "smart-meter-dc"

    @simple_env_var.section
    class Discovery:
        device_id_prefix = None
        base_path = "/dev"
        port_filter = None
        full_path = None
        delay = 15

    @simple_env_var.section
    class StartDelay:
        enabled = False
        min = 5
        max = 20

    @simple_env_var.section
    class Senergy:
        dt_LGZxZMF100AC = None


conf = Conf()


if not all((conf.Discovery.port_filter, )):
    exit('Please provide port filter')

if not all((conf.Senergy.dt_LGZxZMF100AC,)):
    exit('Please provide SENERGY device types')
