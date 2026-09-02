"""
week06/pow_simulator.py
=======================
7주차 — Proof of Work (PoW) 채굴 시뮬레이터

학습 목표:
  - PoW 합의 알고리즘의 작동 원리 구현
  - 난이도(앞 N자리 0 조건)와 채굴 시간의 관계 측정
  - Nonce 탐색 과정 시각화
  - PoW vs PoS 비교 이해
  - 51% 공격의 이론적 비용 계산

실행:
  uv run python week06/pow_simulator.py
"""

import hashlib
import time
import random
import statistics


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def mine_block(block_data: dict, difficulty: int) -> tuple[int, str, float]:
    """
    PoW 채굴: 해시의 앞 difficulty 자리가 '0'이 될 때까지 nonce 증가

    Returns:
        (nonce, winning_hash, elapsed_seconds)
    """
    prefix = "0" * difficulty
    nonce = 0
    start = time.time()

    while True:
        content = (
            f"{block_data['index']}{block_data['data']}{block_data['prev_hash']}{nonce}"
        )
        h = sha256(content)
        if h.startswith(prefix):
            return nonce, h, time.time() - start
        nonce += 1


def print_separator(title: str = "") -> None:
    if title:
        print(f"\n{'=' * 62}")
        print(f"  {title}")
        print(f"{'=' * 62}\n")
    else:
        print("=" * 62)


# ──────────────────────────────────────────────
# 1. 기본 채굴 시연
# ──────────────────────────────────────────────


def demo_basic_mining():
    print_separator("데모 1: 단일 블록 채굴")

    block = {
        "index": 1,
        "data": "Alice → Bob: 1.5 BTC",
        "prev_hash": "0" * 64,
    }
    difficulty = 4

    print(f"블록 데이터: '{block['data']}'")
    print(f"난이도: {difficulty} (해시 앞 {difficulty}자리 = '{'0' * difficulty}')")
    print(f"\n채굴 시작...", end="", flush=True)

    nonce, winning_hash, elapsed = mine_block(block, difficulty)

    print(f" 완료!\n")
    print(f"  Nonce:       {nonce:,}")
    print(f"  해시:        {winning_hash}")
    print(f"  소요 시간:   {elapsed:.3f}초")
    print(f"  초당 해시:   {nonce / elapsed:,.0f} H/s")

    print(f"""
💡 핵심:
  - 유효한 해시를 찾는 것은 어렵지만(nonce를 무수히 시도)
  - 검증은 한 번의 SHA-256 계산으로 즉시 가능
  - 이 비대칭성이 PoW 보안의 핵심입니다.
""")


# ──────────────────────────────────────────────
# 2. 난이도별 채굴 시간 측정
# ──────────────────────────────────────────────


def demo_difficulty_vs_time():
    print_separator("데모 2: 난이도별 채굴 시간 측정")

    block = {"index": 1, "data": "test", "prev_hash": "0" * 64}
    max_difficulty = 6
    results = []

    print(
        f"{'난이도':>6} | {'Nonce':>10} | {'시간(초)':>10} | {'H/s':>12} | 해시(앞 20자)"
    )
    print("-" * 75)

    for diff in range(1, max_difficulty + 1):
        nonce, h, elapsed = mine_block(block, diff)
        hps = nonce / elapsed if elapsed > 0 else 0
        results.append((diff, nonce, elapsed, hps))
        print(
            f"  {diff:4d}   | {nonce:10,} | {elapsed:10.3f} | {hps:12,.0f} | {h[:20]}..."
        )

    print(f"""
💡 난이도 1 증가(hex 0 추가) = 기대 탐색 횟수 16배 증가 (16진수 한 자리 = 4비트)
Bitcoin 실제 난이도: 약 76비트(hex 19자리) → 2^76 ≈ 7.5×10^22 번 시도 필요
""")
    return results


# ──────────────────────────────────────────────
# 3. 블록체인 채굴 시뮬레이션 (5블록)
# ──────────────────────────────────────────────


def demo_blockchain_mining():
    print_separator("데모 3: 5블록 연속 채굴 (블록체인 구성)")

    difficulty = 3
    transactions = [
        "Alice → Bob: 1.0 BTC",
        "Bob → Carol: 0.5 BTC",
        "Carol → Dave: 2.0 BTC",
        "Dave → Eve: 0.3 BTC",
        "Eve → Alice: 1.2 BTC",
    ]

    print(f"난이도: {difficulty} (앞 {difficulty}자리 = '{'0' * difficulty}')\n")
    print(
        f"{'#':>3} | {'Nonce':>8} | {'시간(초)':>8} | {'해시(앞 24자)':24s} | 트랜잭션"
    )
    print("-" * 90)

    blockchain = []
    prev_hash = "0" * 64

    for i, tx in enumerate(transactions):
        block = {"index": i + 1, "data": tx, "prev_hash": prev_hash}
        nonce, h, elapsed = mine_block(block, difficulty)
        blockchain.append({**block, "nonce": nonce, "hash": h})
        prev_hash = h
        print(f"  {i + 1:1d} | {nonce:8,} | {elapsed:8.3f} | {h[:24]} | {tx}")

    print(f"\n✅ {len(transactions)}개 블록 채굴 완료!")
    print(f"\n🔗 체인 구조 (해시 포인터):")
    for b in blockchain:
        print(
            f"  Block {b['index']}: ...{b['hash'][-8:]} ← prev: ...{b['prev_hash'][-8:]}"
        )


# ──────────────────────────────────────────────
# 4. 통계 실험: 샘플링으로 기댓값 검증
# ──────────────────────────────────────────────


def demo_statistics():
    print_separator("데모 4: 통계 실험 — 기댓값 vs 실측값")

    difficulty = 2  # 앞 2자리 = '00': 기대 탐색 횟수 = 16^2 = 256
    expected = 16**difficulty
    samples = 30

    print(f"난이도 {difficulty} (앞 {difficulty}자리 = '{'0' * difficulty}')")
    print(f"이론적 기대 탐색 횟수: {expected:,}회")
    print(f"\n{samples}회 반복 채굴 실험...\n")

    nonce_list = []
    for i in range(samples):
        block = {"index": i, "data": f"tx{i}", "prev_hash": "00"}
        nonce, _, _ = mine_block(block, difficulty)
        nonce_list.append(nonce)

    mean_ = statistics.mean(nonce_list)
    stdev = statistics.stdev(nonce_list)
    min_ = min(nonce_list)
    max_ = max(nonce_list)

    print(f"  실험 횟수: {samples}회")
    print(f"  평균 Nonce: {mean_:,.1f}  (기댓값: {expected:,})")
    print(f"  표준편차:   {stdev:,.1f}")
    print(f"  최솟값:     {min_:,}")
    print(f"  최댓값:     {max_:,}")

    print(f"""
💡 PoW는 확률 과정입니다.
  기댓값은 있지만 매번 결과가 다릅니다 (기하 분포).
  Bitcoin은 2,016 블록마다 평균 10분/블록이 되도록 난이도를 자동 조정합니다.
""")


# ──────────────────────────────────────────────
# 5. PoW vs PoS 비교
# ──────────────────────────────────────────────


def demo_pos_comparison():
    print_separator("데모 5: PoW vs PoS 비교")

    print("""
  [Proof of Work (PoW)]
  ─────────────────────────────────────────────
  - 채굴자가 해시 퍼즐을 풀어 블록 생성권 획득
  - 컴퓨팅 파워(해시레이트)에 비례한 채굴 확률
  - 장점: 검증된 보안, 탈중앙화
  - 단점: 전력 소비 (Bitcoin ≈ 아르헨티나 연간 전력 사용량)
  - 사용: Bitcoin (BTC), Litecoin (LTC)

  [Proof of Stake (PoS)]
  ─────────────────────────────────────────────
  - 검증자(Validator)가 ETH를 32개 스테이킹 → 블록 제안권
  - 보유 지분에 비례한 블록 생성 확률
  - 장점: 에너지 효율 (~99.95% 절감), 빠른 Finality
  - 단점: 부익부 빈익빈 우려, 스테이킹 의존도
  - 사용: Ethereum (ETH, Merge 이후 2022년 9월)

  [51% 공격 비용 비교]
  ─────────────────────────────────────────────
  PoW: Bitcoin 해시레이트의 51% = 수백억 달러 규모 채굴기
  PoS: ETH 스테이킹 총량의 1/3 이상 = 수십억 달러 ETH 필요
       + 공격 성공해도 ETH 가치 폭락 → 자기 자산 손실 → 자기 억제력
""")


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n⛏  7주차 실습: Proof of Work 채굴 시뮬레이터\n")

    demo_basic_mining()
    demo_difficulty_vs_time()
    demo_blockchain_mining()
    demo_statistics()
    demo_pos_comparison()

    print("=" * 62)
    print("✅ 실습 완료! 출력 결과 스크린샷 → LMS 제출")
    print("=" * 62)
