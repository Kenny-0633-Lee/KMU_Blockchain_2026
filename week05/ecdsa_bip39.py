from ecdsa import SigningKey, SECP256k1

# --- [정상적인 거래 준비] ---
# 1. 내 열쇠(개인키)와 계좌번호(공개키)를 만들어요.
private_key = SigningKey.generate(curve=SECP256k1)
public_key = private_key.get_verifying_key()

# 2. 진짜 주인이 메시지를 작성하고 도장(서명)을 찍습니다.
original_message = "I send 1 BTC to my friend."
message_bytes = original_message.encode()
signature = private_key.sign(message_bytes)

print(f"📜 원본 메시지: {original_message}")
print(f"✍️ 생성된 도장(서명): {signature.hex()[:30]}...")

# --- [상황 발생: 해커의 위조 시도] ---
# 3. 해커가 중간에서 메시지를 살짝 고쳤습니다! (1 BTC -> 100 BTC)
hacked_message = "I send 100 BTC to my friend."
hacked_message_bytes = hacked_message.encode()

print(f"\n😈 위조된 메시지: {hacked_message}")

# --- [검증 시스템 가동] ---
print("\n🔍 [검증 시스템] 거래 내역과 도장을 대조합니다...")

# 

try:
    # 해커가 고친 메시지와, 아까 만든 진짜 도장을 같이 넣어봅니다.
    public_key.verify(signature, hacked_message_bytes)
    print("✅ 결과: 검증 성공! (이럴 수가, 위조를 못 잡아냈어요!)")
except:
    print("❌ 결과: 검증 실패! 위조된 거래입니다. 장부에 기록할 수 없습니다!")