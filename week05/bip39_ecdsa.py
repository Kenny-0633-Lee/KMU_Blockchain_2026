"""
week05/bip39_ecdsa.py
======================
5주차 — BIP-39 니모닉 + ECDSA + Bitcoin/Ethereum 주소 도출

학습 목표:
  - BIP-39: 니모닉(12단어) → Seed → 개인키 도출 원리
  - ECDSA secp256k1: 개인키 → 공개키 도출
  - Bitcoin 주소 생성: SHA-256 + RIPEMD-160 + Base58Check
  - Ethereum 주소 생성: Keccak-256 + 마지막 20바이트
  - HD Wallet 경로(BIP-44) 이해

실행:
  uv run python week05/bip39_ecdsa.py

⚠️  교육용 코드입니다. 생성된 니모닉으로 실제 자산을 보관하지 마세요.
"""

import hashlib
import hmac
import struct


# ── 라이브러리 임포트 (uv add ecdsa base58 mnemonic bip-utils)
try:
    import ecdsa
    import base58
    from mnemonic import Mnemonic
except ImportError as e:
    print(f"❌ 패키지 설치 필요: uv add ecdsa base58 mnemonic bip-utils")
    raise


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new("ripemd160")
    h.update(data)
    return h.digest()

def hash160(data: bytes) -> bytes:
    """SHA-256 → RIPEMD-160 (Bitcoin 주소 핵심)"""
    return ripemd160(sha256(data))

def keccak256(data: bytes) -> bytes:
    """Ethereum에서 사용하는 Keccak-256"""
    try:
        from Crypto.Hash import keccak
        k = keccak.new(digest_bits=256)
        k.update(data)
        return k.digest()
    except ImportError:
        # pycryptodome 없을 경우 경고
        print("  ℹ️  Keccak-256: pycryptodome 없어 sha3_256으로 대체 (실습용)")
        return hashlib.sha3_256(data).digest()

def print_separator(title: str = "") -> None:
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    else:
        print("=" * 60)


# ──────────────────────────────────────────────
# 1. BIP-39 니모닉 생성
# ──────────────────────────────────────────────

def step1_mnemonic() -> tuple[str, bytes]:
    print_separator("STEP 1: BIP-39 니모닉 생성")

    mnemo    = Mnemonic("english")
    words    = mnemo.generate(strength=128)   # 12단어
    seed     = mnemo.to_seed(words, passphrase="")

    print(f"📝 니모닉 (12단어):")
    word_list = words.split()
    for i, word in enumerate(word_list, 1):
        print(f"  {i:2d}. {word}")

    print(f"\n🌱 Seed (512비트):")
    print(f"  {seed.hex()[:64]}...")
    print(f"  (총 {len(seed) * 8}비트)")

    print(f"""
💡 BIP-39 원리:
  엔트로피(128비트 무작위) → 체크섬 추가 → 2048개 영단어 목록 매핑
  니모닉 → PBKDF2-SHA512(2048회 반복) → 512비트 Seed
  Seed → BIP-32 HD Wallet 루트 키 파생 시작점
""")

    return words, seed


# ──────────────────────────────────────────────
# 2. ECDSA secp256k1: 개인키 → 공개키
# ──────────────────────────────────────────────

def step2_keypair(seed: bytes) -> tuple[bytes, bytes]:
    print_separator("STEP 2: ECDSA secp256k1 키 쌍 생성")

    # 시드에서 개인키 도출 (실습용 간략 방식: HMAC-SHA512)
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    private_key_bytes = I[:32]   # 왼쪽 32바이트

    # ecdsa 라이브러리로 공개키 도출
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()

    # 압축 공개키 (33바이트: 02 or 03 + X 좌표)
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    prefix = b"\x02" if y % 2 == 0 else b"\x03"
    compressed_pubkey = prefix + x.to_bytes(32, "big")

    # 비압축 공개키 (65바이트: 04 + X + Y)
    uncompressed_pubkey = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")

    print(f"🔑 개인키 (Private Key):")
    print(f"  HEX: {private_key_bytes.hex()}")

    print(f"\n🔓 공개키 (Public Key):")
    print(f"  X 좌표: {x.to_bytes(32,'big').hex()}")
    print(f"  Y 좌표: {y.to_bytes(32,'big').hex()}")
    print(f"  압축  (33B): {compressed_pubkey.hex()}")
    print(f"  비압축(65B): {uncompressed_pubkey.hex()[:40]}...")

    print(f"""
💡 ECDSA secp256k1:
  y² = x³ + 7  (mod p)  — Bitcoin/Ethereum이 사용하는 타원 곡선
  개인키: 256비트 무작위 정수 k
  공개키: G × k  (G는 곡선의 생성점, 곱셈은 타원곡선 스칼라 곱)
  → 공개키에서 개인키를 역산하는 것은 이산 로그 문제 = 현실적으로 불가능
""")

    return private_key_bytes, compressed_pubkey


# ──────────────────────────────────────────────
# 3. Bitcoin 주소 생성
# ──────────────────────────────────────────────

def step3_bitcoin_address(private_key: bytes, pubkey: bytes) -> str:
    print_separator("STEP 3: Bitcoin 주소 생성 (P2PKH)")

    # 1. Hash160 = RIPEMD-160(SHA-256(pubkey))
    h160 = hash160(pubkey)
    print(f"① Hash160 = RIPEMD-160(SHA-256(pubkey))")
    print(f"  {h160.hex()}")

    # 2. 버전 바이트 추가 (0x00 = Mainnet P2PKH)
    versioned = b"\x00" + h160
    print(f"\n② 버전 바이트(0x00) 추가:")
    print(f"  {versioned.hex()}")

    # 3. 체크섬 (SHA-256 × 2 앞 4바이트)
    checksum = sha256(sha256(versioned))[:4]
    print(f"\n③ 체크섬 = SHA256(SHA256(versioned))[:4]:")
    print(f"  {checksum.hex()}")

    # 4. Base58Check 인코딩
    payload = versioned + checksum
    address = base58.b58encode(payload).decode("ascii")
    print(f"\n④ Base58Check 인코딩:")
    print(f"  Bitcoin 주소: {address}")

    # WIF (Wallet Import Format) 개인키
    wif_raw  = b"\x80" + private_key + b"\x01"   # 0x80=mainnet, 0x01=압축
    wif_check = sha256(sha256(wif_raw))[:4]
    wif = base58.b58encode(wif_raw + wif_check).decode("ascii")
    print(f"\n🔑 WIF 개인키 (Wallet Import Format):")
    print(f"  {wif}")

    print(f"""
💡 Bitcoin 주소 생성 과정:
  개인키(256비트) → 공개키(ECDSA) → Hash160(20바이트)
  → 버전+체크섬 추가 → Base58Check 인코딩 → 1로 시작하는 주소
""")

    return address


# ──────────────────────────────────────────────
# 4. Ethereum 주소 생성
# ──────────────────────────────────────────────

def step4_ethereum_address(private_key: bytes) -> str:
    print_separator("STEP 4: Ethereum 주소 생성")

    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    x  = vk.pubkey.point.x()
    y  = vk.pubkey.point.y()

    # 비압축 공개키의 64바이트 부분 (prefix 04 제거)
    pubkey_bytes = x.to_bytes(32, "big") + y.to_bytes(32, "big")

    # Keccak-256
    k256   = keccak256(pubkey_bytes)
    print(f"① Keccak-256(비압축 공개키 64바이트):")
    print(f"  {k256.hex()}")

    # 마지막 20바이트 → 주소
    eth_addr_bytes = k256[-20:]
    eth_addr = "0x" + eth_addr_bytes.hex()
    print(f"\n② 마지막 20바이트(40 hex chars) = Ethereum 주소:")
    print(f"  {eth_addr}")

    print(f"""
💡 Ethereum vs Bitcoin 주소 비교:
  Bitcoin : SHA-256 + RIPEMD-160 → Base58Check → "1..." 형식
  Ethereum: Keccak-256 → 마지막 20바이트 → "0x..." 형식
  
  둘 다 같은 ECDSA secp256k1 개인키에서 파생되지만 주소 형식이 다릅니다.
  같은 니모닉이라도 BIP-44 파생 경로가 다르면 다른 체인의 주소가 나옵니다.
""")

    return eth_addr


# ──────────────────────────────────────────────
# 5. 서명 & 검증 (ECDSA)
# ──────────────────────────────────────────────

def step5_sign_verify(private_key: bytes) -> None:
    print_separator("STEP 5: ECDSA 서명 생성 및 검증")

    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1,
                                      hashfunc=hashlib.sha256)
    vk = sk.get_verifying_key()

    message = b"Alice pays Bob 1 BTC"
    print(f"📨 메시지: '{message.decode()}'")

    # 서명
    signature = sk.sign(message)
    print(f"\n✍️  서명 (DER 형식, 71~72바이트):")
    print(f"  {signature.hex()[:60]}...")

    # 검증 — 정상
    try:
        vk.verify(signature, message)
        print(f"\n✅ 서명 검증 성공 (올바른 서명)")
    except ecdsa.BadSignatureError:
        print(f"\n❌ 서명 검증 실패")

    # 검증 — 변조된 메시지
    tampered = b"Alice pays Bob 999 BTC"
    try:
        vk.verify(signature, tampered)
        print(f"✅ 변조된 메시지 검증 성공 (위험!)")
    except ecdsa.BadSignatureError:
        print(f"🚨 변조된 메시지 검증 실패 → 위변조 감지! (정상 동작)")

    print(f"""
💡 트랜잭션 서명 원리:
  1. 발신자가 private_key로 tx_data에 서명 → signature 생성
  2. 노드는 public_key + signature + tx_data 로 서명 검증
  3. 검증 통과 → 발신자가 해당 주소의 소유자임을 증명
  4. private_key 없이는 유효한 서명 불가능 → 이중 지불 방지
""")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🔐 5주차 실습: BIP-39 + ECDSA + Bitcoin/Ethereum 주소 도출")
    print("⚠️  교육용 코드입니다. 생성된 니모닉으로 실제 자산을 보관하지 마세요.\n")

    words, seed                   = step1_mnemonic()
    private_key, compressed_pubkey = step2_keypair(seed)
    btc_address                   = step3_bitcoin_address(private_key, compressed_pubkey)
    eth_address                   = step4_ethereum_address(private_key)
    step5_sign_verify(private_key)

    print_separator("최종 요약")
    print(f"  니모닉   : {words[:40]}...")
    print(f"  Bitcoin  : {btc_address}")
    print(f"  Ethereum : {eth_address}")

    print("\n" + "=" * 60)
    print("✅ 실습 완료! 출력 결과 스크린샷 → LMS 제출")
    print("=" * 60)
