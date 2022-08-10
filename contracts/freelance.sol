// SPDX-License-Identifier: Kevin Calderon

pragma solidity ^0.8.7;

//Contract Import
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol";

contract Amana is ERC721Enumerable {
    ///State Variables
    address payable public immutable feeAccount; //Freelancer Developers Account
    uint256 public immutable feePercent; ///Fee Percent Per Service
    uint256 public ServiceCount; //Freelance Service Count
    string public CustomerUsername;///Username Customer
    string public FreelancerUsername;///Username Freelancer
    string public ServiceType;///Service Type
    uint public Reviews;///Reviews
    uint public Ratings;///User Rating
    uint8 public totalRating;///Review Count
    uint public balanceReceived;

    ///Creating a Mapping for Customers, Freelancers, Services, Review, Rating & Token URIs
    mapping(uint => Customer) public Customers;
    mapping(uint => Freelancer) public FreelancersAvailable;
    mapping(uint => FreelanceService) public servicesAvailable;
    mapping (uint256 => string) public tokenURIs;
    mapping(uint => Sale) public Sales;

    ///Struct for the Customers - Question to Steve About How to Create Unique Username
    struct Customer{
        string CustomerUsername;
        address CustomerWallet;
        uint256 CusID;
        uint256 UsernameID;
    }

    ///Struct for the Freelancers
    struct Freelancer{
        string FreelanceUsername;
        address payable seller;
        string AboutMe;
        uint256 FreeID;
        uint32 ExperienceYears;
        uint256 FreelanceCount;
        uint8 FreelanceRating;/// - Question to Steve About How to Ban for >3 Stars?
    }

    ///Struct for the Freelancers Services
    struct FreelanceService{
        uint256 tokenID;
        uint256 price;
        address payable FreelancerWallet;
        bool listed;
    }

    ///Struct for Sale
        struct Sale{
        uint256 tokenId;
        IERC721 nft;
        uint256 price;
        address payable seller;
        address payable buyer;
        uint date;
    }

    
    constructor(string memory _name, string memory _symbol, uint8 _feePercent) ERC721(_name,_symbol) payable
    {
        feeAccount = payable(msg.sender);
        feePercent = _feePercent;
    }

    function _setTokenURI(uint256 _tokenID, string memory _tokenURI) internal{
        require(_exists(_tokenID), "Token ID does not exist to add URI");
        tokenURIs[_tokenID] = _tokenURI;
    }

    function tokenURI(uint256 _tokenID) public view virtual override returns(string memory){
        require(_exists(_tokenID), "Token ID does not exist");
        string memory _tokenURI = tokenURIs[_tokenID];
        return _tokenURI;
    }

    ///Function for mint a Freelancing Service, set the tokenID and Price
    function mint(string memory nftURI, uint _price, uint _tokenID) public {
        FreelanceService storage service = servicesAvailable[_tokenID];

        ///Increment Freelance Service Count
        ServiceCount ++;

        _mint(address(this),_tokenID);
        _setTokenURI(_tokenID,nftURI);

        require(_tokenID > 0 && _tokenID <= ServiceCount, "service doesn't exist");

        ////update service to sold
        service.listed = true;

        ///Add New Services to Freelancer Services
        servicesAvailable[ServiceCount] = FreelanceService(
            _tokenID,
            _price,
            payable(msg.sender),
            false
        );
    }

    ///Function to Purchase a Freelancing Service
    function purchaseService(uint256 _tokenID) external payable {

        require(_exists(_tokenID), "Token ID does not exist");

        uint256 totalPrice = Sales[_tokenID].price + (Sales[_tokenID].price / 100 * 5);

        require(msg.value >= totalPrice, "not enough ether to cover service price and platform fee");
        _transfer(address(this), msg.sender, _tokenID);
    }


    function receiveMoney() public payable {
        balanceReceived += msg.value;
    }


    function getBalance() public view returns(uint) {
        return address(this).balance;
    }


    function withdrawMoney() public {
        address payable seller = payable(msg.sender);
        seller.transfer(getBalance());
    }


    function withdrawMoneyTo(address payable seller) public {
        seller.transfer(getBalance());
    }

    
    function userRating(uint _totalreviews, uint _amountofservice, uint _totalrating) view internal returns(uint8) {
        _totalreviews = Reviews / ServiceCount;
        _amountofservice = ServiceCount;
        _totalrating = Reviews;
        return(totalRating);
    }
}