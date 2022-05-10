# Python program to create Blockchain
 
# For timestamp
import datetime
 
# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib
 
# To store data
# in our blockchain
import json
import uuid
import base64
import merkletools

mt = merkletools.MerkleTools(hash_type="sha256")  # default is sha256 
 
class Blockchain:
   
    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        #self.chain = []
        self.memPool = {}
        time = str(datetime.datetime.now())
        self.createBlock(prev_block_height=0, prev_hash="00000000")
        vouchingUserId = "0000000000000000000000000"
        self.createNewCitizen(time, vouchingUserId, {"age":33})
        self.editCitizenData(time, vouchingUserId, vouchingUserId, {"gender":"male"})
        #print("merkle root")
        #print(self.get_merkle_root(self.memPool))
        #self.createNewCitizen(time, hashlib.sha256(time.encode("utf-8")).hexdigest(), {"age":33})
        #self.create_block(proof=1, previous_hash='0')
 

    def makeTransaction(self, type, subtype, initiator_address, recipient_address, data):
        if type == "CREATE":
            #ADD NEW CITIZEN OR ORGANIZATION TO COMMUNE
            #USED TO CREATE CORPORATIONS
            #INITIATOR_ADDRESS IS USER ID OF USER WHO VOUCHED FOR NEW USER, RECIPIENT ADDRESS IS LAW ID
            if subtype=="USER":
                transaction = {"type":"CREATE", "subtype":"USER", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ADD NEW LAW 
            #INITIATOR_ADDRESS IS USER ID OF LAW PROPOSER, RECIPIENT ADDRESS IS LAW ID
            elif subtype=="LAW":
                transaction = {"type":"CREATE", "subtype":"LAW", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ADD NEW ASSET TO GROSS COMMUNE PRODUCT GDP
            #INITIATOR_ADDRESS IS BLANK, RECIPIENT ADDRESS IS WALLET ADDRESS WHERE ASSET LIVES
            #THIS TYPE OF TRANSACTION IS USED WHEN A BLOCK IS MINED, UBI IS DISTRIBUTED, OR A NEW PRODUCT IS GENERATED OR FOUND
            elif subtype=="ASSET":
                transaction = {"type":"CREATE", "subtype":"ASSET", "initiator":initiator_address, "recipient": recipient_address, "data": data}
           #CREATE NEW COURT CASE
           #INITIATOR IS PERSON INITIATING DISPUTE, RECIPIENT IS ENTITY RECEIVING DISPUTE
            elif subtype=="COURTCASE":
                transaction = {"type":"CREATE", "subtype":"COURTCASE", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            else:
                print("no subtype, no tx")
        elif type == "EDIT":
            #CHANGE USER DATA
            #INITIATOR_ADDRESS IS USER ID OF USER WHO EDITED USER, RECIPIENT ADDRESS IS TARGET USER ID
            if subtype=="USER":
                transaction = {"type":"EDIT","subtype":"USER", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #CHANGE EXISTING LAW
            #INITIATOR_ADDRESS IS USER ID OF USER WHO TRIED TO EDIT LAW, RECIPIENT ADDRESS IS LAW ID TO BE EDITED
            elif subtype=="LAW":
                transaction = {"type":"EDIT", "subtype":"LAW", "initiator":initiator_address, "recipient": recipient_address, "data": data} 
            #ASSETS CANNOT BE EDITED   
            elif subtype=="ASSET":
                print("assets cannot be edits")
            else:
                print("bad transaction")
        elif type == "REMOVE":
            #REMOVE USER FROM COMMUNE
            #INITIATOR IS USER WHO DELETES, RECIPIENT IS USER WHO GETS DELETED
            if subtype=="USER":
                transaction = {"type":"REMOVE","subtype":"USER", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #REPEAL EXISTING LAW
            #INITIATOR_ADDRESS IS USER ID OF USER WHO TRIED TO REPEAL LAW, RECIPIENT ADDRESS IS LAW ID TO BE REPEALED
            elif subtype=="LAW":
                transaction = {"type":"REMOVE", "subtype":"LAW", "initiator":initiator_address, "recipient": recipient_address, "data": data} 
            #CONSUME EXISTING ASSET
            #INITIATOR_ADDRESS IS USER ID OF USER WHO CONSUMED ASSET, RECIPIENT IS ASSET ID
            elif subtype=="ASSET":
                transaction = {"type":"REMOVE", "subtype":"ASSET" , "initiator":initiator_address, "recipient": recipient_address, "data": data}
            else:
                print("rejected")
        elif type == "REALLOCATE":
            #USER CANT BE REALLOCATED
            if subtype=="USER":
                print("user cant be reallocated")
            #LAW CANT BE REALLOCATED
            elif subtype=="LAW":
                print("law cant be reallocated")
            #ASSETS CAN BE TRANSFERRED FROM USER TO USER
            #ASSET DATA CONTAINED IN DATA
            elif subtype=="ASSET":
                transaction = {"type":"REALLOCATE", "subtype":"ASSET" , "initiator":initiator_address, "recipient": recipient_address, "data": data}
            else:
                print("rejected")
        else:
            print("BAD TRANSACTION")
        print("binary data")
        print(data)
        print("decoded data")
        print(base64.b64decode(data))
        print("transaction id")
        print(hashlib.sha256(str(transaction).encode('utf-8')).hexdigest())
        #add transaction to memPool
        self.memPool[hashlib.sha256(str(transaction).encode('utf-8')).hexdigest()] = transaction
        #print(self.memPool)
        


    def createNewCitizen(self, timestamp, vouchingUserId, citizenData):
        self.makeTransaction("CREATE", "USER", vouchingUserId, hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest(), base64.b64encode(json.dumps(citizenData).encode("utf-8")))

    def editCitizenData(self, timestamp, userIDMakingChange, userIDToChange, changeToMake):
        self.makeTransaction("EDIT", "USER", userIDMakingChange, userIDToChange, base64.b64encode(json.dumps(changeToMake).encode("utf-8")))


    #type can be CREATE, EDIT, REMOVE, REALLOCATE, 
    #initiator_address is a citizenID
    #recipient_address can be lawID, citizenID/ORGNAIZATIONID, COURTCASEID

    
    # This function is created
    # to add further blocks
    # into the chain
    def create_block(self, proof, previous_hash):

        block = {'index': len(self.chain) + 1,
                 'timestamp': datetime.timestamp(datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_merkle_root(self, transactionsInMemPool):
        branches = []
        for txid, tx in transactionsInMemPool.items():
            branches.append(txid)
            #print("txid")
            #print(txid)
        #branches = [t.hash for t in transactions]
        while len(branches) > 1:
            #print("branches")
            #print(branches)
            #print("length of branches")
            #print(len(branches))
            if (len(branches) % 2) == 1:
                branches.append(branches[-1])
                #print(branches)
            for a, b in zip(branches[0::2], branches[1::2]):
                branches = [hashlib.sha256(str(a+b).encode("utf-8")).hexdigest()]
            #print("branches")
            #print(branches)
            #branches = [hashlib.sha256(a + b).hexdigest() for (a, b) in zip(branches[0::2], branches[1::2])]
        return branches[0]



    

    def createBlock(self, prev_block_height, prev_hash):
        #merkle_root = "merkle_root": get_merkle_root(), 
        blockheader = {"version":1, "prev_block_hash":prev_hash, "time": str(datetime.datetime.now()) }
        block = {"header":blockheader, "tx_count":len(self.memPool)}
        return block




    # This function is created
    # to display the previous block
    #def print_previous_block(self):
    #    return self.chain[-1]
       
    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
         
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode("utf-8")).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
 
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded_block).hexdigest()
 
    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
         
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
               
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode("utf-8")).hexdigest()
             
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
         
        return True

# Creating the Web
# App using flask
#app = Flask(__name__)
 
# Create the object
# of the class blockchain
blockchain = Blockchain()
 
# # Mining a new block
# #@app.route('/mine_block', methods=['GET'])
# def mine_block():
#     previous_block = blockchain.print_previous_block()
#     previous_proof = previous_block['proof']
#     proof = blockchain.proof_of_work(previous_proof)
#     previous_hash = blockchain.hash(previous_block)
#     block = blockchain.create_block(proof, previous_hash)
     
#     response = {'message': 'A block is MINED',
#                 'index': block['index'],
#                 'timestamp': block['timestamp'],
#                 'proof': block['proof'],
#                 'previous_hash': block['previous_hash']}
     
#     return jsonify(response), 200
 
# # Display blockchain in json format
# #@app.route('/get_chain', methods=['GET'])
# #def display_chain():
# #   response = {'chain': blockchain.chain,
# #               'length': len(blockchain.chain)}
# #    return jsonify(response), 200
 
# # Check validity of blockchain
# #@app.route('/valid', methods=['GET'])
# def valid():
#     valid = blockchain.chain_valid(blockchain.chain)
     
#     if valid:
#         response = {'message': 'The Blockchain is valid.'}
#     else:
#         response = {'message': 'The Blockchain is not valid.'}
#     print(response)
#     return jsonify(response), 200
 
 
# Run the flask server locally
#app.run(host='127.0.0.1', port=5000)


