import os
import json
from web3 import Account, Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import requests
import user as usr

load_dotenv()

# Create a W3 Connection
#w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))    #Rinkerby
w3 = Web3(Web3.HTTPProvider(os.getenv("GANACHE")))               #Ganache
private_key = os.getenv("PRIVATE_KEY")
#contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

def generate_account(w3,private_key):
    account = Account.privateKeyToAccount(private_key)
    return account

# Set up Pinata Headers
json_headers = {
    "Content-Type":"application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY")
}

file_headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY")
}

def convert_data_to_json(content):
    data = {"pinataOptions":{"cidVersion":1}, 
            "pinataContent":content }
    return json.dumps(data)

def pin_file_to_ipfs(data):
    r = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS",
                      files={'file':data},
                      headers= file_headers)
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def pin_json_to_ipfs(json):
    r = requests.post("https://api.pinata.cloud/pinning/pinJSONToIPFS",
                      data=json,
                      headers= json_headers)
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def pin_service(service_name, documents,**kwargs):
    if documents is not None:
        # Pin service documents to IPFS
        ipfs_file_hash = pin_file_to_ipfs(documents.getvalue())
        # Build our NFT Token JSON
        token_json = {
            "name": service_name,
            "image": f"ipfs.io/ipfs/{ipfs_file_hash}"
            }
    else:
        token_json = {
            "name": service_name,
            "image": None
        }

    # Add extra attributes if any passed in
    token_json.update(kwargs.items())
    # print(token_json)
    # Convert json to pinata format json
    json_data = convert_data_to_json(token_json)

    # Pin the real NFT Token JSON
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash, token_json

def get_account():
    account = generate_account(w3,private_key)
    return account

def get_nonce(account):
    nonce = w3.eth.get_transaction_count(account)
    return nonce

def wait_for_receipt(tx_hash):
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt


######################################################################
## Load the contract
######################################################################

@st.cache(allow_output_mutation=True)
def load_contract():
    #with open(Path("./contracts/compiled/amana_abi.json1")) as file:
    with open(Path("./contracts/compiled/amana_abi.json")) as file:
        amana_abi = json.load(file)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    freelancer_contract = w3.eth.contract(address=contract_address,
                    abi=amana_abi)

    return freelancer_contract            
    

######################################################################
## Streamlit Inputs
######################################################################
# Load the contract
if st.session_state.Freelancer:
    st.markdown("""
                <h4 style='text-align: left; color: red;'
                >You must be a client to perform purchases!</h4>""", unsafe_allow_html=True)

elif not st.session_state.loggedIn:
        st.markdown("""
                <h4 style='text-align: left; color: red;'
                >You must be logged in to use this function!</h4>""", unsafe_allow_html=True)
else:
    contract = load_contract()

    # Pull in Ethereum Account - Used for signing transactions
    st.markdown("<h1 style='text-align: center; color: lightblue;'>Welcome to AMANA</h1>", unsafe_allow_html=True)
    st.markdown("""<h5 style='text-align: left; color: lightgreen;'
                   >Purchases a service</h5>""", unsafe_allow_html=True)

    account = generate_account(w3,private_key)
    #st.write("Loaded Account Address: ", account.address)
    #st.write("Smart Contract Address: ", contract_address)
   
    st.write(f"Freelancer's name: {st.session_state.selFreelancer}")
    client_account = st.text_input("Enter Freelancer's Account Address: ")
    st.write(f"Selected area of expertise is : {st.session_state.area_exp}")
    st.write(f"Purchasing token ID is : {st.session_state.token_id}")
    # rate = st.number_input("Enter the Service Rate in USDT: ")
    
    # Upload a document
    file = st.file_uploader("Upload a document", type=None)


    ######################################################################
    ## Button to Register service
    ######################################################################

    if st.button("Purchase Service"):
 
        service_ipfs_hash,token_json = pin_service(st.session_state.area_exp, file, 
                TokenID=st.session_state.token_id, freelancer_name = st.session_state.selFreelancer
                )

        service_uri = f"ipfs.io/ipfs/{service_ipfs_hash}"
        nonce = w3.eth.get_transaction_count(account.address)

        #For Ganache
        tx_hash = contract.functions.purchaseService(st.session_state.token_id
                                          ).transact({'from':client_account,'gas':1000000})

        # This generally works on the mainnet - Rinkeby, not so much
        try:
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        except w3.exceptions.SolidityError as error:
            print(f"Error --> {error}")

        #receipt = w3.eth.waitForTransactionReceipt(tx_hash,timeout=300)
        usr.RegisterService(st.session_state.User, st.session_state.area_exp, service_uri, token_json['image'])

        st.write("Service Registered on the Blockchain!")
        st.write(dict(receipt))

        st.write("You can view the service posted with the following links")
        st.markdown(f"[Service IPFS Gateway Link] (https://{service_uri})")
        st.markdown(f"[Service IPFS Image Link] (https://{token_json['image']})")




