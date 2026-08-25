// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SimpleStorage
 * @notice 10주차 실습 — Solidity 첫 스마트 컨트랙트
 *
 * 학습 목표:
 *   - Solidity 기본 문법: state variable, function, modifier
 *   - 읽기(view) vs 쓰기 함수 차이 (가스 소비 여부)
 *   - event와 emit — 트랜잭션 로그 기록
 *   - Remix IDE에서 컴파일 → 배포 → 함수 호출 실습
 *
 * 배포: Remix IDE → Injected Provider (MetaMask Sepolia)
 */
contract SimpleStorage {

    // ── State Variables (블록체인에 영구 저장) ──
    uint256 private storedNumber;          // 저장할 숫자
    string  private storedMessage;         // 저장할 메시지
    address public  owner;                 // 컨트랙트 소유자
    uint256 public  updateCount;           // 업데이트 횟수

    // ── Events (트랜잭션 로그) ──
    event NumberUpdated(address indexed by, uint256 oldValue, uint256 newValue);
    event MessageUpdated(address indexed by, string newMessage);

    // ── Constructor ──
    constructor(uint256 _initialNumber) {
        storedNumber = _initialNumber;
        storedMessage = "Hello, Blockchain!";
        owner = msg.sender;
        updateCount = 0;
    }

    // ── Modifier ──
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    // ── Write Functions (가스 소비) ──

    /**
     * @notice 숫자 저장
     * @param _number 저장할 새 숫자
     */
    function setNumber(uint256 _number) public {
        uint256 old = storedNumber;
        storedNumber = _number;
        updateCount += 1;
        emit NumberUpdated(msg.sender, old, _number);
    }

    /**
     * @notice 메시지 저장 (소유자만 가능)
     * @param _message 저장할 메시지 문자열
     */
    function setMessage(string memory _message) public onlyOwner {
        storedMessage = _message;
        emit MessageUpdated(msg.sender, _message);
    }

    /**
     * @notice 숫자를 1 증가
     */
    function increment() public {
        uint256 old = storedNumber;
        storedNumber += 1;
        updateCount += 1;
        emit NumberUpdated(msg.sender, old, storedNumber);
    }

    /**
     * @notice 숫자를 초기화 (소유자만)
     */
    function reset() public onlyOwner {
        uint256 old = storedNumber;
        storedNumber = 0;
        updateCount += 1;
        emit NumberUpdated(msg.sender, old, 0);
    }

    // ── Read Functions (가스 없음) ──

    /**
     * @notice 저장된 숫자 반환
     */
    function getNumber() public view returns (uint256) {
        return storedNumber;
    }

    /**
     * @notice 저장된 메시지 반환
     */
    function getMessage() public view returns (string memory) {
        return storedMessage;
    }

    /**
     * @notice 현재 상태 전체 반환
     */
    function getState() public view returns (
        uint256 number,
        string memory message,
        address contractOwner,
        uint256 count
    ) {
        return (storedNumber, storedMessage, owner, updateCount);
    }
}
