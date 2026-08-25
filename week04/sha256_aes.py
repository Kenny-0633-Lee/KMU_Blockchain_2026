"""
week04/sha256_aes.py
──────────────────────────────────────────────────────────────
4주차 실습: SHA-256 Avalanche Effect + AES-CBC 암호화
교재: Mastering Blockchain 4th Ed. — Ch.3 Symmetric Cryptography

학습 목표:
  1. SHA-256의 Avalanche Effect(눈사태 효과) 직접 확인
  2. 비트 단위 차이 분석으로 해시 함수 성질 이해
  3. AES-CBC 모드로 데이터 암호화/복호화 구현
  4. HMAC-SHA256으로 메시지 무결성 검증

실행:
  uv run python week04/sha256_aes.py
──────────────────────────────────────────────────────────────
"""

import hashlib
import hmac
import os
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


# ── 유틸리티 ─────────────────────────────────────────────────────────────────

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def count_bit_differences(hex1: str, hex2: str) -> int:
    """두 16진수 해시 사이의 비트 차이 수 계산"""
    b1 = int(hex1, 16)
    b2 = int(hex2, 16)
    xor = b1 ^ b2
    return bin(xor).count('1')

def hex_diff_visual(hex1: str, hex2: str, width: int = 32) -> str:
    """두 해시를 비교해 다른 문자에 '*' 마킹"""
    result = ""
    for c1, c2 in zip(hex1[:width], hex2[:width]):
        result += c1 if c1 == c2 else '*'
    return result + "…"


# ── PART 1: SHA-256 Avalanche Effect ─────────────────────────────────────────

def part1_avalanche():
    print("=" * 62)
    print("[PART 1] SHA-256 Avalanche Effect (눈사태 효과)")
    print("=" * 62)
    print("  입력이 단 1비트(글자 1개)만 달라져도 해시가 완전히 바뀝니다.")
    print()

    test_pairs = [
        ("Hello, Blockchain!", "Hello, Blockchain."),    # 마침표 차이
        ("blockchain", "Blockchain"),                     # 대소문자 차이
        ("password1", "password2"),                       # 숫자 1자 차이
    ]

    for msg1, msg2 in test_pairs:
        h1 = sha256_hex(msg1)
        h2 = sha256_hex(msg2)
        bit_diff = count_bit_differences(h1, h2)
        diff_ratio = bit_diff / 256 * 100

        print(f"  입력1: {msg1!r:30s}  →  {h1[:20]}…")
        print(f"  입력2: {msg2!r:30s}  →  {h2[:20]}…")
        print(f"  차이:  {hex_diff_visual(h1, h2)}")
        print(f"  비트 차이: {bit_diff}/256 ({diff_ratio:.1f}%)  ← 이상적: ~50%")
        print(f"  해시 일치: {'예' if h1 == h2 else '아니오'}")
        print()


# ── PART 2: 해시 함수 단방향성 확인 ──────────────────────────────────────────

def part2_one_way():
    print("=" * 62)
    print("[PART 2] 해시 함수 단방향성 — 역산 불가 시뮬레이션")
    print("=" * 62)

    target_hash = sha256_hex("blockchain")
    print(f"  목표 해시 (역산 대상): {target_hash}")
    print(f"  (원본: 'blockchain')")
    print()
    print("  무작위 입력으로 목표 해시를 찾으려는 시도 (최대 100,000회):")

    attempts = 0
    found = False
    start = time.time()

    for i in range(100_000):
        attempts += 1
        candidate = os.urandom(8).hex()   # 무작위 16자 16진수 문자열
        if sha256_hex(candidate) == target_hash:
            found = True
            print(f"  우연히 발견! (거의 불가능): {candidate}")
            break

    elapsed = time.time() - start
    print(f"  시도 횟수: {attempts:,}회 | 소요 시간: {elapsed:.2f}초")
    print(f"  결과: {'발견됨' if found else '❌ 발견 실패 — 단방향성 확인'}")
    print()
    print("  💡 실제 Bitcoin: 64자리(256비트) 해시를 역산하려면")
    print("     우주 나이보다 오랜 시간이 필요합니다.")
    print()


# ── PART 3: AES-CBC 암호화/복호화 ────────────────────────────────────────────

def part3_aes_cbc():
    print("=" * 62)
    print("[PART 3] AES-CBC 암호화/복호화")
    print("=" * 62)

    # 키(32바이트=256비트)와 IV(16바이트) 랜덤 생성
    key = os.urandom(32)     # AES-256
    iv  = os.urandom(16)     # CBC 초기 벡터

    plaintexts = [
        b"Alice -> Bob: 0.5 BTC at block 830000",
        b"Secret transaction data #12345678",
    ]

    print(f"  AES-256-CBC 키  (32byte): {key.hex()[:32]}…")
    print(f"  초기 벡터 IV   (16byte): {iv.hex()}")
    print()

    for plaintext in plaintexts:
        # 패딩 (PKCS7, 블록 크기 128비트=16바이트)
        padder     = padding.PKCS7(128).padder()
        padded     = padder.update(plaintext) + padder.finalize()

        # 암호화
        cipher     = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor  = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        # 복호화
        decryptor        = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder         = padding.PKCS7(128).unpadder()
        decrypted        = unpadder.update(decrypted_padded) + unpadder.finalize()

        print(f"  평문  : {plaintext.decode()}")
        print(f"  암호문: {ciphertext.hex()[:40]}…  ({len(ciphertext)}바이트)")
        print(f"  복호화: {decrypted.decode()}")
        print(f"  일치  : {'✅' if plaintext == decrypted else '❌'}")
        print()

    # IV 변경 시 암호문이 완전히 달라지는 것 확인
    print("  [CBC 모드: IV가 다르면 같은 평문도 다른 암호문 생성]")
    msg = b"same plaintext"
    padder = padding.PKCS7(128).padder()
    padded = padder.update(msg) + padder.finalize()

    iv1 = os.urandom(16)
    iv2 = os.urandom(16)

    ct1 = Cipher(algorithms.AES(key), modes.CBC(iv1), backend=default_backend()).encryptor()
    ct2 = Cipher(algorithms.AES(key), modes.CBC(iv2), backend=default_backend()).encryptor()

    enc1 = (ct1.update(padded) + ct1.finalize()).hex()
    enc2 = (ct2.update(padded) + ct2.finalize()).hex()

    print(f"  평문     : {msg.decode()!r}")
    print(f"  암호문1  : {enc1[:32]}… (IV1 사용)")
    print(f"  암호문2  : {enc2[:32]}… (IV2 사용)")
    print(f"  일치 여부: {'같음' if enc1 == enc2 else '❌ 다름 (IV가 달라도 키가 같으면 복호화 가능)'}")
    print()


# ── PART 4: HMAC-SHA256 (메시지 무결성) ──────────────────────────────────────

def part4_hmac():
    print("=" * 62)
    print("[PART 4] HMAC-SHA256 — 메시지 인증 코드 (MAC)")
    print("=" * 62)
    print("  HMAC = 공유 비밀키 + SHA-256 → 메시지 무결성 + 출처 인증")
    print()

    secret_key = b"shared_secret_between_Alice_and_Bob"
    message    = b"Transfer 100 KNUT to Carol"

    mac = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
    print(f"  메시지 : {message.decode()}")
    print(f"  HMAC   : {mac}")
    print()

    # 변조된 메시지로 검증 실패 확인
    tampered_message = b"Transfer 10000 KNUT to Carol"
    tampered_mac     = hmac.new(secret_key, tampered_message, hashlib.sha256).hexdigest()

    print(f"  변조 메시지: {tampered_message.decode()}")
    print(f"  변조 HMAC  : {tampered_mac}")
    print(f"  원본 HMAC과 일치: {'예' if mac == tampered_mac else '❌ 아니오 — 변조 감지'}")
    print()

    # 잘못된 키로 검증 시도
    wrong_key = b"wrong_key"
    wrong_mac = hmac.new(wrong_key, message, hashlib.sha256).hexdigest()
    print(f"  잘못된 키로 생성한 HMAC: {wrong_mac[:32]}…")
    print(f"  원본 HMAC과 일치: {'예' if mac == wrong_mac else '❌ 아니오 — 키 불일치 감지'}")
    print()


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    part1_avalanche()
    part2_one_way()
    part3_aes_cbc()
    part4_hmac()

    print("=" * 62)
    print("  ✅ 4주차 실습 완료")
    print("  핵심 요약:")
    print("  - 해시 함수: 단방향, Avalanche Effect, 충돌저항")
    print("  - AES-CBC: 대칭키 블록 암호화 (키+IV 필요)")
    print("  - HMAC: 공유키 기반 메시지 무결성 검증")
    print("=" * 62)


if __name__ == "__main__":
    main()
