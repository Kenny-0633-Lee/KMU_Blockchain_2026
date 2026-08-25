// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title KMUToken (KMUT)
 * @notice 13주차 실습 — ERC-20 토큰 발행
 *
 * 학습 목표:
 *   - ERC-20 표준: 6개 필수 함수 + 2개 이벤트
 *   - OpenZeppelin ERC20 기반 컨트랙트 상속
 *   - decimals와 10^18 단위 변환
 *   - approve / transferFrom DeFi 패턴
 *   - Ownable: 소유자 권한 관리
 *
 * 배포: Remix IDE → Injected Provider (MetaMask Sepolia)
 * OpenZeppelin Import: Remix가 자동으로 GitHub에서 다운로드
 */

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract KMUToken is ERC20, Ownable {
    // ── 상수 ──
    uint256 public constant MAX_SUPPLY = 100_000_000 * 10 ** 18; // 1억 KMUT 최대 발행량

    // ── 이벤트 (ERC-20 기본 외 추가) ──
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);

    /**
     * @param initialSupply 초기 발행량 (단위: KMUT, 내부에서 10^18 곱함)
     * constructor 예시: initialSupply = 1000000 → 1,000,000 KMUT 발행
     */
    constructor(
        uint256 initialSupply
    ) ERC20("KMU Token", "KMUT") Ownable(msg.sender) {
        require(
            initialSupply * 10 ** decimals() <= MAX_SUPPLY,
            "Exceeds maximum supply"
        );
        _mint(msg.sender, initialSupply * 10 ** decimals());
        emit TokensMinted(msg.sender, initialSupply * 10 ** decimals());
    }

    /**
     * @notice 추가 발행 (소유자만)
     * @param to      수신 주소
     * @param amount  발행량 (단위: KMUT, 10^18 곱하지 않음)
     */
    function mint(address to, uint256 amount) public onlyOwner {
        require(
            totalSupply() + amount * 10 ** decimals() <= MAX_SUPPLY,
            "Exceeds maximum supply"
        );
        _mint(to, amount * 10 ** decimals());
        emit TokensMinted(to, amount * 10 ** decimals());
    }

    /**
     * @notice 토큰 소각 (자신의 토큰만)
     * @param amount 소각량 (단위: KMUT)
     */
    function burn(uint256 amount) public {
        _burn(msg.sender, amount * 10 ** decimals());
        emit TokensBurned(msg.sender, amount * 10 ** decimals());
    }

    /**
     * @notice 잔액 조회 (사람이 읽기 좋은 단위로)
     * @return KMUT 단위 잔액 (소수점 이하 버림)
     */
    function balanceOfKMUT(address account) public view returns (uint256) {
        return balanceOf(account) / 10 ** decimals();
    }
}

/**
 * ─────────────────────────────────────────────
 * ERC-20 필수 인터페이스 (OpenZeppelin이 구현)
 * ─────────────────────────────────────────────
 *
 * function name()        → "KMU Token"
 * function symbol()      → "KMUT"
 * function decimals()    → 18
 * function totalSupply() → 총 발행량
 * function balanceOf(address) → 주소별 잔액
 * function transfer(address to, uint256 amount)
 * function approve(address spender, uint256 amount)
 * function transferFrom(address from, address to, uint256 amount)
 * function allowance(address owner, address spender)
 *
 * event Transfer(address indexed from, address indexed to, uint256 value)
 * event Approval(address indexed owner, address indexed spender, uint256 value)
 */
