# backend/blockchain.py
"""
Real Blockchain Implementation for MediTrace
Cryptographically linked blocks with integrity verification
"""

import hashlib
import json
from datetime import datetime
import sqlite3

class Block:
    """Individual block in the blockchain"""
    
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Generate SHA-256 hash of block contents"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self):
        """Convert block to dictionary for storage"""
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:
    """Blockchain ledger for supply chain events"""
    
    def __init__(self, db_path='meditrace.db'):
        self.db_path = db_path
        self.chain = []
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Load existing chain or create genesis block"""
        genesis = self._create_genesis_block()
        self.chain.append(genesis)
        print("✅ Blockchain initialized with genesis block")
    
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        return Block(
            index=0,
            timestamp=datetime.now(),
            data={"event": "Genesis Block", "note": "MediTrace Blockchain Initialized"},
            previous_hash="0x000000"
        )
    
    def get_latest_block(self):
        """Get the most recent block"""
        return self.chain[-1] if self.chain else None
    
    def add_block(self, drug_id, event_type, location):
        """Add new supply chain event as a block"""
        previous_block = self.get_latest_block()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(),
            data={
                'drug_id': drug_id,
                'event_type': event_type,
                'location': location
            },
            previous_hash=previous_block.hash if previous_block else "0x000000"
        )
        
        self.chain.append(new_block)
        print(f"✅ Block #{new_block.index} added to blockchain | Hash: {new_block.hash[:16]}...")
        return new_block
    
    def verify_chain(self):
        """Verify integrity of entire blockchain"""
        if len(self.chain) < 2:
            print("✅ Blockchain has only genesis block - Valid by default")
            return True
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if current hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Block #{i} has been tampered with!")
                print(f"   Expected: {current_block.calculate_hash()[:16]}...")
                print(f"   Got: {current_block.hash[:16]}...")
                return False
            
            # Check if previous hash link is valid
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block #{i} chain is broken!")
                print(f"   Expected previous: {previous_block.hash[:16]}...")
                print(f"   Got: {current_block.previous_hash[:16]}...")
                return False
        
        print("✅ Blockchain integrity verified - No tampering detected")
        return True
    
    def get_chain_as_json(self):
        """Export entire chain as JSON"""
        return [block.to_dict() for block in self.chain]
    
    def display_chain(self):
        """Pretty print the blockchain"""
        print("\n" + "="*70)
        print("MEDITRACE BLOCKCHAIN")
        print("="*70)
        
        for block in self.chain:
            print(f"\nBlock #{block.index}")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Data: {block.data}")
            print(f"  Previous Hash: {block.previous_hash[:16]}...")
            print(f"  Current Hash: {block.hash[:16]}...")
        
        print("\n" + "="*70)


# ═══════════════════════════════════════════════════════
# DEMO FUNCTIONS FOR VIVA
# ═══════════════════════════════════════════════════════

def demo_blockchain():
    """Demonstrate blockchain functionality"""
    print("🔗 MediTrace Blockchain Demo\n")
    
    blockchain = Blockchain()
    
    # Add test blocks
    print("\n📦 Adding blocks to chain...")
    blockchain.add_block(1, "Production Complete", "Bangalore Factory")
    blockchain.add_block(1, "Quality Check", "Chennai Warehouse")
    blockchain.add_block(2, "Dispatch", "Mumbai Warehouse")
    blockchain.add_block(3, "Retail Scan", "Delhi Pharmacy")
    
    # Display chain
    blockchain.display_chain()
    
    # Verify integrity
    print("\n🔍 Verifying blockchain integrity...")
    blockchain.verify_chain()
    
    # Demonstrate tampering detection
    print("\n⚠️  Simulating tampering attack...")
    print("   Modifying Block #2 data...")
    blockchain.chain[2].data['location'] = "FAKE LOCATION"
    
    print("\n🔍 Re-verifying blockchain integrity...")
    blockchain.verify_chain()
    
    print(f"\n📊 Final Stats:")
    print(f"   Total Blocks: {len(blockchain.chain)}")
    print(f"   Latest Hash: {blockchain.get_latest_block().hash[:32]}...")


if __name__ == '__main__':
    demo_blockchain()