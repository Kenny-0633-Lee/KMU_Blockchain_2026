// hardhat.config.js
// dotenv를 require하면 .env 파일을 OS 무관하게 자동 로드합니다.
// Windows PowerShell에서 "source .env" 불필요 — 이 한 줄이 대신합니다.
require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: { chainId: 31337 },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "https://rpc.sepolia.org",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
};
