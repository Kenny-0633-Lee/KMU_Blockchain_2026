// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SimpleStorage (Week12 버전)
 * @notice ethers.js 연동 실습을 위한 단순 스토리지 컨트랙트
 */
contract SimpleStorage {
    uint256 private storedNumber;
    event NumberSet(address indexed by, uint256 value);

    constructor(uint256 _initial) {
        storedNumber = _initial;
    }

    function setNumber(uint256 _number) public {
        storedNumber = _number;
        emit NumberSet(msg.sender, _number);
    }

    function getNumber() public view returns (uint256) {
        return storedNumber;
    }
}
