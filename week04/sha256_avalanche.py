"""
week04/sha256_avalanche.py
==========================
4주차 — SHA-256 & 해시 함수 특성 실험

학습 목표:
  - SHA-256 해시 함수의 5가지 특성 실험
  - 눈사태 효과(Avalanche Effect): 입력 1비트 변화 → 출력 50% 비트 변화
  - 해시 함수의 단방향성(One-way) 체험
  - 간단한 Dictionary Attack 시뮬레이션

실행:
  uv run python week04/sha256_avalanche.py
"""

import hashlib
import time


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hex_to_bin(hex_str: str) -> str:
    """16진수 해시를 2진수 문자열로 변환"""
    return bin(int(hex_str, 16))[2:].zfill(256)


def bit_diff(hash1: str, hash2: str) -> tuple[int, float]:
    """두 해시(hex) 간 비트 차이 수와 비율 반환"""
    b1 = hex_to_bin(hash1)
    b2 = hex_to_bin(hash2)
    diff = sum(c1 != c2 for c1, c2 in zip(b1, b2))
    return diff, diff / 256 * 100


def print_separator(title: str = "") -> None:
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    else:
        print("=" * 60)


# ──────────────────────────────────────────────
# 실험 1: SHA-256 기본 동작
# ──────────────────────────────────────────────

def exp1_basic():
    print_separator("실험 1: SHA-256 기본 동작 및 결정론적 특성")

    inputs = ["blockchain", "Blockchain", "blockchain!", "", "계명대학교"]
    print(f"\n{'입력':20s} | SHA-256 해시")
    print("-" * 70)
    for text in inputs:
        h = sha256(text)
        label = f'"{text}"' if text else "(빈 문자열)"
        print(f"  {label:20s} | {h}")

    print("\n💡 관찰:")
    print("  - 대소문자 한 글자 차이만으로도 해시가 완전히 달라집니다.")
    print("  - 같은 입력은 언제나 같은 출력 (결정론적)")
    print("  - 빈 문자열도 항상 같은 해시를 가집니다.")


# ──────────────────────────────────────────────
# 실험 2: 눈사태 효과 (Avalanche Effect)
# ──────────────────────────────────────────────

def exp2_avalanche():
    print_separator("실험 2: 눈사태 효과 (Avalanche Effect)")

    base = "blockchain"
    base_hash = sha256(base)

    print(f"\n기준 입력: '{base}'")
    print(f"기준 해시: {base_hash}")

    variants = [
        ("Blockchain",    "첫 글자 대문자화"),
        ("blockchain!",   "끝에 '!' 추가"),
        ("blockchain1",   "끝에 '1' 추가"),
        ("blockchain ",   "끝에 공백 추가"),
        ("blockchaid",    "한 글자 변경 (n→d)"),
        ("blcokchain",    "두 글자 순서 변경"),
    ]

    print(f"\n{'변형 입력':20s} | {'변경 설명':22s} | 비트차이 | 변화율")
    print("-" * 80)

    total_diff = 0
    for variant, desc in variants:
        h = sha256(variant)
        diff, pct = bit_diff(base_hash, h)
        total_diff += pct
        print(f"  {variant:20s} | {desc:22s} | {diff:3d}비트  | {pct:.1f}%")

    avg = total_diff / len(variants)
    print(f"\n  평균 변화율: {avg:.1f}%  (이상적 눈사태 효과 = 50%)")
    print("\n💡 결론: 입력이 조금만 달라져도 출력의 절반 정도가 바뀝니다.")
    print("   이것이 블록체인에서 한 블록을 수정하면 이후 전체가 무너지는 이유입니다.")


# ──────────────────────────────────────────────
# 실험 3: 단방향성 (One-way) 시뮬레이션
# ──────────────────────────────────────────────

def exp3_one_way():
    print_separator("실험 3: 단방향성 — 무차별 대입의 비현실성")

    target_hash = sha256("abc")
    print(f"\n목표 해시: {target_hash}")
    print("목표 원문: 3글자 소문자 조합 중 하나")
    print("\n무작위 3글자 조합 1,000개 시도 중...")

    import random
    import string

    chars   = string.ascii_lowercase
    found   = False
    start   = time.time()

    for attempt in range(1000):
        guess  = "".join(random.choices(chars, k=3))
        g_hash = sha256(guess)
        if g_hash == target_hash:
            elapsed = time.time() - start
            print(f"✅ 우연히 발견! '{guess}' (시도 {attempt+1}회, {elapsed:.3f}초)")
            found = True
            break

    if not found:
        elapsed = time.time() - start
        print(f"✗ 1,000회 시도 실패 ({elapsed:.3f}초)")
        total = 26 ** 3
        print(f"\n💡 3글자 소문자 조합 수: {total:,}개 ({total}가지)")
        print(f"   실제 해시 역산은 2^256 ≈ 10^77 경우의 수 → 현실적으로 불가능")


# ──────────────────────────────────────────────
# 실험 4: 충돌 저항성 (해시값 앞 N자리 일치 탐색)
# ──────────────────────────────────────────────

def exp4_collision():
    print_separator("실험 4: 부분 충돌 탐색 — PoW 사전 맛보기")

    prefix_lengths = [1, 2, 3]  # 목표 앞 N hex자리 = 0

    for n in prefix_lengths:
        target_prefix = "0" * n
        count = 0
        start = time.time()

        while True:
            candidate = f"blockchain{count}"
            h = sha256(candidate)
            count += 1
            if h.startswith(target_prefix):
                elapsed = time.time() - start
                print(f"\n  앞 {n}자리 = '{'0'*n}' 조건:")
                print(f"    입력: '{candidate}'  →  {h}")
                print(f"    시도 횟수: {count:,}회 | 소요 시간: {elapsed:.3f}초")
                break

            if count > 500_000:
                print(f"  앞 {n}자리 조건: 50만 회 내 미발견 (너무 어려움)")
                break

    print(f"\n💡 Bitcoin PoW는 앞 19자리(=76비트) 0 조건")
    print(f"   → 평균 2^76 ≈ 7.5×10^22 번 시도 필요")


# ──────────────────────────────────────────────
# 실험 5: 블록체인 구조 시뮬레이션
# ──────────────────────────────────────────────

def exp5_chain():
    print_separator("실험 5: 블록 해시 체인 — 변조 시 연쇄 붕괴")

    blocks = []

    def make_block(index: int, data: str, prev_hash: str) -> dict:
        content = f"{index}{data}{prev_hash}"
        return {
            "index":     index,
            "data":      data,
            "prev_hash": prev_hash,
            "hash":      sha256(content),
        }

    # 블록체인 구성
    genesis = make_block(0, "Genesis Block", "0" * 64)
    blocks.append(genesis)
    datas = ["Alice→Bob: 1BTC", "Bob→Carol: 0.5BTC", "Carol→Dave: 2BTC"]
    for i, d in enumerate(datas, 1):
        blocks.append(make_block(i, d, blocks[-1]["hash"]))

    print("\n  [정상 체인]")
    for b in blocks:
        print(f"  Block {b['index']}: {b['hash'][:20]}...  ← {b['prev_hash'][:12]}...")

    # Block 1 데이터 변조
    print("\n  [Block 1 데이터 변조: 'Alice→Bob: 1BTC' → 'Alice→Bob: 999BTC']")
    tampered = blocks[:]
    tampered[1] = make_block(1, "Alice→Bob: 999BTC", tampered[0]["hash"])

    for b in tampered:
        original_hash = blocks[b["index"]]["hash"]
        current_hash  = b["hash"]
        ok = "✓" if original_hash == current_hash else "✗ 해시 불일치!"
        print(f"  Block {b['index']}: {current_hash[:20]}...  {ok}")

    print("\n💡 Block 1을 변조하면 Block 1의 해시가 바뀌고,")
    print("   Block 2의 prev_hash가 다르므로 Block 2~3 해시도 연쇄적으로 바뀝니다.")
    print("   → 전체 체인을 다시 계산해야 하고, PoW가 적용되면 사실상 불가능합니다.")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🔐 4주차 실습: SHA-256 & 해시 함수 특성 실험\n")

    exp1_basic()
    print()
    exp2_avalanche()
    print()
    exp3_one_way()
    print()
    exp4_collision()
    print()
    exp5_chain()

    print("\n" + "=" * 60)
    print("✅ 실습 완료! 출력 결과 스크린샷 → LMS 제출")
    print("=" * 60)
