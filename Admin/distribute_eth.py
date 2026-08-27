"""
distribute_eth.py — Tally 폼 제출 학생 지갑에 Sepolia 테스트 ETH 일괄 전송

사용 예시:
    # dry-run (실제 전송 없이 대상 목록만 확인)
    uv run python distribute_eth.py --amount 0.05 --dry-run

    # 실제 전송 (Tally API로 최신 제출건 조회)
    uv run python distribute_eth.py --amount 0.05

    # CSV로 대체 입력 (Tally API 키가 없을 때)
    uv run python distribute_eth.py --amount 0.05 --csv submissions.csv

전제:
    .env 파일에 아래 값 필요 (00_Admin_Only/.env, 절대 커밋 금지)
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


# ─────────────────────────────────────────────────────────
# 1. 제출 데이터 수집
# ─────────────────────────────────────────────────────────

def fetch_from_tally_api(form_id: str, api_key: str) -> list[dict]:
    """Tally API에서 전체 제출건을 페이지네이션으로 수집한다."""
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
                # Tally 응답 필드 스키마: {"label": "...", "value": "..."} 형태 가정
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
    """행(row)에서 지갑 주소로 보이는 값을 찾는다.
    Tally 필드 라벨이 정확히 뭔지 몰라도 동작하도록,
    0x로 시작하는 42자리 값을 아무 컬럼에서나 탐색한다."""
    for value in row.values():
        if isinstance(value, str) and value.startswith("0x") and len(value) == 42:
            return value
    return None


# ─────────────────────────────────────────────────────────
# 2. 전송 로그 (중복 방지)
# ─────────────────────────────────────────────────────────

def load_log() -> dict:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {}


def save_log(log: dict) -> None:
    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


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
    parser = argparse.ArgumentParser(description="Tally 제출 학생에게 Sepolia 테스트 ETH 분배")
    parser.add_argument("--amount", type=float, required=True, help="학생당 전송 금액 (ETH 단위, 예: 0.05)")
    parser.add_argument("--csv", type=str, default=None, help="Tally API 대신 CSV 파일 사용 (Tally 내보내기 파일 경로)")
    parser.add_argument("--dry-run", action="store_true", help="실제 전송 없이 대상 목록만 출력")
    args = parser.parse_args()

    if args.amount <= 0:
        sys.exit("❌ --amount 는 0보다 커야 합니다.")

    # 4-1. 제출 데이터 수집
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

    # 4-2. 주소 추출 + 중복 제거 (같은 주소 여러 번 제출 시 최신 1건만)
    addr_to_row = {}
    skipped_no_address = 0
    for row in rows:
        addr = extract_wallet_address(row)
        if not addr:
            skipped_no_address += 1
            continue
        addr_to_row[Web3.to_checksum_address(addr)] = row

    if skipped_no_address:
        print(f"   ⚠️ 지갑 주소를 찾지 못해 제외된 제출: {skipped_no_address}건")

    # 4-3. 기존 전송 로그와 대조 → 신규 대상만 필터
    log = load_log()
    targets = [addr for addr in addr_to_row if addr not in log]
    already_sent = len(addr_to_row) - len(targets)

    print(f"   고유 주소 {len(addr_to_row)}개 중 이미 전송됨 {already_sent}개, 신규 대상 {len(targets)}개")

    if not targets:
        print("✅ 신규 전송 대상이 없습니다. 종료합니다.")
        return

    print("\n신규 전송 대상:")
    for addr in targets:
        print(f"  - {addr}")

    if args.dry_run:
        print(f"\n🧪 [DRY RUN] 실제 전송은 수행하지 않았습니다. (대상 {len(targets)}명 × {args.amount} ETH)")
        return

    # 4-4. 실제 전송
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

    confirm = input(f"\n{len(targets)}명에게 각 {args.amount} ETH를 전송합니다. 계속할까요? (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("취소되었습니다.")
        return

    nonce = w3.eth.get_transaction_count(account.address, "pending")
    for addr in targets:
        try:
            tx_hash = send_eth(w3, account, addr, args.amount, nonce)
            log[addr] = {
                "amount_eth": args.amount,
                "tx_hash": tx_hash,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            print(f"  ✅ {addr} → {tx_hash}")
            nonce += 1
            save_log(log)  # 매 전송 후 즉시 저장 (중간에 끊겨도 중복 전송 방지)
        except Exception as e:
            print(f"  ❌ {addr} 전송 실패: {e}")

    print(f"\n완료. 총 {len(targets)}건 시도. 결과는 {LOG_PATH} 확인.")


if __name__ == "__main__":
    main()
