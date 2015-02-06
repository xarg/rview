from fabric.api import env
env.use_ssh_config = True

env.roledefs = {
    'server': ['rview@q0'],
    'client': ["pi@raspberrypi.caserne", ]
}

import server
import client
