"""
改善版暗号化モジュール

動的な鍵抽出機能を統合した暗号化処理
"""

import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ロガー設定
logger = logging.getLogger(__name__)

from dynamic_key_extractor import get_encryption_key

# デフォルト鍵（フォールバック用）
DEFAULT_KEY = bytes.fromhex("6f71a512b1e035eaab53d8be73120d3fb68a0ca346b9560aab3e5cdf753d5e98")

# グローバルな鍵とAESGCMインスタンス
_current_key = DEFAULT_KEY
_aesgcm = AESGCM(_current_key)


def set_encryption_key(key: bytes):
    """
    暗号化鍵を設定
    
    Args:
        key: 新しい暗号化鍵
    """
    global _current_key, _aesgcm
    _current_key = key
    _aesgcm = AESGCM(key)


def update_key_from_endpoint(endpoint: str):
    """
    エンドポイントから鍵を動的に取得して更新
    
    Args:
        endpoint: AWS WAFのエンドポイント
    """
    try:
        key = get_encryption_key(endpoint)
        set_encryption_key(key)
        logger.info("暗号化鍵を更新しました")
    except Exception as e:
        logger.warning(f"鍵の更新に失敗、デフォルト鍵を使用: {e}")


def encrypt(plaintext: bytes) -> str:
    """
    データを暗号化
    
    Args:
        plaintext: 平文データ
        
    Returns:
        暗号化されたデータ（文字列形式）
        フォーマット: base64(iv)::tag_hex::ciphertext_hex
    """
    iv = os.urandom(12)
    
    cipher_bytes = _aesgcm.encrypt(iv, plaintext, None)
    tag = cipher_bytes[-16:]
    ciphertext = cipher_bytes[:-16]
    
    iv_b64 = base64.b64encode(iv).decode('utf-8')
    
    # ブラウザの実装: iv_base64::tag_hex::ciphertext_hex
    # identifierは signals の name フィールド ("Zoey") に入る
    return f"{iv_b64}::{tag.hex()}::{ciphertext.hex()}"


def decrypt(encrypted: str) -> bytes:
    """
    データを復号化
    
    Args:
        encrypted: 暗号化されたデータ
        
    Returns:
        復号化されたデータ
    """
    parts = encrypted.split("::")
    # フォーマット: iv_b64::tag_hex::ct_hex (3パート)
    if len(parts) == 3:
        iv_b64, tag_hex, ct_hex = parts
    # Zoey::iv_b64::tag_hex::ct_hex (4パート - 後方互換)
    elif len(parts) == 4:
        _, iv_b64, tag_hex, ct_hex = parts
    else:
        raise ValueError(f"Invalid encrypted format: {len(parts)} parts")

    iv = base64.b64decode(iv_b64)
    tag = bytes.fromhex(tag_hex)
    ciphertext = bytes.fromhex(ct_hex)

    return _aesgcm.decrypt(iv, ciphertext + tag, None)


if __name__ == "__main__":
    # テスト
    print("改善版暗号化モジュールのテスト")
    
    plaintext = b"test data"
    encrypted = encrypt(plaintext)
    print(f"暗号化: {encrypted[:50]}...")
    
    decrypted = decrypt(encrypted)
    print(f"復号化: {decrypted}")
    
    assert plaintext == decrypted, "暗号化/復号化が正しく動作していません"
    print("テスト完了")
