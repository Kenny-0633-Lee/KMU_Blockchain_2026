"""
week03/merkle_tree.py
=====================
3주차 — Merkle Tree 구현

학습 목표:
  - Merkle Tree의 구조와 작동 원리 이해
  - 해시 함수(SHA-256)를 이용한 트리 구성
  - Merkle Proof(포함 증명) 생성 및 검증
  - Bitcoin 블록 내 트랜잭션 무결성 검증 원리 체험

실행:
  uv run python week03/merkle_tree.py
"""

import hashlib


# ──────────────────────────────────────────────
# 1. 헬퍼 함수
# ──────────────────────────────────────────────

def sha256(data: str | bytes) -> str:
    """문자열 또는 바이트를 SHA-256 해시(hex)로 변환"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_pair(left: str, right: str) -> str:
    """두 해시를 결합하여 부모 해시 계산 (Bitcoin 방식: SHA-256(left + right))"""
    combined = left + right
    return sha256(combined.encode("utf-8"))


# ──────────────────────────────────────────────
# 2. Merkle Tree 클래스
# ──────────────────────────────────────────────

class MerkleTree:
    """
    단순 이진 Merkle Tree 구현
    - 홀수 개 노드: 마지막 노드를 복제하여 짝수로 맞춤 (Bitcoin 방식)
    """

    def __init__(self, transactions: list[str]):
        if not transactions:
            raise ValueError("트랜잭션 목록이 비어 있습니다.")
        self.transactions = transactions
        self.leaves: list[str] = [sha256(tx) for tx in transactions]
        self.tree: list[list[str]] = []   # tree[0] = leaves, tree[-1] = [root]
        self.root: str = self._build()

    def _build(self) -> str:
        """트리 구성 → Merkle Root 반환"""
        level = self.leaves[:]
        self.tree = [level[:]]

        while len(level) > 1:
            # 홀수이면 마지막 요소 복제
            if len(level) % 2 == 1:
                level.append(level[-1])

            next_level = []
            for i in range(0, len(level), 2):
                parent = hash_pair(level[i], level[i + 1])
                next_level.append(parent)

            self.tree.append(next_level[:])
            level = next_level

        return level[0]

    def get_proof(self, tx_index: int) -> list[dict]:
        """
        특정 트랜잭션의 Merkle Proof 생성
        반환: [{"hash": "...", "position": "left"|"right"}, ...]
        """
        proof = []
        idx = tx_index
        level = self.leaves[:]

        for level_nodes in self.tree[:-1]:   # root 제외
            # 홀수이면 마지막 복제
            nodes = level_nodes[:]
            if len(nodes) % 2 == 1:
                nodes.append(nodes[-1])

            if idx % 2 == 0:   # 왼쪽 → 형제는 오른쪽
                sibling_idx = idx + 1
                position = "right"
            else:               # 오른쪽 → 형제는 왼쪽
                sibling_idx = idx - 1
                position = "left"

            sibling_idx = min(sibling_idx, len(nodes) - 1)
            proof.append({"hash": nodes[sibling_idx], "position": position})
            idx //= 2

        return proof

    def verify_proof(self, tx: str, proof: list[dict]) -> bool:
        """Merkle Proof를 이용해 트랜잭션이 트리에 포함되어 있는지 검증"""
        current = sha256(tx)
        for step in proof:
            if step["position"] == "right":
                current = hash_pair(current, step["hash"])
            else:
                current = hash_pair(step["hash"], current)
        return current == self.root

    def display(self) -> None:
        """트리 구조 출력 (루트부터 역순)"""
        print("\n📐 Merkle Tree 구조 (상단=루트, 하단=리프)\n")
        for i, level in enumerate(reversed(self.tree)):
            label = "Root" if i == len(self.tree) - 1 else f"Level {len(self.tree)-1-i}"
            print(f"  [{label:8s}] {len(level)}개 노드")
            for h in level:
                print(f"             {h[:20]}...")
        print()


# ──────────────────────────────────────────────
# 3. 실습 시나리오
# ──────────────────────────────────────────────

def scenario_basic():
    """기본 Merkle Tree 구성"""
    print("=" * 60)
    print("📦 시나리오 1: 기본 Merkle Tree 구성")
    print("=" * 60)

    transactions = [
        "Alice → Bob: 1.5 BTC",
        "Bob → Carol: 0.3 BTC",
        "Carol → Dave: 2.0 BTC",
        "Dave → Alice: 0.7 BTC",
    ]

    print("\n📋 트랜잭션 목록:")
    for i, tx in enumerate(transactions):
        print(f"  [{i}] {tx}")

    tree = MerkleTree(transactions)

    print("\n🍃 리프 해시 (각 TX의 SHA-256):")
    for i, (tx, leaf) in enumerate(zip(transactions, tree.leaves)):
        print(f"  [{i}] {tx[:25]:<26} → {leaf[:20]}...")

    print(f"\n🌳 Merkle Root:\n  {tree.root}")
    tree.display()


def scenario_proof():
    """Merkle Proof 생성 및 검증"""
    print("=" * 60)
    print("🔍 시나리오 2: Merkle Proof (포함 증명)")
    print("=" * 60)

    transactions = [
        "Alice → Bob: 1.5 BTC",
        "Bob → Carol: 0.3 BTC",
        "Carol → Dave: 2.0 BTC",
        "Dave → Alice: 0.7 BTC",
    ]
    tree = MerkleTree(transactions)

    # TX[1] 검증
    target_idx = 1
    target_tx  = transactions[target_idx]
    print(f"\n📌 검증 대상: [{target_idx}] {target_tx}")

    proof = tree.get_proof(target_idx)
    print("\n📜 Merkle Proof (경로):")
    for step in proof:
        print(f"  [{step['position']:5s}] {step['hash'][:20]}...")

    is_valid = tree.verify_proof(target_tx, proof)
    print(f"\n✅ 검증 결과: {'포함 확인됨 ✓' if is_valid else '포함되지 않음 ✗'}")

    # 변조된 TX 검증
    tampered_tx = "Alice → Bob: 999 BTC"  # 금액 변조
    is_valid_tampered = tree.verify_proof(tampered_tx, proof)
    print(f"\n🚨 변조된 TX 검증: '{tampered_tx}'")
    print(f"   결과: {'포함 확인됨 ✓' if is_valid_tampered else '변조 감지됨 ✗ → 차단!'}")


def scenario_odd():
    """홀수 개 트랜잭션 처리 (Bitcoin 방식)"""
    print("=" * 60)
    print("🔢 시나리오 3: 홀수 트랜잭션 처리")
    print("=" * 60)

    transactions = [
        "TX_A",
        "TX_B",
        "TX_C",   # 홀수 → 마지막 노드 복제
    ]

    tree = MerkleTree(transactions)
    print(f"\n트랜잭션 수: {len(transactions)}개 (홀수)")
    print(f"리프 수:     {len(tree.leaves)}개 (홀수)")
    print("→ Bitcoin 방식: 마지막 해시를 복제하여 짝수로 맞춤")
    print(f"\nMerkle Root: {tree.root[:30]}...")
    tree.display()


def scenario_tamper():
    """블록 변조 시 Merkle Root 변경 확인"""
    print("=" * 60)
    print("🚨 시나리오 4: 블록 변조 감지")
    print("=" * 60)

    original = ["TX_A", "TX_B", "TX_C", "TX_D"]
    tampered = ["TX_A", "TX_B_HACKED", "TX_C", "TX_D"]  # TX_B 변조

    tree_orig    = MerkleTree(original)
    tree_tamper  = MerkleTree(tampered)

    print(f"\n원본  Merkle Root: {tree_orig.root[:30]}...")
    print(f"변조후 Merkle Root: {tree_tamper.root[:30]}...")
    print(f"\n일치 여부: {'동일 ✓' if tree_orig.root == tree_tamper.root else '불일치 ✗ → 변조 감지!'}")
    print("\n→ 단 하나의 TX만 변조해도 Merkle Root가 완전히 달라집니다.")


# ──────────────────────────────────────────────
# 4. 메인
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🌳 3주차 실습: Merkle Tree 구현\n")

    scenario_basic()
    print()
    scenario_proof()
    print()
    scenario_odd()
    print()
    scenario_tamper()

    print("\n" + "=" * 60)
    print("✅ 실습 완료!")
    print("   위 출력 내용 스크린샷 → LMS 제출")
    print("=" * 60)
