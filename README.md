# KMU Blockchain 2026

**Special Topics on Distributed Systems (A2037-01)** — 계명대학교 대학원 컴퓨터공학과 · 2026년 2학기

이 레포는 강의 실습 코드 저장소입니다. **강의자료(이론·연구정보·FAQ)의 기준은 Notion 강의 허브**이며, 이 레포는 코드와 최소한의 실행 안내만 담습니다.

> 📎 Notion 강의 허브: 비공개 초대제 (1주차 오리엔테이션 시간에 개별 초대)

---

## 강의 정보

| 항목 | 내용 |
| --- | --- |
| 담당교수 | 이경근 (infosec@knu.ac.kr) |
| 강의시간 | 금 12:00–14:50 (공1314) |
| 이수구분 | 전공, 3학점 |
| 주교재 | Notion 강의 허브 (직접 제작 자료) |
| 부교재 | *Mastering Blockchain* 4th Ed. — Imran Bashir |

---

## 평가 방식

| 항목 | 비율 | 비고 |
| --- | --- | --- |
| 출석 | 10% | |
| 프로포절 발표 | 30% | 6주차, 중간고사 대체 |
| 논문발제 + 연구발표 | 40% | 10·12주차(잠정), 기말고사 대체 |
| 실습실행평가 | 20% | 실행 여부(ON/OFF) 확인, 세부 배점표 없음 |

필기시험은 실시하지 않습니다.

---

## 15주 커리큘럼

| 주 | 주제 | 실습 도구 |
| --- | --- | --- |
| 1 | Orientation | MetaMask |
| 2 | Blockchain 101 + Decentralization + Merkle Tree | Python |
| 3 | 블록체인 연구분야 소개 + 평가방법 안내 | — |
| 4 | Cryptography: Symmetric (SHA-256, AES) | Python |
| 5 | Cryptography: Asymmetric (ECDSA, BIP-39) | Python |
| 6 | **연구주제 선정 + 프로포절 발표** | — |
| 7 | Consensus + Bitcoin 핵심 (개념) | Python (PoW 시뮬레이터) |
| 8 | Ethereum 구조 + 스마트 컨트랙트 핵심 | Remix IDE, Sepolia(시연) |
| 9 | SRE 맛보기 (Scaffold-ETH 2, 로컬) + 토큰 개념 | SRE |
| 10 | **논문 발제 / 연구 발표 ①** (A조 논문, B조 연구) | — |
| 11 | 토큰 표준 코드 해부(ERC-20/721) + DApp | Remix VM, Hardhat, ethers.js |
| 12 | **논문 발제 / 연구 발표 ②** (B조 논문, A조 연구) | — |
| 13 | 예비 (발표 결원 보강) · 최종 정리 제출 | — |
| 14 | 공휴일(12/25) — 보강 일정 별도 공지 | — |
| 15 | 공휴일(1/1) — 보강 일정 별도 공지 | — |

> 주차 배치와 날짜는 잠정이며 학사일정에 따라 변경될 수 있습니다. 최신 내용은 Notion 강의 허브를 기준으로 합니다.

---

## 레포 구조

```
KMU_Blockchain_2026/
├── week01/ ~ week15/       ← 주차별 실습 코드
├── docs/                   ← 지갑 주소 수집용 연결 페이지 (GitHub Pages)
├── Admin/                  ← 관리자 전용 스크립트·문서 (ETH 분배, 커리큘럼 TODO)
├── pyproject.toml          ← Python 의존성 (uv 관리)
```

---

## 시작하기

```bash
git clone https://github.com/Kenny-0633-Lee/KMU_Blockchain_2026.git
cd KMU_Blockchain_2026
uv sync
```

상세 개발환경 설정(Git · uv · VS Code · Node.js)은 Notion 강의 허브의 "환경 설정 가이드"를 참조하세요.

---

## 주요 링크

- [Sepolia Etherscan](https://sepolia.etherscan.io) — 컨트랙트/트랜잭션 검증의 주(主) 경로
- [Speed Run Ethereum](https://speedrunethereum.com) — 9주차 SRE 맛보기 실습 참고
