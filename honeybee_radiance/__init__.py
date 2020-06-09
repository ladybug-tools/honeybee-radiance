"""honeybee-radiance library."""

from honeybee.logutil import get_logger

# use the same logger settings across honeybee extensions
# this does NOT mean that the logs will be written to the same file but they will have
# the same formatting, level, etc.
logger = get_logger(name=__name__)

# load all functions that extends honeybee core library
import honeybee_radiance._extend_honeybee
