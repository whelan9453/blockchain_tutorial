# Module1 Create a blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify

# part 1 - building a blockchain


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, prev_hash='0')

    def create_block(self, proof, prev_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prev_hash': prev_hash}
        cur_hash = self.hash(block)
        block['hash'] = cur_hash
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


#  part 2- mining our blockchain
app = Flask(__name__)

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
        return jsonify({'message': 'chain is invalid'}), 400


@app.route('/mine', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_last_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash)
    response = {'message': 'You mined a block!',
                'index': block['index'],
                'time': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'hash': block['hash']}
    return jsonify(response), 200

app.run()