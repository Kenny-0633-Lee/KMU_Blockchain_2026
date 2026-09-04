"""
distribute_eth.py — Tally 폼 제출 학생 지갑에 Sepolia 테스트 ETH 매 수업 전송

정책 (2026-08-27 확정):
    - 매 수업시간마다 제출된 주소 전원에게 무조건 전송한다.
    - 같은 학생이 여러 번(여러 주차) 받는 것은 정상이며, 중복 전송 방지 로직은 없다.
    - sent_log.json은 필터링용이 아니라 "전송 이력 기록"용이다 (append-only).

사용 예시:
    uv run python Admin/distribute_eth.py --dry-run
    uv run python Admin/distribute_eth.py
    uv run python Admin/distribute_eth.py --amount 0.2
    uv run python Admin/distribute_eth.py --csv Admin/submissions.csv

전제:
    Admin/.env 파일에 아래 값 필요 (절대 커밋 금지)
        ALCHEMY_SEPOLIA_URL=...
        ADMIN_PRIVATE_KEY=...          # 0x 접두사 없이 64자리
        TALLY_API_KEY=...              # --csv 사용 시 불필요
        TALLY_FORM_ID=...              # --csv 사용 시 불필요
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from web3 import Web3
import os

load_dotenv()

LOG_PATH = Path(__file__).parent / "sent_log.json"
TALLY_API_BASE = "https://api.tally.so"

DEFAULT_AMOUNT_ETH = 0.1


# ─────────────────────────────────────────────────────────
# 1. 제출 데이터 수집
# ─────────────────────────────────────────────────────────

def fetch_from_tally_api(form_id: str, api_key: str) -> list[dict]:
    submissions = []
    page = 1
    headers = {"Authorization": f"Bearer {api_key}"}

    while True:
        resp = requests.get(
            f"{TALLY_API_BASE}/forms/{form_id}/submissions",
            headers=headers,
            params={"page": page},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        for sub in data.get("submissions", []):
            row = {"submission_id": sub["id"], "submitted_at": sub.get("createdAt")}
            for field in sub.get("responses", sub.get("fields", [])):
                label = (field.get("label") or field.get("key") or "").strip().lower()
                row[label] = field.get("value")
            submissions.append(row)

        if not data.get("hasMore") and not data.get("has_more"):
            break
        page += 1

    return submissions


def fetch_from_csv(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [{k.strip().lower(): v for k, v in row.items()} for row in reader]


def extract_wallet_address(row: dict) -> str | None:
    for value in row.values():
        if isinstance(value, str) and value.startswith("0x") and len(value) == 42:
            return value
    return None


# ─────────────────────────────────────────────────────────
# 2. 전송 이력 기록 (필터링 아님 — 기록 전용, append-only)
# ─────────────────────────────────────────────────────────

def load_history() -> list[dict]:
    """sent_log.json을 읽는다. 구버전(딕셔너리) 형식이면 백업 후 새로 시작한다."""
    if not LOG_PATH.exists():
        return []

    data = json.loads(LOG_PATH.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    # 구버전(주소를 key로 쓰던 dict) 형식 감지 → 백업 후 마이그레이션
    backup_path = LOG_PATH.with_name("sent_log.legacy_backup.json")
    LOG_PATH.rename(backup_path)
    print(f"⚠️  구버전 형식의 sent_log.json을 발견해 {backup_path.name}으로 백업하고 새로 시작합니다.")

    migrated = []
    if isinstance(data, dict):
        for addr, entry in data.items():
            if isinstance(entry, dict):
                migrated.append({"address": addr, **entry})
    return migrated


def append_history(history: list[dict], entry: dict) -> None:
    history.append(entry)
    LOG_PATH.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


# ─────────────────────────────────────────────────────────
# 3. ETH 전송
# ─────────────────────────────────────────────────────────

def send_eth(w3: Web3, from_account, to_address: str, amount_eth: float, nonce: int) -> str:
    tx = {
        "from": from_account.address,
        "to": Web3.to_checksum_address(to_address),
        "value": w3.to_wei(amount_eth, "ether"),
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
    }
    signed = from_account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()


# ─────────────────────────────────────────────────────────
# 4. 메인
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Tally 제출 학생 전원에게 Sepolia 테스트 ETH 매회 전송 (중복 방지 없음)")
    parser.add_argument("--amount", type=float, default=DEFAULT_AMOUNT_ETH,
                         help=f"학생당 전송 금액 (ETH 단위, 기본값 {DEFAULT_AMOUNT_ETH})")
    parser.add_argument("--csv", type=str, default=None, help="Tally API 대신 CSV 파일 사용")
    parser.add_argument("--dry-run", action="store_true", help="실제 전송 없이 대상 목록만 출력")
    args = parser.parse_args()

    if args.amount <= 0:
        sys.exit("❌ --amount 는 0보다 커야 합니다.")

    if args.csv:
        print(f"📄 CSV에서 제출 데이터 로드: {args.csv}")
        rows = fetch_from_csv(args.csv)
    else:
        api_key = os.getenv("TALLY_API_KEY")
        form_id = os.getenv("TALLY_FORM_ID")
        if not api_key or not form_id:
            sys.exit("❌ .env에 TALLY_API_KEY / TALLY_FORM_ID가 필요합니다 (또는 --csv 사용).")
        print("🌐 Tally API에서 제출 데이터 조회 중...")
        rows = fetch_from_tally_api(form_id, api_key)

    print(f"   총 {len(rows)}건 제출 확인")

    addr_set = set()
    skipped_no_address = 0
    for row in rows:
        addr = extract_wallet_address(row)
        if not addr:
            skipped_no_address += 1
            continue
        addr_set.add(Web3.to_checksum_address(addr))

    if skipped_no_address:
        print(f"   ⚠️ 지갑 주소를 찾지 못해 제외된 제출: {skipped_no_address}건")

    targets = sorted(addr_set)
    print(f"   고유 주소 {len(targets)}개 — 전원에게 매번 전송 (중복전송 체크 없음)")

    if not targets:
        print("✅ 전송 대상이 없습니다. 종료합니다.")
        return

    print("\n전송 대상:")
    for addr in targets:
        print(f"  - {addr}")

    if args.dry_run:
        print(f"\n🧪 [DRY RUN] 실제 전송은 수행하지 않았습니다. (대상 {len(targets)}명 × {args.amount} ETH)")
        return

    rpc_url = os.getenv("ALCHEMY_SEPOLIA_URL")
    private_key = os.getenv("ADMIN_PRIVATE_KEY")
    if not rpc_url or not private_key:
        sys.exit("❌ .env에 ALCHEMY_SEPOLIA_URL / ADMIN_PRIVATE_KEY가 필요합니다.")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        sys.exit("❌ Sepolia RPC 연결 실패. ALCHEMY_SEPOLIA_URL을 확인하세요.")

    account = w3.eth.account.from_key(private_key)
    balance = w3.from_wei(w3.eth.get_balance(account.address), "ether")
    required = args.amount * len(targets)
    print(f"\n💰 관리자 지갑 잔액: {balance} ETH / 필요 금액: {required} ETH")
    if balance < required:
        sys.exit("❌ 잔액 부족. Faucet에서 충전 후 다시 실행하세요.")

    confirm = input(f"\n{len(targets)}명에게 각 {args.amount} ETH를 전송합니다 (중복전송 체크 없음). 계속할까요? (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("취소되었습니다.")
        return

    history = load_history()
    nonce = w3.eth.get_transaction_count(account.address, "pending")

    for addr in targets:
        # (1) 온체인 전송 — 이게 성공해야만 nonce를 증가시킨다
        try:
            tx_hash = send_eth(w3, account, addr, args.amount, nonce)
        except Exception as e:
            print(f"  ❌ {addr} 전송 실패: {e}")
            continue  # nonce 그대로 유지, 다음 주소도 같은 nonce로 재시도

        nonce += 1
        print(f"  ✅ {addr} → {tx_hash}")

        # (2) 이력 기록 — 실패해도 전송 자체는 이미 성공했으므로 nonce에 영향 없음
        try:
            append_history(history, {
                "address": addr,
                "amount_eth": args.amount,
                "tx_hash": tx_hash,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            })
        except Exception as e:
            print(f"  ⚠️  이력 기록 실패 (전송 자체는 성공함): {e}")

    print(f"\n완료. 이력은 {LOG_PATH} 에 누적 기록됨.")


if __name__ == "__main__":
    main()
