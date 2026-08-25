# 📊 KMU_Blockchain_2026 — 커리큘럼 현황 & TODO

**계명대학교 대학원 컴퓨터공학과 | Special Topics on Distributed Systems (A2037-01) | 2026년 2학기**

*최종 업데이트: 2026-08-25 | 문서 버전: v1.0*

> 이 문서는 KNU `blockchain_curriculum_vXXX.md` + `vXXX_matrix_todo.md` 두 파일을 통합·축약한 것입니다.
> **Single Source of Truth = Notion 허브** (비공개 초대제). 이 문서와 Notion 내용이 다르면 Notion이 기준입니다.

---

## 범례

| 기호 | 의미 |
|------|------|
| ✅ | 작성 완료 (Notion 배포까지 완료) |
| 📥 | 콘텐츠 확보 완료 (KNU 원본 재사용/각색, Notion 배포 대기) |
| 🔄 | 수정 필요 (KNU 원본에 알려진 오류/구식 정보 있음) |
| ⬜ | 미착수 (신규 제작 필요, KNU에 대응 콘텐츠 없음) |
| — | 해당 없음 |

---

## 변경 이력

| 버전 | 날짜 | 주요 변경 |
|------|------|----------|
| v1.0 | 2026-08-25 | KNU→KMU 레포 이관, 15주 재설계(연구트랙 도입), 평가구조 확정(10/30/40/20), Sparrow Wallet 오류 수정, 이 문서 최초 작성 |

---

## 1. 주차별 콘텐츠 현황

| 주 | 주제 | KNU 소스 | 상태 | 비고 |
|:--:|------|----------|:----:|------|
| 1 | Orientation | week01 | 📥 | 대학원용 축약 필요 |
| 2 | Blockchain101+Decentralization+Merkle | week02+03 병합 | 📥 | — |
| 3 | 연구분야 소개+평가방법 안내 | 없음 | ⬜ | 신규 제작 |
| 4 | Symmetric Crypto (SHA-256+AES) | week04 | ✅ | 그대로 재사용, 검증 완료 |
| 5 | Asymmetric Crypto (ECDSA+BIP-39) | week05 | ✅ | 그대로 재사용, 검증 완료 |
| 6 | 연구주제 선정+프로포절 발표 | 없음 | ⬜ | 신규 제작, 템플릿 불필요(Notion 안내만) |
| 7 | Consensus+Bitcoin Architecture | week06+week08(KNU 신주차번호 기준) | 🔄→✅ | **Electrum→Sparrow Wallet 수정 완료 (2026-08-25)** |
| 8 | Ethereum+Smart Contracts (Remix) | week09+10 | 📥 | — |
| 9 | Web3+DApp (Hardhat) | week11+12 | 📥 | KNU 원본 Hardhat 버전 확인 필요 (v2 확정 여부) |
| 10 | 연구발표 A+논문발제 | 없음 | ⬜ | 수강인원 확정 후 세부구조 결정 |
| 11 | ERC-20 | week13 (KMUToken.sol) | ✅ | 리브랜딩 완료, Remix 유지 확정 |
| 12 | 연구발표 B+논문발제 | 없음 | ⬜ | 〃 |
| 13 | NFT & ERC-721 | week14 (KMUNFT.sol) | ✅ | 리브랜딩 완료, Remix 유지 확정 |
| 14 | 연구발표 C+논문발제 | 없음 | ⬜ | 〃 |
| 15 | 연구발표 D+종합정리 | 없음 | ⬜ | 신규 제작 |

**요약**: ✅완료 5 · 📥재사용확보 4 · ⬜신규필요 6 · 🔄수정중 0

---

## 2. 외부 의존성 감사 (Known Risks)

| 항목 | 현재 상태 | 리스크 | 대응 |
|------|----------|--------|------|
| Sepolia Testnet | 사용 중 | **EOL 예상 2026-09-30**, 개강 시점과 겹침 | 개강 직전(8월 말) 재확인 예정, setup 문서에 각주 반영 완료 |
| Bitcoin 지갑 도구 | Sparrow Wallet | KNU 구버전 자료에 Electrum 잔존 가능성 | week07 수정 완료, 다른 주차 작성 시 재확인 |
| Hardhat 버전 | KMU는 미사용(Remix 유지) | 해당없음 | week09(Web3+DApp)에서만 Hardhat 사용 — KNU 원본이 v2/v3 중 무엇인지 확인 필요 |
| Node.js | v22 LTS 가정 | KNU 구버전 자료에 v20 언급 가능성 | 문서 작성 시 확인 |
| Rarible/OpenSea | testnet.rarible.com 사용 | 낮음 (KNU에서 이미 검증됨) | — |

---

## 3. 우선순위별 TODO

### 🔴 다음 작업 (즉시)
- [ ] 신규 연구주차(3·6·10·12·14·15) README 내용 보강 여부 결정
- [ ] 루트 README.md 대학원용 전면 개편

### 🟠 개강 전 필요
- [ ] Notion 허브 랜딩페이지 최종 반영 (LMS 주소 포함)
- [ ] week09(Web3+DApp) KNU 원본의 Hardhat 버전 확인 (v2/v3)
- [ ] Sepolia EOL 최신 상태 재확인 (8월 말)
- [ ] week01/week08 README 대학원 맥락으로 축약

### 🟡 중간(6주, 프로포절) 이후
- [ ] 연구발표 A~D(10/12/14/15주) 세부 운영구조 확정 (수강인원 기준)
- [ ] 7주차(Consensus+Bitcoin) 실습 밀도 현장 조정 결과 기록

### 🟢 상시
- [ ] KNU 원본 재사용 콘텐츠 작성 시점마다 최신 버전 여부 확인 (Notion이 기준)

---

## 4. 평가 구조 (확정)

| 항목 | 비중 |
|------|:---:|
| 출석 | 10% |
| 프로포절 발표 | 30% |
| 논문발제(연구발표 포함) | 40% |
| 실습실행평가 | 20% |
