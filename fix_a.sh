#!/bin/bash
set -e

# A-1. pyproject.toml
sed -i 's/name = "blockchain-knu2026"/name = "blockchain-kmu2026"/' pyproject.toml
sed -i 's/version = "0.93.0"/version = "1.0.0"/' pyproject.toml
sed -i 's/description = "경북대학교 블록체인 강의 실습 코드 — ICAB0203-001 (2026년 1학기)"/description = "계명대학교 대학원 블록체인 강의 실습 코드 — A2037-01 (2026년 2학기)"/' pyproject.toml

# A-2. 주차 번호 내부 불일치
sed -i 's/3주차/2주차/g' week02/merkle_tree.py
sed -i 's/6주차/7주차/g' week07/pow_simulator.py
sed -i 's/Week 09/Week 08/' week08/README.md
sed -i 's/10주차/8주차/g' week08/SimpleStorage.sol
sed -i 's/Week 12/Week 09/' week09/README.md
sed -i 's/12주차/9주차/g' week09/package.json week09/scripts/interact.js
sed -i 's/13주차/11주차/g' week11/KMUToken.sol
sed -i 's/14주차/13주차/g' week13/KMUNFT.sol

echo "완료. 아래에서 변경사항 확인:"
echo "---"
git diff --stat
