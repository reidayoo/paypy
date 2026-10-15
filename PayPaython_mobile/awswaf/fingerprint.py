import json
import random
import time
import uuid
import os
from .crypto import encrypt

# AWSSolverのJS由来カスタムIEEE CRC
ALPHABET = "0123456789abcdef"
IEEE_POLYNOMIAL = 0xEDB88320

def _build_crc_table() -> list:
    table = []
    for i in range(256):
        v = i
        for _ in range(8):
            if v & 1:
                v = (v >> 1) ^ IEEE_POLYNOMIAL
            else:
                v >>= 1
        table.append(v)
    return table

_CRC_TABLE = _build_crc_table()

def _calculate_crc(data: str) -> int:
    v = 0 ^ 0xFFFFFFFF
    for char in data:
        idx = 255 & (v ^ ord(char))
        v = (v & 0xFFFFFFFF) >> 8 ^ _CRC_TABLE[idx]
    result = 0xFFFFFFFF ^ v
    if result >= 0x80000000:
        result -= 0x100000000
    return result

def _encode_number(n: int) -> str:
    n = n & 0xFFFFFFFF
    return (
        ALPHABET[(n >> 28) & 15]
        + ALPHABET[(n >> 24) & 15]
        + ALPHABET[(n >> 20) & 15]
        + ALPHABET[(n >> 16) & 15]
        + ALPHABET[(n >> 12) & 15]
        + ALPHABET[(n >> 8) & 15]
        + ALPHABET[(n >> 4) & 15]
        + ALPHABET[n & 15]
    ).upper()

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gpus = json.load(open(os.path.join(base_dir, "webgl.json")))

def get_fp(user_agent: str):
    ts = int(time.time() * 1000)
    gpu = random.choice(gpus)
    is_mobile = "Mobile" in user_agent or "Android" in user_agent

    bins = [random.randrange(0, 40) for _ in range(256)]
    bins[0], bins[-1] = random.randrange(14473, 16573), random.randrange(14473, 16573)

    fp = {
        "metrics": {
            "fp2": 1, "browser": 0, "capabilities": 1, "gpu": 7, "dnt": 0,
            "math": 0, "screen": 0, "navigator": 0, "auto": 1, "stealth": 0,
            "subtle": 0, "canvas": 5, "formdetector": 1, "be": 0
        },
        "start": ts,
        "flashVersion": None,
        "plugins": [
            {"name": "PDF Viewer",                "str": "PDF Viewer "},
            {"name": "Chrome PDF Viewer",         "str": "Chrome PDF Viewer "},
            {"name": "Chromium PDF Viewer",       "str": "Chromium PDF Viewer "},
            {"name": "Microsoft Edge PDF Viewer", "str": "Microsoft Edge PDF Viewer "},
            {"name": "WebKit built-in PDF",       "str": "WebKit built-in PDF "},
        ],
        "dupedPlugins": (
            "PDF Viewer Chrome PDF Viewer Chromium PDF Viewer "
            "Microsoft Edge PDF Viewer WebKit built-in PDF ||"
            + ("360-780-780-24-*-*-*" if is_mobile else "1920-1080-1032-24-*-*-*")
        ),
        "screenInfo": "360-780-780-24-*-*-*" if is_mobile else "1920-1080-1032-24-*-*-*",
        "referrer": "",
        "userAgent": user_agent,
        "location": "",
        "webDriver": False,
        "capabilities": {
            "css": {
                "textShadow": 1, "WebkitTextStroke": 1, "boxShadow": 1,
                "borderRadius": 1, "borderImage": 1, "opacity": 1,
                "transform": 1, "transition": 1,
            },
            "js": {
                "audio": True,
                "geolocation": random.choice([True, False]),
                "localStorage": "supported",
                "touch": is_mobile,
                "video": True,
                "webWorker": random.choice([True, False]),
            },
            "elapsed": 1,
        },
        "gpu": {
            "vendor": gpu["webgl"][0]["webgl_unmasked_vendor"],
            "model":  gpu["webgl_unmasked_renderer"],
            "extensions": gpu["webgl"][0]["webgl_extensions"].split(";"),
        },
        "dnt": None,
        "math": {
            "tan": "-1.4214488238747245",
            "sin": "0.8178819121159085",
            "cos": "-0.5753861119575491",
        },
        "automation": {
            "wd":      {"properties": {"document": [], "window": [], "navigator": []}},
            "phantom": {"properties": {"window": []}},
        },
        "stealth": {"t1": 0, "t2": 0, "i": 1, "mte": 0, "mtd": False},
        "crypto": {
            "crypto": 1, "subtle": 1,
            "encrypt": True, "decrypt": True, "wrapKey": True, "unwrapKey": True,
            "sign": True, "verify": True, "digest": True,
            "deriveBits": True, "deriveKey": True,
            "getRandomValues": True, "randomUUID": True,
        },
        "canvas": {
            "hash": random.randrange(645172295, 735192295),
            "emailHash": None,
            "histogramBins": bins,
        },
        "formDetected": False,
        "numForms": 0,
        "numFormElements": 0,
        "be": {"si": False},
        "end": ts + random.randint(1, 5),
        "errors": [],
        "version": "2.4.0",
        "id": str(uuid.uuid4()),
    }

    # AWSSolverと同じカスタムIEEE CRCでchecksum計算
    payload_str = json.dumps(fp, separators=(",", ":"))
    crc = _calculate_crc(payload_str)
    checksum = _encode_number(crc)
    encoded = f"{checksum}#{payload_str}"

    return checksum, encrypt(encoded.encode("utf-8"))
