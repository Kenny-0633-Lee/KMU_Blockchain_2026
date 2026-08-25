/**
 * week12/scripts/deploy.js
 * interact.js 실행 전 이 스크립트로 먼저 배포
 *
 * 실행:
 *   npx hardhat run scripts/deploy.js --network localhost
 */

const { ethers } = require("hardhat");

async function main() {
  const initialValue = 42n;
  console.log(`SimpleStorage 배포 중 (초기값: ${initialValue})...`);

  const contract = await ethers.deployContract("SimpleStorage", [initialValue]);
  await contract.waitForDeployment();

  const addr = await contract.getAddress();
  console.log(`\n✅ 배포 완료: ${addr}`);
  console.log(`\n📋 interact.js 실행 시 이 주소를 CONTRACT_ADDRESS 환경변수로 설정하거나`);
  console.log(`   scripts/interact.js의 CONTRACT_ADDRESS 변수에 직접 입력하세요.`);
}

main().catch(console.error);
