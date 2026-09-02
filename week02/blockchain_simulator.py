"""
=============================================================
 2주차 실습: 블록체인 구조 시뮬레이터
=============================================================
 학습 목표:
   1. 블록의 구조(index, timestamp, data, prev_hash, hash) 이해
   2. 해시체인으로 블록이 연결되는 원리 체득
   3. 데이터 변조 시 유효성 검사 실패 확인
   4. 해시 재계산으로 덮어쓰기 시도 → 여전히 실패하는 이유 이해

 실행 방법:
   uv run python week02/blockchain_simulator.py

 필요 라이브러리: 표준 라이브러리만 사용
=============================================================
"""

import hashlib
import time
import json
from typing import List, Optional


# ─────────────────────────────────────────────
# Block 클래스
# ─────────────────────────────────────────────

class Block:
    """단일 블록을 표현하는 클래스."""

    def __init__(self, index: int, data: str, prev_hash: str):
        self.index     = index
        self.timestamp = time.time()
        self.data      = data
        self.prev_hash = prev_hash
        self.hash      = self.calculate_hash()

    def calculate_hash(self) -> str:
        """블록의 모든 필드를 직렬화하여 SHA-256 해시를 계산한다."""
        block_string = json.dumps({
            "index":     self.index,
            "timestamp": self.timestamp,
            "data":      self.data,
            "prev_hash": self.prev_hash,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def __repr__(self) -> str:
        return (
            f"Block #{self.index}\n"
            f"  data      : {self.data}\n"
            f"  prev_hash : {self.prev_hash[:20]}...\n"
            f"  hash      : {self.hash[:20]}...\n"
        )


# ─────────────────────────────────────────────
# Blockchain 클래스
# ─────────────────────────────────────────────

class Blockchain:
    """블록들의 연결 리스트를 관리하는 클래스."""

    def __init__(self):
        self.chain: List[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """제네시스 블록(#0)을 생성한다. prev_hash는 "0"*64 로 고정."""
        genesis = Block(index=0, data="Genesis Block", prev_hash="0" * 64)
        self.chain.append(genesis)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: str) -> Block:
        """새 블록을 생성하고 체인에 추가한다."""
        prev = self.get_latest_block()
        new_block = Block(
            index     = prev.index + 1,
            data      = data,
            prev_hash = prev.hash,
        )
        self.chain.append(new_block)
        return new_block

    # ── 유효성 검사 ──────────────────────────

    def is_valid(self) -> tuple[bool, Optional[str]]:
        """
        체인 전체의 무결성을 검사한다.

        반환값:
          (True,  None)          → 유효한 체인
          (False, 오류 설명)     → 유효하지 않은 체인
        """
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            # 1) 블록 자체 해시 검증
            recalculated = current.calculate_hash()
            if current.hash != recalculated:
                return False, (
                    f"Block #{i} 해시 불일치\n"
                    f"  저장된 해시   : {current.hash[:40]}...\n"
                    f"  재계산 해시   : {recalculated[:40]}..."
                )

            # 2) 이전 블록과의 연결 검증
            if current.prev_hash != previous.hash:
                return False, (
                    f"Block #{i}의 prev_hash가 Block #{i-1}.hash와 불일치\n"
                    f"  Block #{i}.prev_hash : {current.prev_hash[:40]}...\n"
                    f"  Block #{i-1}.hash    : {previous.hash[:40]}..."
                )

        return True, None

    def print_chain(self, label: str = "") -> None:
        """체인 전체를 보기 좋게 출력한다."""
        if label:
            print(f"  [{label}]")
        for block in self.chain:
            print(f"  {block}")

    def print_validation(self) -> None:
        """유효성 검사 결과를 출력한다."""
        valid, msg = self.is_valid()
        if valid:
            print("  유효성 검사: ✅ 체인이 유효합니다.\n")
        else:
            print("  유효성 검사: ❌ 체인이 유효하지 않습니다.")
            print(f"  오류 내용:\n    {msg}\n")


# ─────────────────────────────────────────────
# [SCENARIO 1]  정상 체인 생성 + 유효성 검사
# ─────────────────────────────────────────────

def scenario1_normal_chain():
    print("=" * 60)
    print("  [SCENARIO 1]  정상 체인 생성 + 유효성 검사")
    print("=" * 60)

    bc = Blockchain()
    bc.add_block("Alice → Bob   : 0.5 BTC")
    bc.add_block("Bob   → Carol : 0.3 BTC")
    bc.add_block("Carol → Dave  : 0.1 BTC")

    bc.print_chain("블록 3개 추가 완료")
    bc.print_validation()

    return bc   # 이후 시나리오에서 재사용


# ─────────────────────────────────────────────
# [SCENARIO 2]  블록 데이터 변조 → 유효성 실패
# ─────────────────────────────────────────────

def scenario2_tamper_data(bc: Blockchain):
    print("=" * 60)
    print("  [SCENARIO 2]  Block #2 데이터 변조 → 유효성 실패")
    print("=" * 60)

    original_data = bc.chain[2].data
    print(f"  변조 전: Block #2.data = \"{original_data}\"")

    # 데이터만 바꾸고 hash는 그대로 둠 (실제 공격자가 하려는 것)
    bc.chain[2].data = "Bob   → Carol : 99.0 BTC"   # 금액 위조
    print(f"  변조 후: Block #2.data = \"{bc.chain[2].data}\"")
    print(f"  (hash는 변경하지 않음 — 공격자가 hash를 모른다고 가정)\n")

    bc.print_validation()

    # 원상복구 (다음 시나리오를 위해)
    bc.chain[2].data = original_data
    bc.chain[2].hash = bc.chain[2].calculate_hash()


# ─────────────────────────────────────────────
# [SCENARIO 3]  해시까지 재계산해서 덮어쓰기 시도
# ─────────────────────────────────────────────

def scenario3_rehash_attempt(bc: Blockchain):
    print("=" * 60)
    print("  [SCENARIO 3]  해시 재계산으로 덮어쓰기 시도 → 여전히 실패")
    print("=" * 60)
    print("  → Block #2를 변조한 뒤 hash도 다시 계산하면?")
    print("    Block #3의 prev_hash가 Block #2의 원본 hash를")
    print("    참조하고 있으므로 연결이 끊어집니다.\n")

    # 변조
    bc.chain[2].data = "Bob   → Carol : 99.0 BTC"
    bc.chain[2].hash = bc.chain[2].calculate_hash()  # hash 재계산

    print(f"  Block #2 재계산 hash: {bc.chain[2].hash[:40]}...")
    print(f"  Block #3  prev_hash: {bc.chain[3].prev_hash[:40]}...")
    match = bc.chain[2].hash == bc.chain[3].prev_hash
    print(f"  일치 여부: {'✅ 일치' if match else '❌ 불일치 → 연결 끊김'}\n")

    bc.print_validation()

    print("  ─────────────────────────────────────────────")
    print("  [심화] Block #3 hash도 재계산하면?")
    print("  Block #4가 있다면 똑같은 문제가 반복됩니다.")
    print("  실제 Bitcoin은 수십만 블록이 쌓여 있고,")
    print("  변조 후 모든 블록을 재계산하려면 전체 네트워크의")
    print("  51% 이상의 연산력이 필요합니다 (51% Attack).")
    print()


# ─────────────────────────────────────────────
# [SCENARIO 4]  Genesis Block 변조 시도
# ─────────────────────────────────────────────

def scenario4_genesis_tamper():
    print("=" * 60)
    print("  [SCENARIO 4]  Genesis Block (#0) 변조 시도")
    print("=" * 60)

    bc = Blockchain()
    bc.add_block("TX_A")
    bc.add_block("TX_B")

    print("  변조 전 유효성:")
    bc.print_validation()

    # Genesis Block 데이터 변조 + hash 재계산
    bc.chain[0].data = "TAMPERED GENESIS"
    bc.chain[0].hash = bc.chain[0].calculate_hash()

    print("  Genesis Block 변조 후:")
    print(f"  Block #0 새 hash  : {bc.chain[0].hash[:40]}...")
    print(f"  Block #1 prev_hash: {bc.chain[1].prev_hash[:40]}...")
    print()
    bc.print_validation()


# ─────────────────────────────────────────────
# [SOLUTION NOTE]  교수 참고용 설명
# ─────────────────────────────────────────────

def solution_notes():
    print("=" * 60)
    print("  [교수 참고]  핵심 포인트 요약")
    print("=" * 60)
    notes = [
        "블록 = index + timestamp + data + prev_hash + hash 의 조합",
        "hash는 위 5개 필드 전체에 의존하므로, data만 바꿔도 hash가 달라짐",
        "변조 후 hash 재계산 → 다음 블록의 prev_hash와 불일치 (연쇄 무효화)",
        "Genesis Block(#0)을 바꿔도 #1의 prev_hash와 불일치",
        "변조를 숨기려면 변조 지점 이후 전체를 재채굴해야 함 (PoW 장벽)",
        "이어서 진행하는 Merkle Tree 실습에서 TX 변조를 더 효율적으로 검증하는 방법을 다룹니다",
    ]
    for i, note in enumerate(notes, 1):
        print(f"  {i}. {note}")
    print()


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("  ┌──────────────────────────────────────────────┐")
    print("  │  2주차  |  블록체인 시뮬레이터                │")
    print("  └──────────────────────────────────────────────┘")
    print()

    bc = scenario1_normal_chain()
    scenario2_tamper_data(bc)
    scenario3_rehash_attempt(bc)
    scenario4_genesis_tamper()
    solution_notes()

    print("  실습 완료! 수업 중 실행 화면을 보여주시거나, 종료 후 캡처를 전달해주세요.")
    print()
