# Week 07 — Consensus + Bitcoin Architecture (개념)

계명대학교 대학원 컴퓨터공학과 | Special Topics on Distributed Systems (A2037-01) | 2026년 2학기

| 항목 | 내용 |
| --- | --- |
| 주제 | 합의 알고리즘(PoW/PoS), Bitcoin UTXO 구조 (개념 설명) |
| 실습 | PoW 채굴 시뮬레이터 (Python) |
| 코드 | `pow_simulator.py` |

> 📌 Bitcoin 지갑(Sparrow Wallet 등) 핸즈온 실습은 이 강의에서 다루지 않습니다.
> 대학원 과정은 이후 주차의 Ethereum 기반 스마트컨트랙트·연구 활동에 집중하며,
> UTXO/Bitcoin Architecture는 개념 이해 수준(이론 강의)으로만 다룹니다.

## 실습 흐름
1. PoW 시뮬레이터 실행 — 난이도(자릿수)를 바꿔가며 채굴 소요 시간 측정
2. 난이도-시간 관계를 통해 작업증명의 계산 비용 구조를 체감
3. UTXO 모델 vs Account 모델(Ethereum) 차이는 이론 강의에서 개념적으로만 비교
