// SPDX-License-Identifier: Kevin Calderon
pragma solidity ^0.8.7;

//Contract Import
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol"; 
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";


contract Freelancers is ERC721Enumerable {
    
    ///State Variables
    uint256 public ServiceCount; //Freelance Service Count
    string public CustomerUsername;///Username Customer
    string public FreelancerUsername;///Username Freelancer
    string public ServiceType;///Service Type
    uint public Reviews;///Reviews
    uint public Ratings;///User Rating
    uint8 public totalRating;///Review Count

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
        ///Declaring the constructor
        constructor(string memory _username, string memory _servicetype) ERC721(_username, _servicetype) 
        {
            _username = FreelancerUsername;
            _servicetype = ServiceType;
        }

        function _setTokenURI(uint256 _tokenID, string memory _tokenURI) internal
        {
            require(_exists(_tokenID), "Token ID does not exist to add URI");
            tokenURIs[_tokenID] = _tokenURI;
        }
    
        function mint(address recipient, string memory nftURI, uint _price, uint _tokenID) external
        {
            FreelanceService storage service = servicesAvailable[_tokenID];
            ServiceCount ++;

            uint256 tokenID = totalSupply();
            _mint(recipient,tokenID);
            _setTokenURI(tokenID,nftURI);

            //require(_tokenID > 0 && _tokenID <= ServiceCount, "service doesn't exist");
            //require(!service.listed, "service already listed");
            
            //update service to sold
            service.listed = true;

            //Add New Services to Freelancer Services
            servicesAvailable[ServiceCount] = FreelanceService(
                _tokenID,
                _price,
                payable(msg.sender),
                false);

        }

        function tokenURI(uint256 _tokenID) public view virtual override returns(string memory)
        {
            require(_exists(_tokenID), "Token ID does not exist");
            string memory _tokenURI = tokenURIs[_tokenID];
            return _tokenURI;
        }



        function purchaseService(uint256 _tokenID, uint256 _price) external payable 
        {
            Sale storage sales = Sales[_tokenID];
            uint256 _totalPrice = _price;
            require(_tokenID > 0 && _tokenID <= ServiceCount, "service doesn't exist");
            require(msg.value >= _totalPrice, "not enough ether to cover service price and platform fee");
            ///Pay Freelancer
            sales.seller.transfer(sales.price);
            ///transfer NFT to buyer
            sales.nft.transferFrom(address(this), msg.sender, sales.tokenId);
        }


        function userRating(uint _totalreviews, uint _amountofservice, uint _totalrating) view internal returns(uint8) 
        {
            _totalreviews = Reviews / ServiceCount;
            _amountofservice = ServiceCount;
            _totalrating = Reviews;
            return(totalRating);
        }
}