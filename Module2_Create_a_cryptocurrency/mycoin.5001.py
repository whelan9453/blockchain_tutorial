# Module1 Create a cryptocurrency
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# part 1 - building a cryptocurrency based on the blockchain


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, prev_hash='0')
        self.nodes = set()

    def create_block(self, proof, prev_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prev_hash': prev_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = -1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(prev_proof**2 - new_proof**2).encode()).hexdigest()
            print('hash_operation', hash_operation)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_op = hashlib.sha256(
                str(prev_proof**2 - proof**2).encode()).hexdigest()
            if hash_op[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        prev_block = self.get_last_block()
        return prev_block['index']+1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


#  part 2- mining our blockchain to accept transactions
app = Flask(__name__)

# create an address for the node on port 5000
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

# mining a new block


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'len': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/validity', methods=['GET'])
def valid_chain():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        return jsonify({'message': 'chain is valid'}), 200
    else:
        return jsonify({'message': 'chain is invalid'}), 200


@app.route('/mine', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_last_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transaction(
        sender=node_address, receiver='james', amount=100)
    block = blockchain.create_block(proof, prev_hash)
    response = {'message': 'You mined a block!',
                'index': block['index'],
                'time': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Adding a transaction to the blockchain


@app.route('/transaction', methods=['POST'])
def broadcast_transaction():
    obj = request.get_json(force=True)
    transaction_keys = ['sender', 'receiver', 'amount']
    # if not all(for key in obj for key in transaction_keys):
    #     return 'missing keys', 400
    index = blockchain.add_transaction(
        obj['sender'], obj['receiver'], obj['amount'])
    response = {'message': 'this transaction will be added to  block {index}'}
    return jsonify(response, 201)

# part 3 decentralizing our blockchain

# connect to a new node


@app.route('/node', methods=['POST'])
def connect_node():
    obj = request.get_json(force=True)
    nodes = obj['nodes']
    if nodes is None:
        return "no nodes", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes are connected.',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replace the chain by the longest chain


@app.route('/chain', methods=['PUT'])
def use_longest_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        return jsonify({'message': 'chain is replaced',
                        'new_chain': blockchain.chain}), 200
    else:
        return jsonify({'message': 'chain is intact',
                        'current_chain': blockchain.chain}), 200


app.run(port=5001)
