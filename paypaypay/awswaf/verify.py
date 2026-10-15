import hashlib
import base64
import itertools
from typing import Callable, Any


def _check_pow(difficulty: int, hex_hash: str) -> bool:
    """AWSSolverと同じ判定: 上位difficultyビットが0かチェック"""
    return int(hex_hash, 16) >> (len(hex_hash) * 4 - difficulty) == 0


def _check_scrypt(digest: bytes, difficulty: int) -> bool:
    """バイト列チェック"""
    full, rem = divmod(difficulty, 8)
    if digest[:full] != b"\x00" * full:
        return False
    if rem and (digest[full] >> (8 - rem)):
        return False
    return True


def compute_scrypt_nonce(challenge_input: str, checksum: str, difficulty: int) -> str:
    """AWSSolverのcompute_scryptに合わせた実装"""
    salt = checksum.encode("utf-8")
    for nonce in itertools.count(0):
        password = (challenge_input + checksum + str(nonce)).encode("utf-8")
        hash_hex = hashlib.scrypt(password, salt=salt, n=128, r=8, p=1, dklen=16).hex()
        if _check_pow(difficulty, hash_hex):
            return str(nonce)


def hash_pow(challenge_input: str, checksum: str, difficulty: int) -> str:
    """AWSSolverのcompute_powに合わせた実装"""
    base = challenge_input + checksum
    nonce = 0
    while True:
        data = (base + str(nonce)).encode("utf-8")
        hash_bytes = hashlib.sha256(data).digest()
        # uint32のビッグエンディアン連結
        parts = []
        for i in range(0, len(hash_bytes), 4):
            uint32 = int.from_bytes(hash_bytes[i:i+4], byteorder="big")
            parts.append(f"{uint32:08x}")
        hash_hex = "".join(parts)
        if _check_pow(difficulty, hash_hex):
            return str(nonce)
        nonce += 1


def get_filter_bytes(difficulty: int) -> int:
    sizes = {
        1: 1024,
        2: 10 * 1024,
        3: 100 * 1024,
        4: 1 * 1048576,
        5: 10 * 1048576,
    }
    return sizes.get(difficulty, 0)


def network_bandwidth(challenge_input: str, checksum: str, difficulty: int) -> str:
    """
    NetworkBandwidth (mp_verify) チャレンジ:
    difficultyに応じたサイズのnullバイト列をbase64エンコードして返す
    """
    n = get_filter_bytes(difficulty)
    return base64.b64encode(bytes(n)).decode("utf-8")


BANDWIDTH_CHALLENGE = "ha9faaffd31b4d5ede2a2e19d2d7fd525f66fee61911511960dcbb52d3c48ce25"

CHALLENGE_TYPES: dict[str, Callable[[Any, Any, Any], str]] = {
    "h72f957df656e80ba55f5d8ce2e8c7ccb59687dba3bfb273d54b08a261b2f3002": compute_scrypt_nonce,
    "h7b0c470f0cfe3a80a9e26526ad185f484f6817d0832712a4a37a908786a6a67f": hash_pow,
    BANDWIDTH_CHALLENGE: network_bandwidth,
}
