
Convert Python to C#

namespace Namespace {
    
    using truediv = @operator.truediv;
    
    using User = django.contrib.auth.models.User;
    
    using models = django.db.models;
    
    using timezone = django.utils.timezone;
    
    using secrets;
    
    using datetime;
    
    using hashlib;
    
    using json;
    
    using uuid;
    
    using base64;
    
    using sys;
    
    using time;
    
    using JsonResponse = django.http.JsonResponse;
    
    using HttpResponse = django.http.HttpResponse;
    
    using Signer = django.core.signing.Signer;
    
    using exists = os.path.exists;
    
    using np = numpy;
    
    using Node = p2pnetwork.node.Node;
    
    using NodeConnection = p2pnetwork.nodeconnection.NodeConnection;
    
    using os;
    
    using AsgiHandler = channels.http.AsgiHandler;
    
    using ProtocolTypeRouter = channels.routing.ProtocolTypeRouter;
    
    using AsyncJsonWebsocketConsumer = channels.generic.websocket.AsyncJsonWebsocketConsumer;
    
    using System.Collections.Generic;
    
    using System;
    
    using System.Collections;
    
    public static class Module {
        
        public static object path = "C:/Users/Austin/Documents/GitHub/Django-Poll-App/ledgerdata";
        
        public static object OUTBOUND_PORT = 10001;
        
        public static object INBOUND_PORT = 10002;
        
        public static object BOOTSTRAP_LIST = new List<object> {
            "localhost:5999",
            "localhost:5998",
            "localhost:5997"
        };
        
        public static object node_callback(object @event, object node, object connected_node, object data) {
            try {
                if (@event != "node_request_to_stop") {
                    // node_request_to_stop does not have any connected_node, while it is the main_node that is stopping!
                    Console.WriteLine("Event: {} from main node {}: connected node {}: {}".format(@event, node.id, connected_node.id, data));
                }
            } catch (Exception) {
                Console.WriteLine("FUCKI");
                Console.WriteLine(e);
            }
        }
        
        public class MyOwnNodeConnection
            : NodeConnection {
            
            public MyOwnNodeConnection(
                object main_node,
                object sock,
                object id,
                object host,
                object port)
                : base(sock, id, host, port) {
            }
        }
        
        public class MyOwnPeer2PeerNode
            : Node {
            
            public object latestBlockHeight = 0;
            
            public object previouslyRecordedNodeList = new List<object>();
            
            public MyOwnPeer2PeerNode(
                object host,
                object port,
                object id = null,
                object callback = null,
                object max_connections = 0)
                : base(port, id, callback, max_connections) {
            }
            
            public virtual object outbound_node_connected(object connected_node) {
                Console.WriteLine("outbound_node_connected: " + connected_node.id);
            }
            
            public virtual object inbound_node_connected(object connected_node) {
                Console.WriteLine("inbound_node_connected: " + connected_node.id);
                //self.node_message(connected_node, {"txt":"DO YOU NEED BLOCKDATA?", "blockheight":1})
            }
            
            public virtual object inbound_node_disconnected(object connected_node) {
                Console.WriteLine("inbound_node_disconnected: " + connected_node.id);
            }
            
            public virtual object outbound_node_disconnected(object connected_node) {
                Console.WriteLine("outbound_node_disconnected: " + connected_node.id);
            }
            
            // def node_message(self, connected_node, data):
            //     print("node_message from " + connected_node.id + ": " + str(data))
            public virtual object node_disconnect_with_outbound_node(object connected_node) {
                Console.WriteLine("node wants to disconnect with oher outbound node: " + connected_node.id);
            }
            
            public virtual object node_request_to_stop() {
                Console.WriteLine("node is requested to stop!");
            }
            
            public virtual object node_message(object connected_node, object data) {
                Console.WriteLine(data["txt"]);
                Console.WriteLine("FIRST SERVERRRRRRRRRRRRRRRRRRRRRRRRRRRRRR");
                Console.WriteLine("node_message from " + connected_node.id + ": " + data["txt"].ToString());
                //print(str(data['blockheight']))
                if (data["txt"].ToString() == "GET BLOCKDATA FILE") {
                    Console.WriteLine("request to send blockdata for block number ");
                    Console.WriteLine(data["blockheight"]);
                    var blockdata = new Dictionary<object, object> {
                    };
                    var file = "ledgerdata\\block" + data["blockheight"].ToString() + ".dat";
                    if (exists(file)) {
                        using (var datfile = open(file)) {
                            Console.WriteLine("loading datafile to send to peer");
                            lines = datfile.readlines();
                            foreach (var line in lines) {
                                my_json = base64.b64decode(line).decode("utf-8").replace("'", "\"");
                                blockdata += my_json;
                            }
                        }
                        connected_node.node_message(this, new Dictionary<object, object> {
                            {
                                "txt",
                                "RECEIVE BLOCKDATA FILE"},
                            {
                                "blockdata",
                                blockdata}});
                    } else {
                        connected_node.node_message(this, new Dictionary<object, object> {
                            {
                                "txt",
                                "FILE NOT FOUND"}});
                    }
                } else if (data["txt"].ToString() == "RECEIVE BLOCKDATA FILE") {
                    Console.WriteLine(data["blockdata"].ToString());
                } else if (data["txt"].ToString() == "GET LATEST BLOCKHEIGHT") {
                    connected_node.node_message(this, new Dictionary<object, object> {
                        {
                            "txt",
                            "RECEIVE LATEST BLOCKHEIGHT"},
                        {
                            "blockheight",
                            this.latestBlockHeight}});
                } else if (data["txt"].ToString() == "RECEIVE LATEST BLOCKHEIGHT") {
                    Console.WriteLine("received latest block height");
                    Console.WriteLine(data["blockheight"]);
                    this.latestBlockHeight == data["blockheight"];
                } else if (data["txt"].ToString() == "FILE NOT FOUND") {
                    Console.WriteLine("could not locate that block, try the next one maybe?");
                } else if (data["txt"].ToString() == "GET PEERNODE LIST") {
                    connected_node.node_message(this, new Dictionary<object, object> {
                        {
                            "txt",
                            "RECEIVE PEERNODE LIST"},
                        {
                            "peernodes",
                            this.latestBlockHeight}});
                }
            }
            
            // OPTIONAL
            // If you need to override the NodeConection as well, you need to
            // override this method! In this method, you can initiate
            // you own NodeConnection class.
            public virtual object create_new_connection(object connection, object id, object host, object port) {
                return MyOwnNodeConnection(this, connection, id, host, port);
            }
        }
        
        public class Poll
            : models.Model {
            
            public object owner = models.ForeignKey(User, on_delete: models.CASCADE);
            
            public object text = models.TextField();
            
            public object pub_date = models.DateTimeField(@default: timezone.now);
            
            public object active = models.BooleanField(@default: true);
            
            //  
            //         Return False if user already voted
            //         
            public virtual object user_can_vote(object user) {
                var user_votes = user.vote_set.all();
                var qs = user_votes.filter(poll: this);
                if (qs.exists()) {
                    return false;
                }
                return true;
            }
            
            public object get_vote_count {
                get {
                    return this.vote_set.count();
                }
            }
            
            public virtual object get_result_dict() {
                var res = new List<object>();
                foreach (var choice in this.choice_set.all()) {
                    var d = new Dictionary<object, object> {
                    };
                    var alert_class = new List<object> {
                        "primary",
                        "secondary",
                        "success",
                        "danger",
                        "dark",
                        "warning",
                        "info"
                    };
                    d["alert_class"] = secrets.choice(alert_class);
                    d["text"] = choice.choice_text;
                    d["num_votes"] = choice.get_vote_count;
                    if (!this.get_vote_count) {
                        d["percentage"] = 0;
                    } else {
                        d["percentage"] = choice.get_vote_count / this.get_vote_count * 100;
                    }
                    res.append(d);
                }
                return res;
            }
            
            public override object ToString() {
                return this.text;
            }
        }
        
        public class Choice
            : models.Model {
            
            public object poll = models.ForeignKey(Poll, on_delete: models.CASCADE);
            
            public object choice_text = models.CharField(max_length: 255);
            
            public object get_vote_count {
                get {
                    return this.vote_set.count();
                }
            }
            
            public override object ToString() {
                return "{self.poll.text[:25]} - {self.choice_text[:25]}";
            }
        }
        
        public class Vote
            : models.Model {
            
            public object user = models.ForeignKey(User, on_delete: models.CASCADE);
            
            public object poll = models.ForeignKey(Poll, on_delete: models.CASCADE);
            
            public object choice = models.ForeignKey(Choice, on_delete: models.CASCADE);
            
            public override object ToString() {
                return "{self.poll.text[:15]} - {self.choice.choice_text[:15]} - {self.user.username}";
            }
        }
        
        public class MiningNode {
            
            public MiningNode() {
                //miningNode = MyOwnPeer2PeerNode("127.0.0.1", OUTBOUND_PORT)
                var miningNode = MyOwnPeer2PeerNode("127.0.0.1", INBOUND_PORT, node_callback);
                this.mining_node_instance = miningNode;
                miningNode.debug = true;
                // time.sleep(1)
                // # Do not forget to start your node!
                miningNode.start();
                this.previousBlock = new Dictionary<object, object> {
                };
                this.miningnodeversion = 1;
                this.chain = new List<object>();
                this.latestBlockHeight = 0;
                this.mining_node_instance.latestBlockHeight = this.latestBlockHeight;
                this.memPool = new Dictionary<object, object> {
                };
                this.candidateBlock = new Dictionary<object, object> {
                };
                this.tempUser = "";
                this.legalDictionary = new Dictionary<object, object> {
                };
            }
            
            public virtual object connect_to_node() {
                this.mining_node_instance.connect_with_node("127.0.0.1", OUTBOUND_PORT);
            }
            
            //if there are no other nodes to download blockdata from, generate the genesis block
            public virtual object createGenesisBlock() {
                var genesis_hash = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f";
                var genesis_proof = 1;
                //automatically create first entity (users), then create citizen so there is at least 1 transaction, genesis block hash same as vouching user id
                this.createNewEntity(genesis_hash, new Dictionary<object, object> {
                    {
                        "name",
                        "USER"},
                    {
                        "type",
                        "noun"},
                    {
                        "desc",
                        "a human who is using this software as intended"}});
                this.createNewCitizen(genesis_hash, new Dictionary<object, object> {
                    {
                        "name",
                        "admin"},
                    {
                        "age",
                        33}});
                //then create the other initial entities using newly generated USERID
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "LAW"},
                    {
                        "type",
                        "noun"},
                    {
                        "desc",
                        "a law created using this software"}});
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "DISPUTE"},
                    {
                        "type",
                        "noun"},
                    {
                        "desc",
                        "a dispute between two users created using this software"}});
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "POINTS"},
                    {
                        "type",
                        "noun"},
                    {
                        "desc",
                        "the default currency"}});
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "INITIATE"},
                    {
                        "type",
                        "verb"},
                    {
                        "desc",
                        "initiating a transaction with this software"}});
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "STEAL"},
                    {
                        "type",
                        "verb"},
                    {
                        "desc",
                        "take something you dont own without consent"}});
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "VOTE"},
                    {
                        "type",
                        "verb"},
                    {
                        "desc",
                        "impose your will on society"}});
                this.createNewEntity(this.tempUser, new Dictionary<object, object> {
                    {
                        "name",
                        "OWN"},
                    {
                        "type",
                        "verb"},
                    {
                        "desc",
                        "possess full rights over an asset"}});
                this.createBasicIncome(this.tempUser, new Dictionary<object, object> {
                    {
                        "POINTS",
                        100.0}});
                //automatically create candidate block so there is something there 
                Console.WriteLine("CREATED GENESIS BLOCK");
                this.createCandidateBlock(0, genesis_proof, genesis_hash);
            }
            
            public virtual object requestBlockData(object blockheight) {
                this.mining_node_instance.node_message(this.mining_node_instance, new Dictionary<object, object> {
                    {
                        "txt",
                        "GET BLOCKDATA FILE"},
                    {
                        "blockheight",
                        blockheight}});
            }
            
            public virtual object requestLatestBlockHeight() {
                this.mining_node_instance.node_message(this.mining_node_instance, new Dictionary<object, object> {
                    {
                        "txt",
                        "GET LATEST BLOCKHEIGHT"}});
            }
            
            //create binary data from memPool JSON
            public virtual object createCandidateBlock(object blockheight, object proof, object prev_hash) {
                //header = {version, prev_block_hash/prev_block_merkleroot, thisblocks_merkleroot, time, difficulty, nonce}
                if (blockheight == 0) {
                    blockheight = 0;
                } else {
                    blockheight = Convert.ToInt32(blockheight) - 1;
                }
                var blockheader = new Dictionary<object, object> {
                    {
                        "version",
                        this.miningnodeversion},
                    {
                        "proof",
                        proof},
                    {
                        "prev_block_height",
                        blockheight},
                    {
                        "prev_block_hash",
                        prev_hash},
                    {
                        "this_block_hash",
                        this.get_merkle_root(this.memPool)},
                    {
                        "time",
                        datetime.datetime.timestamp(datetime.datetime.now())}};
                //print("BLOCK HEADER")
                var block = new Dictionary<object, object> {
                    {
                        "header",
                        blockheader},
                    {
                        "tx_count",
                        this.memPool.Count},
                    {
                        "transactions",
                        this.memPool}};
                if (blockheight == 0) {
                    this.chain.append(block);
                    Console.WriteLine(this.chain);
                }
                this.candidateBlock = block;
                Console.WriteLine("CANDIDATE BLOCK DATA STORED IN PREV BLOCK SLOT, AND ADDED TO CHAIN");
                Console.WriteLine("WRITE BLOCK TO FILE");
                var bytesfile = base64.b64encode(block.ToString().encode("utf-8"));
                using (var binary_file = open("ledgerdata\\block" + blockheight.ToString() + ".dat", "wb")) {
                    binary_file.write(bytesfile);
                }
                this.memPool = new Dictionary<object, object> {
                };
                Console.WriteLine("MEMPOOL EMPTIED");
            }
            
            public virtual object createTestBlock() {
                Console.WriteLine("self.latestBlockHeight");
                Console.WriteLine(this.latestBlockHeight);
                var testBlockPrevHash = this.chain[this.latestBlockHeight]["header"]["this_block_hash"];
                var testnlockLatestBlockHeight = this.chain[this.latestBlockHeight]["header"]["prev_block_height"] + 1;
                var testBlockNonce = 1;
                var testInitatorAddress = "12345";
                //automatically create first entity (users), then create citizen so there is at least 1 transaction, genesis block hash same as vouching user id
                var testCitizen1Id = this.createNewCitizen(testInitatorAddress, new Dictionary<object, object> {
                    {
                        "name",
                        "guy1"},
                    {
                        "age",
                        33}});
                var testCitizen2Id = this.createNewCitizen(testInitatorAddress, new Dictionary<object, object> {
                    {
                        "name",
                        "guy2"},
                    {
                        "age",
                        33}});
                //then propose some bills
                var testBill1Id = this.proposeNewBill(testInitatorAddress, new HashSet({
                    "data"}));
                var testBill2Id = this.proposeNewBill(testInitatorAddress, new HashSet({
                    "data"}));
                //then have the 3 citizens vote
                this.voteOnBill(testInitatorAddress, testBill2Id);
                this.voteOnBill(testCitizen1Id, testBill2Id);
                this.voteOnBill(testCitizen2Id, testBill2Id);
                //resolve Bill vote simulating when turn
                this.resolveBillVote(testBill2Id);
                Console.WriteLine("CREATED TEST BLOCK");
                this.createCandidateBlock(testnlockLatestBlockHeight, testBlockNonce, testBlockPrevHash);
            }
            
            public virtual object proposeNewBill(object initiatorAddress, object data) {
                var proposedBillAddress = hashlib.sha256(uuid.uuid4().ToString().encode("utf-8")).hexdigest();
                this.makeTransaction(this, "CREATE", "LAW", "initiator_address", proposedBillAddress, data);
                return proposedBillAddress;
            }
            
            public virtual object voteOnBill(object voterCitizenId, object proposedBillId) {
                this.makeTransaction(this, "VOTE", "LAW", voterCitizenId, proposedBillId, new Dictionary<object, object> {
                    {
                        "data",
                        0}});
            }
            
            public virtual object get_merkle_root(object transactionsInMemPool) {
                var branches = new List<object>();
                foreach (var _tup_1 in transactionsInMemPool.items()) {
                    var timestamp = _tup_1.Item1;
                    var tx = _tup_1.Item2;
                    //print("TX.txid")
                    //print(tx["txid"])
                    branches.append(tx["txid"]);
                    //print("txid")
                    //print(txid)
                    //branches = [t.hash for t in transactions]
                }
                while (branches.Count > 1) {
                    //print("branches")
                    //print(branches)
                    //print("length of branches")
                    //print(len(branches))
                    if (branches.Count % 2 == 1) {
                        branches.append(branches[-1]);
                        //print(branches)
                    }
                    foreach (var _tup_2 in zip(branches[0:2:], branches[1:2:])) {
                        var a = _tup_2.Item1;
                        var b = _tup_2.Item2;
                        branches = new List<object> {
                            hashlib.sha256((a + b).ToString().encode("utf-8")).hexdigest()
                        };
                        //print("branches")
                        //print(branches)
                        //branches = [hashlib.sha256(a + b).hexdigest() for (a, b) in zip(branches[0::2], branches[1::2])]
                    }
                }
                Console.WriteLine("in GET MERKLE ROOT");
                Console.WriteLine(branches[0]);
                if (branches.Count < 1) {
                    return "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f";
                }
                return branches[0];
            }
            
            public virtual object makeSureInitiatorIsValidUser(object initiator_address) {
                if (true) {
                    return true;
                } else {
                    return false;
                }
            }
            
            public virtual object resolveBillVote(object billId) {
                return;
            }
            
            //type can be CREATE, EDIT, REMOVE, VOTE
            //recipient_address can be lawID, citizenID/ORGNAIZATIONID, COURTCASEID, PRIVELEGEID
            public virtual object makeTransaction(
                object type,
                object subtype,
                object initiator_address,
                object recipient_address,
                object data) {
                object transaction;
                //TRANSACTION LOOKS LIKE 
                //{ 122317812112.0121: {"v":1, "txid":"1212412451cab787fe" , "type":CREATE, "subtype":"USER", "initiator":"3243243abc9867876a8001234", "recipient":"21b421b123421b00031", "data":{data}}}
                //time = datetime.datetime.timestamp(datetime.datetime.now())
                var timestamp = time.time().ToString();
                //print(timestamp)
                //create signing object with current time as salt
                var txsignature = Signer();
                //UNIQUE IDS CREATE EVERY SINGLE TIME FOR EACH USER RECEIVING NEW PRIVILEGE OR ASSET
                //SINGLE LAW ID OR COURTCASE ID CREATED FOR ENTIRE COMMUNE
                //DATA CAN BE ANYTHING
                if (type == "CREATE") {
                    //ADD NEW CITIZEN OR ORGANIZATION TO COMMUNE
                    //USED TO CREATE CORPORATIONS
                    //INITIATOR_ADDRESS IS USER ID OF USER WHO VOUCHED FOR NEW USER, RECIPIENT ADDRESS IS LAW ID
                    if (subtype == "USER") {
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "CREATE"},
                            {
                                "subtype",
                                "USER"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "LAW") {
                        //ADD NEW LAW 
                        //INITIATOR_ADDRESS IS USER ID OF LAW PROPOSER, RECIPIENT ADDRESS IS LAW ID
                        //DATA IS EXPLANATION WITH RELATION TO AS MANY ENTITIES AS POSSIBLE
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "CREATE"},
                            {
                                "subtype",
                                "LAW"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "ASSET") {
                        //ADD NEW ASSET TO GROSS COMMUNE PRODUCT GDP
                        //INITIATOR_ADDRESS IS USERID WHO BECOMES OWNER OF ASSET, RECIPIENT ADDRESS IS WALLET ADDRESS WHERE ASSET LIVES
                        //THIS TYPE OF TRANSACTION IS USED WHEN A BLOCK IS MINED, UBI IS DISTRIBUTED, OR A NEW PRODUCT IS GENERATED OR FOUND
                        if (this.makeSureInitiatorIsValidUser(initiator_address)) {
                            transaction = new Dictionary<object, object> {
                                {
                                    "type",
                                    "CREATE"},
                                {
                                    "subtype",
                                    "ASSET"},
                                {
                                    "initiator",
                                    initiator_address},
                                {
                                    "recipient",
                                    recipient_address},
                                {
                                    "data",
                                    data}};
                        }
                    } else if (subtype == "COURTCASE") {
                        //CREATE NEW COURT CASE
                        //INITIATOR IS PERSON INITIATING DISPUTE, RECIPIENT IS ENTITY RECEIVING DISPUTE
                        //DATA CONTAINS ALL RELEVANT DETAILS
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "CREATE"},
                            {
                                "subtype",
                                "COURTCASE"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "PRIVILEGE") {
                        //ADD NEW PERMISSION FOR USER
                        //INITIATOR IS USER/ORGANIZATION APPROVING PERMIT, RECIPIENT IS USERID OF CITIZEN GAINING NEW PERMISSION
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "CREATE"},
                            {
                                "subtype",
                                "PRIVILEGE"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "ENTITY") {
                        //ADD NEW PERMISSION FOR USER
                        //INITIATOR IS USER/ORGANIZATION ID PROPOSING NEW ENTITY, RECIPIENT IS PERMANENT ADDRESS OF NEW ENTITY WHICH WILL BE REFERENCED
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "CREATE"},
                            {
                                "subtype",
                                "ENTITY"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else {
                        Console.WriteLine("no subtype, no tx");
                    }
                } else if (type == "EDIT") {
                    //CHANGE USER DATA
                    //INITIATOR_ADDRESS IS USER ID OF USER WHO EDITED USER, RECIPIENT ADDRESS IS TARGET USER ID
                    if (subtype == "USER") {
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "EDIT"},
                            {
                                "subtype",
                                "USER"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "LAW") {
                        //CHANGE EXISTING LAW
                        //INITIATOR_ADDRESS IS USER ID OF USER WHO TRIED TO EDIT LAW, RECIPIENT ADDRESS IS LAW ID TO BE EDITED
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "EDIT"},
                            {
                                "subtype",
                                "LAW"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "COURTCASE" || subtype == "ENTITY") {
                        //COURTCASE CANNOT BE EDITED
                        Console.WriteLine("courtcase cannot be edited");
                    } else if (subtype == "ASSET") {
                        //ASSET EDIT FUNCTIONS AS SENDING DATA AND TRANSFERRING OWNERSHIP!!!!!!!!!!!!!!!!!!!!!!!!
                        //INITIATOR IS USER LOSING ASSET OWNERSHIP, RECIPIENT IS USER GAINING ASSET OWNERSHIP
                        //DATA CONTAINS ASSET ID e.g. {"ASSETID":"32345r235325h", "ITEM":1}
                        //IF ITEM IS INT, PROECSS AS WHUFFIE, IF STRING PROCESS AS ITEM DESCRIPTION
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "EDIT"},
                            {
                                "subtype",
                                "ASSET"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "PRIVILEGE") {
                        //EDIT USER PRIVILEGE
                        //INITIATOR IS USERID MAKING CHANGE, RECIPIENT IS TRANSACTION ID OF ORIGINAL PRIVELGE
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "EDIT"},
                            {
                                "subtype",
                                "PRIVILEGE"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else {
                        Console.WriteLine("bad transaction");
                    }
                } else if (type == "VOTE") {
                    //DELEGATE VOTING POWER TO OTHER CITIZEN
                    //INITIATOR IS USERID OF WHO IS GIVING VOTING POWER, RECIPIENT IS WHO IS RECEIVING VOTING POWER
                    if (subtype == "USER") {
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "VOTE"},
                            {
                                "subtype",
                                "USER"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "LAW") {
                        //VOTE ON LAWS VALIDITY
                        //INITIATOR_ADDRESS IS USER ID OF VOTER, RECIPIENT ADDRESS IS LAW ID TO BE VOTED ON
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "VOTE"},
                            {
                                "subtype",
                                "LAW"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "ENTITY") {
                        //VOTE ON ENTITY VALIDITY
                        //INITIATOR_ADDRESS IS USER ID OF VOTER, RECIPIENT ADDRESS IS ENTITY ID TO BE VOTED ON
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "VOTE"},
                            {
                                "subtype",
                                "ENTITY"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "ASSET") {
                        //CANT VOTE ON ASSETS
                        Console.WriteLine("cant vote on assets");
                    } else if (subtype == "PRIVILEGE") {
                        //ENDORSE PRIVILEGES
                        //INITIATOR_ADDRESS IS USER ID OF VOTER, RECIPIENT ADDRESS IS RIGHT TO BE VOTED ON
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "VOTE"},
                            {
                                "subtype",
                                "PRIVILEGE"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "COURTCASE") {
                        //ANONYMOUS VOTE ON RESULT OF DISPUTE
                        //INITIATOR IS COURTCASEID, RECIPIENT IS USER ID OF EITHER PLANTIFF OR DEFENDANT
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "VOTE"},
                            {
                                "subtype",
                                "COURTCASE"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else {
                        Console.WriteLine("rejected");
                    }
                } else if (type == "REMOVE") {
                    //REMOVE EXISTING USER FROM COMMUNE
                    //INITIATOR IS USER WHO DELETES, RECIPIENT IS USER WHO GETS DELETED
                    if (subtype == "USER") {
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "REMOVE"},
                            {
                                "subtype",
                                "USER"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "LAW") {
                        //REPEAL EXISTING LAW
                        //INITIATOR_ADDRESS IS USER ID OF USER WHO TRIED TO REPEAL LAW, RECIPIENT ADDRESS IS LAW ID TO BE REPEALED
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "REMOVE"},
                            {
                                "subtype",
                                "LAW"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "ASSET") {
                        //CONSUME EXISTING ASSET
                        //INITIATOR_ADDRESS IS USER ID OF USER WHO CONSUMED ASSET, RECIPIENT IS ASSET ID
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "REMOVE"},
                            {
                                "subtype",
                                "ASSET"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "PRIVILEGE") {
                        //RESCIND EXISTING PERMISSION
                        //INITIATOR_ADDRESS IS USER ID OF USER LOSING PRIVILEGE, RECIPIENT IS PRIVILEGE ID
                        //DATA IS DESCRIPTION E.G. {"desc":"remove voting privilege"}
                        transaction = new Dictionary<object, object> {
                            {
                                "type",
                                "REMOVE"},
                            {
                                "subtype",
                                "PRIVILEGE"},
                            {
                                "initiator",
                                initiator_address},
                            {
                                "recipient",
                                recipient_address},
                            {
                                "data",
                                data}};
                    } else if (subtype == "COURTCASE" || subtype == "ENTITY") {
                        //COURTCASE AND ENTITIES CANT BE REMOVED
                        Console.WriteLine("courtcases and entities cannot be removed");
                    } else {
                        Console.WriteLine("rejected");
                    }
                } else {
                    Console.WriteLine("BAD TRANSACTION");
                }
                Console.WriteLine("transaction id");
                var txid = hashlib.sha256(transaction.ToString().encode("utf-8")).hexdigest();
                //print(txid)
                transaction["v"] = this.miningnodeversion;
                transaction["txid"] = txid;
                //transaction["signature"] = 
                //add transaction to memPool with time as key
                this.memPool[timestamp] = transaction;
                Console.WriteLine("tx added to mempool");
                return transaction;
                // print("binary data")
                // print(data)
                // print("decoded data")
                // print(base64.b64decode(data))
                // print("transaction id")
                // print(hashlib.sha256(str(transaction).encode('utf-8')).hexdigest())
                // #add transaction to memPool
                // self.memPool[hashlib.sha256(str(transaction).encode('utf-8')).hexdigest()] = transaction
                // #print(self.memPool)
                //self.makeTransaction("CREATE", "USER", vouchingUserId, hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest(), base64.b64encode(json.dumps(citizenData).encode("utf-8")))
            }
            
            public virtual object createNewCitizen(object vouchingUserId, object citizenData) {
                var newCitizenId = hashlib.sha256(uuid.uuid4().ToString().encode("utf-8")).hexdigest();
                this.tempUser = newCitizenId;
                this.makeTransaction("CREATE", "USER", vouchingUserId, newCitizenId, citizenData);
                return newCitizenId;
            }
            
            public virtual object createBasicIncome(object firstAssetOwner, object assetData) {
                this.makeTransaction("CREATE", "ASSET", firstAssetOwner, hashlib.sha256(uuid.uuid4().ToString().encode("utf-8")).hexdigest(), assetData);
            }
            
            //ENTITIES ARE LEGAL DEFINITIONS THAT MUST BE REFERENCED IN LAWS/DISPUTES/ETC
            public virtual object createNewEntity(object lawOrUserCreatingEntity, object entityData) {
                this.makeTransaction("CREATE", "ENTITY", lawOrUserCreatingEntity, hashlib.sha256(uuid.uuid4().ToString().encode("utf-8")).hexdigest(), entityData);
            }
            
            public virtual object editCitizenData(object userIDMakingChange, object userIDToChange, object changeToMake) {
                this.makeTransaction("EDIT", "USER", userIDMakingChange, userIDToChange, changeToMake);
            }
            
            public virtual object proof_of_work(object previous_proof) {
                var new_proof = 1;
                var check_proof = false;
                while (object.ReferenceEquals(check_proof, false)) {
                    var hash_operation = hashlib.sha256((Math.Pow(new_proof, 2) - Math.Pow(previous_proof, 2)).ToString().encode("utf-8")).hexdigest();
                    if (hash_operation[::5] == "00000") {
                        check_proof = true;
                    } else {
                        new_proof += 1;
                    }
                }
                return new_proof;
            }
            
            // def hash(self, block):
            //     encoded_block = json.dumps(block, sort_keys=True).encode("utf-8")
            //     return hashlib.sha256(encoded_block).hexdigest()
            // def chain_valid(self, chain):
            //     previous_block = chain[0]
            //     block_index = 1
            //     while block_index < len(chain):
            //         block = chain[block_index]
            //         if block["prev_hash"] != self.hash(previous_block):
            //             return False
            //         previous_proof = previous_block['proof']
            //         proof = block['proof']
            //         hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode("utf-8")).hexdigest()
            //         if hash_operation[:5] != '00000':
            //             return False
            //         previous_block = block
            //         block_index += 1
            //     return True
            // def print_previous_block(self, node):
            //     return node.chain[-1]
            // This is the function for proof of work
            // and used to successfully mine the block
            public virtual object display_chain() {
                Console.WriteLine("displaychain");
                var response = new Dictionary<object, object> {
                    {
                        "chain",
                        this.chain},
                    {
                        "length",
                        this.chain.Count}};
                return response;
            }
            
            public virtual object mine_block() {
                //get proof of previous block
                var previous_block = this.print_previous_block();
                var previous_proof = previous_block["proof"];
                var proof = this.proof_of_work(previous_proof);
                var previous_hash = this.hash(previous_block);
                var block = this.create_block(proof, previous_hash);
                var response = new Dictionary<object, object> {
                    {
                        "message",
                        "A block is MINED"},
                    {
                        "index",
                        block["index"]},
                    {
                        "timestamp",
                        block["timestamp"]},
                    {
                        "proof",
                        block["proof"]},
                    {
                        "previous_hash",
                        block["previous_hash"]}};
                return response;
            }
            
            public virtual object verifyBlock(object prev_blockdata, object currentblock_prev_hash) {
                if (this.get_merkle_root(prev_blockdata) == currentblock_prev_hash) {
                    return true;
                } else {
                    return false;
                    //blockhash = { 'hash': polls }
                    //return render(request, 'polls/polls_list.html', blockhash)
                    //     # print("decoded data")
                    //     # print(base64.b64decode(data))
                    // # # Mining a new block
                    // # #@app.route('/mine_block', methods=['GET'])
                    // def mine_block():
                    //     previous_block = blockchain.print_previous_block()
                    //     previous_proof = previous_block['proof']
                    //     proof = blockchain.proof_of_work(previous_proof)
                    //     previous_hash = blockchain.hash(previous_block)
                    //     block = blockchain.create_block(proof, previous_hash)
                    //     response = {'message': 'A block is MINED',
                    //                 'index': block['index'],
                    //                 'timestamp': block['timestamp'],
                    //                 'proof': block['proof'],
                    //                 'previous_hash': block['previous_hash']}
                    //     return JsonResponse(response)
                    // # # Display blockchain in json format
                    // # #@app.route('/get_chain', methods=['GET'])
                    // def display_chain():
                    //     print("displaychain")
                    //     response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
                    //     return response
                    // # # Check validity of blockchain
                    // # #@app.route('/valid', methods=['GET'])
                    // def valid():
                    //     valid = blockchain.chain_valid(blockchain.chain)
                    //     if valid:
                    //         response = {'message': 'The Blockchain is valid.'}
                    //     else:
                    //         response = {'message': 'The Blockchain is not valid.'}
                    //     print(response)
                    //     return JsonResponse(response)
                    // # Run the flask server locally
                    // #app.run(host='127.0.0.1', port=5000)
                }
            }
        }
    }
}

