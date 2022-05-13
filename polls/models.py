from operator import truediv
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import secrets
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
import sys
import time
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.signing import Signer
from os.path import exists
import numpy as np
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection

class MyOwnNodeConnection (NodeConnection):
    # Python class constructor
     def __init__(self, main_node, sock, id, host, port):
        super(MyOwnNodeConnection, self).__init__(main_node, sock, id, host, port)

class MyOwnPeer2PeerNode (Node):
    # Python class constructor
    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, id, callback, max_connections)

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        print("node_message from " + connected_node.id + ": " + str(data))
        
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")

    # OPTIONAL
    # If you need to override the NodeConection as well, you need to
    # override this method! In this method, you can initiate
    # you own NodeConnection class.
    def create_new_connection(self, connection, id, host, port):
        return MyOwnNodeConnection(self, connection, id, host, port)

# import merkletools
# mt = merkletools.MerkleTools(hash_type="sha256")  # default is sha256 
class Poll(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def user_can_vote(self, user):
        """ 
        Return False if user already voted
        """
        user_votes = user.vote_set.all()
        qs = user_votes.filter(poll=self)
        if qs.exists():
            return False
        return True

    @property
    def get_vote_count(self):
        return self.vote_set.count()

    def get_result_dict(self):
        res = []
        for choice in self.choice_set.all():
            d = {}
            alert_class = ['primary', 'secondary', 'success',
                           'danger', 'dark', 'warning', 'info']

            d['alert_class'] = secrets.choice(alert_class)
            d['text'] = choice.choice_text
            d['num_votes'] = choice.get_vote_count
            if not self.get_vote_count:
                d['percentage'] = 0
            else:
                d['percentage'] = (choice.get_vote_count /
                                   self.get_vote_count)*100

            res.append(d)
        return res

    def __str__(self):
        return self.text


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)

    @property
    def get_vote_count(self):
        return self.vote_set.count()

    def __str__(self):
        return f"{self.poll.text[:25]} - {self.choice_text[:25]}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.poll.text[:15]} - {self.choice.choice_text[:15]} - {self.user.username}'



class MiningNode:
    def __init__(self):
        miningNode = MyOwnPeer2PeerNode("127.0.0.1", 10001)
        time.sleep(1)
        # Do not forget to start your node!
        miningNode.start()
        time.sleep(1)
        # Connect with another node, otherwise you do not create any network!
        miningNode.connect_with_node('127.0.0.1', 10002)
        time.sleep(2)
        # Example of sending a message to the nodes (dict).
        miningNode.send_to_nodes({"message": "Hi there!"})
        time.sleep(5) # Create here your main loop of the application
        miningNode.stop()

        self.previousBlock = {}
        self.miningnodeversion = 1
        self.chain = []
        self.latestBlockHeight = 0
        self.memPool = {}
        self.candidateBlock = {}
        self.tempUser = ""
      

    #create binary data from memPool JSON
    def createCandidateBlock(self, blockheight, proof, prev_hash):
        #header = {version, prev_block_hash/prev_block_merkleroot, thisblocks_merkleroot, time, difficulty, nonce}
        blockheader = {"version":self.miningnodeversion, "proof":proof, "prev_block_height":blockheight+1, "prev_block_hash":prev_hash, "this_block_hash": self.get_merkle_root(self.memPool), "time":datetime.datetime.timestamp(datetime.datetime.now()) }
        print("BLOCK HEADEDR")
        block = {"header":blockheader, "tx_count":len(self.memPool), "transactions":self.memPool}
        self.chain.append(block)
        print("WRITE BLOCK TO FILE")
        bytesfile = base64.b64encode(str(block).encode("utf-8"))
        with open("block"+str(blockheight)+".dat", "wb") as binary_file:
            binary_file.write(bytesfile)
        print(self.memPool)
        print("candidateBlockCreated")

    def get_merkle_root(self, transactionsInMemPool):
        branches = []
        for timestamp, tx in transactionsInMemPool.items():
            print("TX.txid")
            print(tx["txid"])
            branches.append(tx["txid"])
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
        print("in GET MERKLE ROOT")
        print(branches[0])
        if (len(branches) < 1):
            return "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
        return branches[0]

    def makeSureInitiatorIsValidUser(self, initiator_address):
        if(True):
            return True
        else:
            return False

    #type can be CREATE, EDIT, REMOVE, VOTE
    #recipient_address can be lawID, citizenID/ORGNAIZATIONID, COURTCASEID, PRIVELEGEID
    def makeTransaction(self, type, subtype, initiator_address, recipient_address, data):
        #TRANSACTION LOOKS LIKE 
        #{ 122317812112.0121: {"v":1, "txid":"1212412451cab787fe" , "type":CREATE, "subtype":"USER", "initiator":"3243243abc9867876a8001234", "recipient":"21b421b123421b00031", "data":{data}}}
        time = datetime.datetime.timestamp(datetime.datetime.now())
        #create signing object with current time as salt
        txsignature = Signer()
        #UNIQUE IDS CREATE EVERY SINGLE TIME FOR EACH USER RECEIVING NEW PRIVILEGE OR ASSET
        #SINGLE LAW ID OR COURTCASE ID CREATED FOR ENTIRE COMMUNE
        #DATA CAN BE ANYTHING
        if type == "CREATE":
            #ADD NEW CITIZEN OR ORGANIZATION TO COMMUNE
            #USED TO CREATE CORPORATIONS
            #INITIATOR_ADDRESS IS USER ID OF USER WHO VOUCHED FOR NEW USER, RECIPIENT ADDRESS IS LAW ID
            if subtype=="USER":
                transaction = {"type":"CREATE", "subtype":"USER", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ADD NEW LAW 
            #INITIATOR_ADDRESS IS USER ID OF LAW PROPOSER, RECIPIENT ADDRESS IS LAW ID
            #DATA IS EXPLANATION WITH RELATION TO AS MANY ENTITIES AS POSSIBLE
            elif subtype=="LAW":
                transaction = {"type":"CREATE", "subtype":"LAW", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ADD NEW ASSET TO GROSS COMMUNE PRODUCT GDP
            #INITIATOR_ADDRESS IS USERID WHO BECOMES OWNER OF ASSET, RECIPIENT ADDRESS IS WALLET ADDRESS WHERE ASSET LIVES
            #THIS TYPE OF TRANSACTION IS USED WHEN A BLOCK IS MINED, UBI IS DISTRIBUTED, OR A NEW PRODUCT IS GENERATED OR FOUND
            elif subtype=="ASSET":
                if self.makeSureInitiatorIsValidUser(initiator_address):
                    transaction = {"type":"CREATE", "subtype":"ASSET", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #CREATE NEW COURT CASE
            #INITIATOR IS PERSON INITIATING DISPUTE, RECIPIENT IS ENTITY RECEIVING DISPUTE
            #DATA CONTAINS ALL RELEVANT DETAILS
            elif subtype=="COURTCASE":
                transaction = {"type":"CREATE", "subtype":"COURTCASE", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ADD NEW PERMISSION FOR USER
            #INITIATOR IS USER/ORGANIZATION APPROVING PERMIT, RECIPIENT IS USERID OF CITIZEN GAINING NEW PERMISSION
            elif subtype=="PRIVILEGE":
                transaction = {"type":"CREATE", "subtype":"PRIVILEGE", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ADD NEW PERMISSION FOR USER
            #INITIATOR IS USER/ORGANIZATION ID PROPOSING NEW ENTITY, RECIPIENT IS PERMANENT ADDRESS OF NEW ENTITY WHICH WILL BE REFERENCED
            elif subtype=="ENTITY":
                transaction = {"type":"CREATE", "subtype":"ENTITY", "initiator":initiator_address, "recipient": recipient_address, "data": data}
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
            #COURTCASE CANNOT BE EDITED
            elif subtype=="COURTCASE" or subtype=="ENTITY":
                print("courtcase cannot be edited")
            #ASSET EDIT FUNCTIONS AS SENDING DATA AND TRANSFERRING OWNERSHIP!!!!!!!!!!!!!!!!!!!!!!!!
            #INITIATOR IS USER LOSING ASSET OWNERSHIP, RECIPIENT IS USER GAINING ASSET OWNERSHIP
            #DATA CONTAINS ASSET ID e.g. {"ASSETID":"32345r235325h", "ITEM":1}
            #IF ITEM IS INT, PROECSS AS WHUFFIE, IF STRING PROCESS AS ITEM DESCRIPTION
            elif subtype=="ASSET":
                transaction = {"type":"EDIT", "subtype":"ASSET" , "initiator":initiator_address, "recipient":recipient_address, "data":data}
            #EDIT USER PRIVILEGE
            #INITIATOR IS USERID MAKING CHANGE, RECIPIENT IS TRANSACTION ID OF ORIGINAL PRIVELGE
            elif subtype=="PRIVILEGE":
                transaction = {"type":"EDIT", "subtype":"PRIVILEGE", "initiator":initiator_address, "recipient":recipient_address, "data":data}
            else:
                print("bad transaction")
        elif type == "VOTE":
            #DELEGATE VOTING POWER TO OTHER CITIZEN
            #INITIATOR IS USERID OF WHO IS GIVING VOTING POWER, RECIPIENT IS WHO IS RECEIVING VOTING POWER
            if subtype=="USER":
                transaction = {"type":"VOTE","subtype":"USER", "initiator":initiator_address, "recipient":recipient_address, "data":data}
            #VOTE ON LAWS VALIDITY
            #INITIATOR_ADDRESS IS USER ID OF VOTER, RECIPIENT ADDRESS IS LAW ID TO BE VOTED ON
            elif subtype=="LAW":
                transaction = {"type":"VOTE", "subtype":"LAW", "initiator":initiator_address, "recipient":recipient_address, "data":data} 
            #VOTE ON ENTITY VALIDITY
            #INITIATOR_ADDRESS IS USER ID OF VOTER, RECIPIENT ADDRESS IS ENTITY ID TO BE VOTED ON
            elif subtype=="ENTITY":
                transaction = {"type":"VOTE", "subtype":"ENTITY", "initiator":initiator_address, "recipient":recipient_address, "data":data} 
            #CANT VOTE ON ASSETS
            elif subtype=="ASSET":
               print("cant vote on assets")
            #ENDORSE PRIVILEGES
            #INITIATOR_ADDRESS IS USER ID OF VOTER, RECIPIENT ADDRESS IS RIGHT TO BE VOTED ON
            elif subtype=="PRIVILEGE":
                transaction = {"type":"VOTE", "subtype":"PRIVILEGE", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #ANONYMOUS VOTE ON RESULT OF DISPUTE
            #INITIATOR IS COURTCASEID, RECIPIENT IS USER ID OF EITHER PLANTIFF OR DEFENDANT
            elif subtype=="COURTCASE":
                transaction = {"type":"VOTE", "subtype":"COURTCASE", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            else:
                print("rejected")
        elif type == "REMOVE":
            #REMOVE EXISTING USER FROM COMMUNE
            #INITIATOR IS USER WHO DELETES, RECIPIENT IS USER WHO GETS DELETED
            if subtype=="USER":
                transaction = {"type":"REMOVE","subtype":"USER", "initiator":initiator_address, "recipient":recipient_address, "data":data}
            #REPEAL EXISTING LAW
            #INITIATOR_ADDRESS IS USER ID OF USER WHO TRIED TO REPEAL LAW, RECIPIENT ADDRESS IS LAW ID TO BE REPEALED
            elif subtype=="LAW":
                transaction = {"type":"REMOVE", "subtype":"LAW", "initiator":initiator_address, "recipient":recipient_address, "data":data} 
            #CONSUME EXISTING ASSET
            #INITIATOR_ADDRESS IS USER ID OF USER WHO CONSUMED ASSET, RECIPIENT IS ASSET ID
            elif subtype=="ASSET":
                transaction = {"type":"REMOVE", "subtype":"ASSET", "initiator":initiator_address, "recipient":recipient_address, "data":data}
            #RESCIND EXISTING PERMISSION
            #INITIATOR_ADDRESS IS USER ID OF USER LOSING PRIVILEGE, RECIPIENT IS PRIVILEGE ID
            #DATA IS DESCRIPTION E.G. {"desc":"remove voting privilege"}
            elif subtype=="PRIVILEGE":
                transaction = {"type":"REMOVE", "subtype":"PRIVILEGE", "initiator":initiator_address, "recipient": recipient_address, "data": data}
            #COURTCASE AND ENTITIES CANT BE REMOVED
            elif subtype=="COURTCASE" or subtype=="ENTITY":
                print("courtcases and entities cannot be removed")
            else:
                print("rejected")
        else:
            print("BAD TRANSACTION")
        print("transaction id")
        txid = hashlib.sha256(str(transaction).encode('utf-8')).hexdigest()
        print(txid)
        transaction["v"] = self.miningnodeversion
        transaction["txid"] = txid
        #transaction["signature"] = 
        #add transaction to memPool with time as key
        self.memPool[time] = transaction
        print("tx added to mempool")
        return transaction
        # print("binary data")
        # print(data)
        # print("decoded data")
        # print(base64.b64decode(data))
        # print("transaction id")
        # print(hashlib.sha256(str(transaction).encode('utf-8')).hexdigest())
        # #add transaction to memPool
        # self.memPool[hashlib.sha256(str(transaction).encode('utf-8')).hexdigest()] = transaction
        # #print(self.memPool)
        #self.makeTransaction("CREATE", "USER", vouchingUserId, hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest(), base64.b64encode(json.dumps(citizenData).encode("utf-8")))
        
    def createNewCitizen(self, vouchingUserId, citizenData):
        newCitizenId = hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest()
        self.tempUser = newCitizenId
        self.makeTransaction("CREATE", "USER", vouchingUserId, newCitizenId, citizenData)


    def createBasicIncome(self, firstAssetOwner, assetData):
        self.makeTransaction("CREATE", "ASSET", firstAssetOwner, hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest(), assetData)

    #ENTITIES ARE LEGAL DEFINITIONS THAT MUST BE REFERENCED IN LAWS/DISPUTES/ETC
    def createNewEntity(self, lawOrUserCreatingEntity, entityData):
        self.makeTransaction("CREATE", "ENTITY", lawOrUserCreatingEntity, hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest(), entityData)


    def editCitizenData(self, userIDMakingChange, userIDToChange, changeToMake):
        self.makeTransaction("EDIT", "USER", userIDMakingChange, userIDToChange, changeToMake)

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode("utf-8")).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
 
    # def hash(self, block):
    #     encoded_block = json.dumps(block, sort_keys=True).encode("utf-8")
    #     return hashlib.sha256(encoded_block).hexdigest()
 
    # def chain_valid(self, chain):
    #     previous_block = chain[0]
    #     block_index = 1
    #     while block_index < len(chain):
    #         block = chain[block_index]
    #         if block["prev_hash"] != self.hash(previous_block):
    #             return False
    #         previous_proof = previous_block['proof']
    #         proof = block['proof']
    #         hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode("utf-8")).hexdigest()
    #         if hash_operation[:5] != '00000':
    #             return False
    #         previous_block = block
    #         block_index += 1
    #     return True

    # def print_previous_block(self, node):
    #     return node.chain[-1]
       
    # This is the function for proof of work
    # and used to successfully mine the block
    def display_chain(self):
        print("displaychain")
        response = {"chain": self.chain, "length": len(self.chain)}
        return response

    def mine_block(self):
        #get proof of previous block
        previous_block = self.print_previous_block()
        previous_proof = previous_block['proof']

        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)
        block = self.create_block(proof, previous_hash)
        
        response = {'message': 'A block is MINED',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash']}
        return response

    def verifyBlock(self, prev_blockdata, currentblock_prev_hash):
        if (self.get_merkle_root(prev_blockdata)==currentblock_prev_hash):
            return True
        else:
            return False

 



    #blockhash = { 'hash': polls }
    #return render(request, 'polls/polls_list.html', blockhash)

    #     # print("decoded data")
    #     # print(base64.b64decode(data))

# # # Mining a new block
# # #@app.route('/mine_block', methods=['GET'])
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
     
#     return JsonResponse(response)
 
# # # Display blockchain in json format
# # #@app.route('/get_chain', methods=['GET'])
# def display_chain():
#     print("displaychain")
#     response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
#     return response
 
# # # Check validity of blockchain
# # #@app.route('/valid', methods=['GET'])
# def valid():
#     valid = blockchain.chain_valid(blockchain.chain)
     
#     if valid:
#         response = {'message': 'The Blockchain is valid.'}
#     else:
#         response = {'message': 'The Blockchain is not valid.'}
#     print(response)
#     return JsonResponse(response)
 
 
# # Run the flask server locally
# #app.run(host='127.0.0.1', port=5000)


