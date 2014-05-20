from fabric.api import env
env.use_ssh_config = True

env.roledefs = {
    'server': ['rview@q0'],
    'client': ['pi@ry']
}

import server
import client
