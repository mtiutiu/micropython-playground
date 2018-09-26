import ujson
import uhashlib
import ubinascii
import utime


def load_cfg(cfg_file):
    cfg_json = None
    with open(cfg_file, 'r') as cfg:
        cfg_json = ujson.load(cfg)
    return cfg_json


def check_file_hash(file):
    file_digest = None
    with open(file, 'r') as f:
        file_digest = uhashlib.sha1(f.read()).digest()
    return ubinascii.hexlify(file_digest)


def millis():
    return utime.ticks_ms()

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))
