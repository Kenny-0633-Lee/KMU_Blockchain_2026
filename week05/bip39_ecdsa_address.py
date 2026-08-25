"""
week05/bip39_ecdsa_address.py
──────────────────────────────────────────────────────────────
5주차 실습: BIP-39 Mnemonic → ECDSA → Bitcoin/Ethereum 주소 도출
교재: Mastering Blockchain 4th Ed. — Ch.4 Asymmetric Cryptography

학습 목표:
  1. BIP-39 니모닉(12단어) 생성 및 시드 도출
  2. secp256k1 타원곡선으로 ECDSA 키쌍 생성
  3. 공개키 → Bitcoin Testnet 주소 변환 과정 이해
  4. ECDSA 서명 생성 및 검증
  5. Ethereum 주소 도출 (Keccak-256 방식)

실행:
  uv run python week05/bip39_ecdsa_address.py
──────────────────────────────────────────────────────────────
"""

import hashlib
import hmac
import os
import struct

import base58
import ecdsa
from mnemonic import Mnemonic


# ── 헬퍼 함수 ─────────────────────────────────────────────────────────────────

def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(pubkey: bytes) -> bytes:
    """공개키 → SHA-256 → RIPEMD-160"""
    return ripemd160(hashlib.sha256(pubkey).digest())

def keccak256(data: bytes) -> bytes:
    """Ethereum 주소 도출에 사용 (pysha3 없으면 sha3_256 근사)"""
    try:
        import sha3  # pysha3
        k = hashlib.new('keccak_256')
        k.update(data)
        return k.digest()
    except Exception:
        # pysha3 없을 때 표준 SHA3-256으로 대체 (교육용)
        return hashlib.sha3_256(data).digest()


# ── PART 1: BIP-39 니모닉 생성 ──────────────────────────────────────────────

def part1_mnemonic() -> tuple[str, bytes]:
    print("=" * 64)
    print("[PART 1] BIP-39 니모닉 생성")
    print("=" * 64)
    print("  엔트로피(랜덤 128비트) → 체크섬 추가 → 2048 단어 사전에서 12단어 선택")
    print()

    mnemo    = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128)   # 128비트 → 12단어
    seed     = mnemo.to_seed(mnemonic)        # PBKDF2-HMAC-SHA512, 2048회 반복

    words = mnemonic.split()
    print(f"  니모닉 ({len(words)}단어):")
    for i, word in enumerate(words, 1):
        print(f"    {i:2d}. {word}")

    print()
    print(f"  시드 (512비트 = 64바이트):")
    print(f"    {seed.hex()[:48]}…")
    print(f"    (앞 24자만 표시)")
    print()
    print("  ⚠️  이 니모닉은 실습용으로 랜덤 생성된 것입니다.")
    print("      실제 지갑에는 절대 사용하지 마세요.")
    print()

    return mnemonic, seed


# ── PART 2: ECDSA 키쌍 생성 ──────────────────────────────────────────────────

def part2_ecdsa_keypair(seed: bytes) -> tuple[ecdsa.SigningKey, ecdsa.VerifyingKey]:
    print("=" * 64)
    print("[PART 2] secp256k1 ECDSA 키쌍 생성")
    print("=" * 64)
    print("  시드 앞 32바이트를 개인키로 사용 (교육용 단순화 구현)")
    print("  실제 HD Wallet은 BIP-32 계층적 파생 경로를 사용합니다.")
    print()

    private_key_bytes = seed[:32]
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()

    # 비압축 공개키 (04 + x좌표 + y좌표, 65바이트)
    uncompressed_pubkey = b'\x04' + vk.to_string()

    # 압축 공개키 (02 또는 03 + x좌표, 33바이트)
    x = vk.to_string()[:32]
    y = vk.to_string()[32:]
    prefix = b'\x02' if y[-1] % 2 == 0 else b'\x03'
    compressed_pubkey = prefix + x

    print(f"  개인키 (32바이트 = 256비트):")
    print(f"    {private_key_bytes.hex()}")
    print()
    print(f"  공개키 (비압축, 65바이트):")
    print(f"    04 {vk.to_string()[:32].hex()}")
    print(f"       {vk.to_string()[32:].hex()}")
    print()
    print(f"  공개키 (압축, 33바이트):")
    print(f"    {compressed_pubkey.hex()}")
    print()

    return sk, vk


# ── PART 3: Bitcoin Testnet 주소 도출 ─────────────────────────────────────────

def part3_bitcoin_address(vk: ecdsa.VerifyingKey) -> str:
    print("=" * 64)
    print("[PART 3] 공개키 → Bitcoin Testnet 주소 변환")
    print("=" * 64)
    print("  공개키 → SHA-256 → RIPEMD-160 → Base58Check 인코딩")
    print()

    # 비압축 공개키
    pubkey = b'\x04' + vk.to_string()

    # STEP 1: SHA-256
    step1 = hashlib.sha256(pubkey).digest()
    print(f"  STEP 1 | SHA-256(공개키)      : {step1.hex()[:32]}…")

    # STEP 2: RIPEMD-160
    step2 = ripemd160(step1)
    print(f"  STEP 2 | RIPEMD-160(step1)    : {step2.hex()}")

    # STEP 3: 버전 바이트 추가 (0x6F = Testnet, 0x00 = Mainnet)
    version = b'\x6f'   # Testnet prefix
    step3 = version + step2
    print(f"  STEP 3 | 버전+해시(Testnet=6F): {step3.hex()}")

    # STEP 4: 체크섬 (이중 SHA-256의 앞 4바이트)
    checksum = sha256d(step3)[:4]
    print(f"  STEP 4 | 체크섬 (4바이트)     : {checksum.hex()}")

    # STEP 5: Base58Check 인코딩
    payload = step3 + checksum
    address = base58.b58encode(payload).decode()
    print(f"  STEP 5 | Base58Check 인코딩")
    print()
    print(f"  ✅ Bitcoin Testnet 주소: {address}")
    print(f"     (m 또는 n으로 시작하면 정상)")
    print()

    return address


# ── PART 4: Ethereum 주소 도출 ────────────────────────────────────────────────

def part4_ethereum_address(vk: ecdsa.VerifyingKey) -> str:
    print("=" * 64)
    print("[PART 4] 공개키 → Ethereum 주소 변환")
    print("=" * 64)
    print("  비압축 공개키(64바이트) → Keccak-256 → 마지막 20바이트 → 0x 접두사")
    print()

    # 비압축 공개키에서 04 접두사 제외한 64바이트
    pubkey_bytes = vk.to_string()   # 64바이트 (x+y)

    keccak_hash = keccak256(pubkey_bytes)
    eth_address = "0x" + keccak_hash[-20:].hex()

    print(f"  공개키 (64바이트): {pubkey_bytes.hex()[:32]}…")
    print(f"  Keccak-256       : {keccak_hash.hex()}")
    print(f"  마지막 20바이트  : {keccak_hash[-20:].hex()}")
    print()
    print(f"  ✅ Ethereum 주소: {eth_address}")
    print()
    print("  📌 Bitcoin과 Ethereum의 주소 도출 차이:")
    print("     Bitcoin  : SHA256 → RIPEMD160 → Base58Check")
    print("     Ethereum : Keccak-256 → 마지막 20바이트 → 16진수")
    print()

    return eth_address


# ── PART 5: ECDSA 서명 & 검증 ────────────────────────────────────────────────

def part5_ecdsa_signature(sk: ecdsa.SigningKey, vk: ecdsa.VerifyingKey):
    print("=" * 64)
    print("[PART 5] ECDSA 서명 생성 및 검증")
    print("=" * 64)

    message = b"Alice sends 0.01 BTC to Bob at block 830000"
    msg_hash = hashlib.sha256(message).digest()

    # 서명 생성 (개인키 사용)
    signature = sk.sign(message)

    print(f"  메시지  : {message.decode()}")
    print(f"  메시지 해시 : {msg_hash.hex()[:32]}…")
    print(f"  서명 (DER): {signature.hex()[:48]}…  ({len(signature)}바이트)")
    print()

    # 정상 검증
    try:
        vk.verify(signature, message)
        print(f"  정상 서명 검증: ✅ 유효")
    except ecdsa.BadSignatureError:
        print(f"  정상 서명 검증: ❌ 실패")

    # 변조된 메시지 검증
    tampered = b"Alice sends 999.0 BTC to Bob at block 830000"
    try:
        vk.verify(signature, tampered)
        print(f"  변조 메시지 검증: ✅ 유효 (이상 없음)")
    except ecdsa.BadSignatureError:
        print(f"  변조 메시지 검증: ❌ 실패 — 변조 감지 성공")

    # 다른 키로 검증
    fake_sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    fake_vk = fake_sk.get_verifying_key()
    try:
        fake_vk.verify(signature, message)
        print(f"  잘못된 공개키 검증: ✅ 유효")
    except ecdsa.BadSignatureError:
        print(f"  잘못된 공개키 검증: ❌ 실패 — 키 불일치 감지")

    print()
    print("  📌 ECDSA의 핵심:")
    print("     - 서명은 개인키로 생성, 검증은 공개키로 수행")
    print("     - 개인키 없이는 유효한 서명 위조 불가능")
    print("     - 메시지 1비트 변조도 서명 검증 실패")
    print()


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 64)
    print("  5주차 실습: BIP-39 → ECDSA → Bitcoin/Ethereum 주소 도출")
    print("=" * 64)
    print()

    mnemonic, seed = part1_mnemonic()
    sk, vk         = part2_ecdsa_keypair(seed)
    btc_address    = part3_bitcoin_address(vk)
    eth_address    = part4_ethereum_address(vk)
    part5_ecdsa_signature(sk, vk)

    print("=" * 64)
    print("  ✅ 5주차 실습 완료 — 결과 요약")
    print("=" * 64)
    print(f"  니모닉 첫 3단어 : {' '.join(mnemonic.split()[:3])} …")
    print(f"  Bitcoin Testnet : {btc_address}")
    print(f"  Ethereum        : {eth_address}")
    print()
    print("  💡 같은 니모닉으로 Bitcoin 주소와 Ethereum 주소를")
    print("     동시에 생성할 수 있습니다 — 이것이 HD Wallet의 힘입니다.")
    print("=" * 64)


if __name__ == "__main__":
    main()
