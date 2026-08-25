/**
 * week12/scripts/interact.js
 * ===========================
 * ethers.js v6 — SimpleStorage 컨트랙트 연동 실습
 *
 * 실행 방법 (Windows PowerShell / macOS 터미널 모두 동일):
 *   node scripts\interact.js
 *
 * 사전 조건:
 *   1. npx hardhat node 가 별도 창에서 실행 중일 것
 *   2. scripts\deploy.js 로 배포 완료 후 .env 에 주소 기록
 *      또는 아래 CONTRACT_ADDRESS 상수를 직접 수정
 *
 * .env 파일 (week12\.env):
 *   CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
 */

"use strict";
require("dotenv").config();   // .env 자동 로드 (OS 무관)

const { ethers } = require("ethers");
const path = require("path");
const fs = require("fs");

// ── 설정 ──────────────────────────────────────────────────────────────
// CONTRACT_ADDRESS 우선순위:
//   1. .env 파일의 CONTRACT_ADDRESS 값
//   2. 아래 fallback 주소 (Hardhat 로컬 기본 첫 번째 배포 주소)
const CONTRACT_ADDRESS =
  process.env.CONTRACT_ADDRESS ||
  "0x5FbDB2315678afecb367f032d93F642f64180aa3";

// Hardhat 로컬 네트워크 기본 테스트 계정 #0 개인키
const PRIVATE_KEY =
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";

const RPC_URL = "http://127.0.0.1:8545";


// ── ABI 로드 ──────────────────────────────────────────────────────────
// hardhat compile 후 artifacts 폴더에서 ABI 자동 읽기
const artifactPath = path.join(
  __dirname,
  "..",
  "artifacts",
  "contracts",
  "SimpleStorage.sol",
  "SimpleStorage.json"
);

if (!fs.existsSync(artifactPath)) {
  console.error("❌ artifacts 없음 — 먼저 실행: npx hardhat compile");
  process.exit(1);
}
const { abi } = JSON.parse(fs.readFileSync(artifactPath, "utf8"));


// ── 메인 실행 ─────────────────────────────────────────────────────────
async function main() {
  console.log("=".repeat(55));
  console.log("  12주차 — ethers.js 스마트 컨트랙트 연동 실습");
  console.log("=".repeat(55));

  // 1. Provider: 블록체인 읽기 전용 연결
  console.log("\n1. Provider 연결 (로컬 Hardhat 네트워크)");
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const network = await provider.getNetwork();
  console.log(`   Chain ID: ${network.chainId}`);

  // 2. Signer: 트랜잭션 서명 가능한 지갑
  console.log("\n2. Signer 설정");
  const signer = new ethers.Wallet(PRIVATE_KEY, provider);
  console.log(`   지갑 주소: ${signer.address}`);
  const balance = ethers.formatEther(await provider.getBalance(signer.address));
  console.log(`   잔액: ${balance} ETH`);

  // 3. Contract 인스턴스 생성
  console.log("\n3. Contract 연결");
  console.log(`   주소: ${CONTRACT_ADDRESS}`);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, abi, signer);

  // 4. 이벤트 리스너 등록 (쓰기 함수 호출 전에 등록)
  console.log("\n4. 이벤트 리스너 등록");
  contract.on("NumberSet", (by, value) => {
    console.log(`\n   📢 이벤트 수신: NumberSet`);
    console.log(`      호출자: ${by}`);
    console.log(`      새 값:  ${value}`);
  });

  // 5. 읽기 함수 호출 (view — 가스 없음)
  console.log("\n5. 읽기 함수 호출 (view)");
  const current = await contract.getNumber();
  console.log(`   현재 저장값: ${current}`);

  // 6. 쓰기 함수 호출 (transaction — 가스 사용)
  console.log("\n6. 쓰기 함수 호출 (setNumber)");
  console.log("   setNumber(777) 호출 중...");
  const tx = await contract.setNumber(777n);
  console.log(`   TX 해시: ${tx.hash}`);

  // tx.wait(): 트랜잭션이 블록에 포함될 때까지 대기
  const receipt = await tx.wait();
  console.log(`   ✅ 블록 번호: ${receipt.blockNumber}`);
  console.log(`   ✅ 가스 사용: ${receipt.gasUsed} gas`);

  // 7. 변경된 값 확인
  console.log("\n7. 변경 후 값 확인");
  const updated = await contract.getNumber();
  console.log(`   현재 저장값: ${updated}`);

  // 이벤트 수신 대기 (1초)
  await new Promise((r) => setTimeout(r, 1000));

  console.log("\n" + "=".repeat(55));
  console.log("  실습 완료!");
  console.log("=".repeat(55));

  process.exit(0);
}

main().catch((err) => {
  console.error("❌ 오류:", err.message);
  process.exit(1);
});
