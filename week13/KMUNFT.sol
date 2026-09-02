// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title KMUNFT
 * @notice 13주차 실습 — ERC-721 NFT 발행
 *
 * 학습 목표:
 *   - ERC-721 표준: tokenId 기반 고유 소유권
 *   - ERC-721URIStorage: tokenURI로 메타데이터 연결
 *   - IPFS & Pinata: 탈중앙 파일 저장 개념
 *   - OpenSea Testnet에서 NFT 확인
 *
 * 배포: Remix IDE → Injected Provider (MetaMask Sepolia)
 */

// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.0.0/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.0.0/contracts/access/Ownable.sol";
import "@openzeppelin/contracts@5.0.0/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts@5.0.0/access/Ownable.sol";
contract KMUNFT is ERC721URIStorage, Ownable {

    // ── State ──
    uint256 private _tokenIdCounter;
    uint256 public  constant MAX_SUPPLY = 100;   // 최대 100개 NFT

    // ── Events ──
    event NFTMinted(address indexed to, uint256 tokenId, string tokenURI);

    constructor()
        ERC721("KMU NFT", "KMUNFT")
        Ownable(msg.sender)
    {}

    /**
     * @notice NFT 민팅 (소유자만)
     * @param to        수신 주소
     * @param tokenURI  메타데이터 URI (IPFS 또는 HTTP)
     * @return tokenId  발행된 토큰 ID
     *
     * 사용 예시:
     *   to      = 0x내주소
     *   tokenURI = "https://gateway.pinata.cloud/ipfs/[CID]"
     */
    function mintNFT(address to, string memory tokenURI)
        public
        onlyOwner
        returns (uint256)
    {
        require(_tokenIdCounter < MAX_SUPPLY, "Max supply reached");

        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        _mint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);

        emit NFTMinted(to, tokenId, tokenURI);
        return tokenId;
    }

    /**
     * @notice 현재까지 발행된 NFT 총 수량
     */
    function totalMinted() public view returns (uint256) {
        return _tokenIdCounter;
    }

    /**
     * @notice 특정 주소가 보유한 NFT 목록 조회 (최대 10개)
     * @dev 대규모 컬렉션에는 적합하지 않음 (교육용 단순 구현)
     */
    function tokensOfOwner(address ownerAddr)
        public
        view
        returns (uint256[] memory)
    {
        uint256 balance = balanceOf(ownerAddr);
        uint256[] memory tokens = new uint256[](balance);
        uint256 count = 0;

        for (uint256 i = 0; i < _tokenIdCounter && count < balance; i++) {
            if (ownerOf(i) == ownerAddr) {
                tokens[count] = i;
                count++;
            }
        }
        return tokens;
    }
}

/**
 * ─────────────────────────────────────────────
 * ERC-721 핵심 함수 (OpenZeppelin 구현)
 * ─────────────────────────────────────────────
 *
 * function ownerOf(uint256 tokenId)     → 소유자 주소
 * function tokenURI(uint256 tokenId)    → 메타데이터 URI
 * function balanceOf(address owner)     → 보유 NFT 수
 * function transferFrom(from, to, id)   → NFT 이전
 * function approve(to, tokenId)         → 위임 승인
 * function safeTransferFrom(from, to, id)
 *
 * event Transfer(from, to, tokenId)
 * event Approval(owner, approved, tokenId)
 *
 * ─────────────────────────────────────────────
 * NFT 메타데이터 JSON 형식 (ERC-721 Metadata Standard)
 * ─────────────────────────────────────────────
 *
* {
*    "name": "KMU NFT #본인_학번_끝네자리",
*    "description": "계명대학교 분산시스템 특강 NFT",
*    "image": "ipfs://본인_이미지_CID",
*    "attributes": [
*        { "trait_type": "Course", "value": "A2037-01" },
*        { "trait_type": "Student", "value": "본인 이름" },
*        { "trait_type": "Semester", "value": "2026 Spring" }
*    ]
* }
*/