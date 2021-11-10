
import os
from environs import Env

env = Env()
env.read_env()

SERVICES_DIRECTORY = env.str("LOGAGG_SERVICES_DIRECTORY", "/var/log/services")

try:
    os.makedirs(SERVICES_DIRECTORY)
except FileExistsError:
    pass
