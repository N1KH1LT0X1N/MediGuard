"""
Blockchain Service for committing hash chain to Ethereum/Polygon blockchain.
Supports both real blockchain (requires ETH) and simulated mode (no ETH required).
"""

import os
import hashlib
from typing import Optional, Dict
from datetime import datetime
from backend.config.blockchain import (
    BLOCKCHAIN_RPC_URL,
    BLOCKCHAIN_PRIVATE_KEY,
    CHAIN_ID,
    GAS_LIMIT,
    GAS_PRICE_MULTIPLIER,
    BLOCKCHAIN_MODE
)

# Try to import web3, but make it optional
try:
    from web3 import Web3
    from eth_account import Account
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    Web3 = None
    Account = None


class BlockchainService:
    """Service for interacting with Ethereum/Polygon blockchain or simulated blockchain."""
    
    def __init__(self):
        """Initialize blockchain service."""
        # Check if we should use simulated mode
        use_simulated = os.getenv("BLOCKCHAIN_SIMULATED", "true").lower() == "true"
        
        if use_simulated or not BLOCKCHAIN_RPC_URL or not BLOCKCHAIN_PRIVATE_KEY:
            # Use simulated blockchain mode (no ETH required)
            self.mode = "simulated"
            self.w3 = None
            self.account = None
            self.address = "0x0000000000000000000000000000000000000000"  # Placeholder address
            self.simulated_block_number = 0
            print(f"✓ Blockchain service initialized (SIMULATED MODE - no ETH required)")
            print(f"  Mode: Simulated blockchain")
            print(f"  Note: Hash chain still provides immutability")
        else:
            # Use real blockchain (requires ETH)
            if not HAS_WEB3:
                raise ImportError("web3 library not installed. Install with: pip install web3 eth-account")
            
            self.mode = "real"
        self.w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain RPC endpoint")
        
        # Load account from private key
        self.account = Account.from_key(BLOCKCHAIN_PRIVATE_KEY)
        self.address = self.account.address
        
        print(f"✓ Blockchain service initialized (REAL MODE)")
        print(f"  Network: {BLOCKCHAIN_RPC_URL}")
        print(f"  Address: {self.address}")
        print(f"  Chain ID: {CHAIN_ID}")
    
    def commit_hash_to_blockchain(self, root_hash: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Commit a hash to the blockchain (real or simulated).
        
        Args:
            root_hash: The hash to commit (from hash chain)
            metadata: Optional metadata to include (will be hashed together)
            
        Returns:
            Dictionary with transaction hash and block number
        """
        if self.mode == "simulated":
            # Simulated blockchain mode - generate fake tx hash and block number
            # This provides blockchain-like metadata without requiring ETH
            timestamp = datetime.utcnow().isoformat()
            data_string = f"MediGuardAI:{root_hash}:{timestamp}"
            if metadata:
                import json
                metadata_str = json.dumps(metadata, sort_keys=True)
                data_string += f":{metadata_str}"
            
            # Generate deterministic "transaction hash" from the data
            tx_hash = hashlib.sha256(data_string.encode()).hexdigest()
            # Use first 16 chars as "transaction hash" (like 0x...)
            tx_hash = f"0x{tx_hash[:16]}"
            
            # Increment simulated block number
            self.simulated_block_number += 1
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "block_number": self.simulated_block_number,
                "gas_used": 0,
                "status": 1,
                "mode": "simulated",
                "note": "This is a simulated blockchain transaction. Hash chain provides immutability."
            }
        else:
            # Real blockchain mode
            try:
                # Prepare transaction data
                data_string = f"MediGuardAI:{root_hash}"
                if metadata:
                    import json
                    metadata_str = json.dumps(metadata, sort_keys=True)
                    data_string += f":{metadata_str}"
                
                # Get current gas price
                gas_price = self.w3.eth.gas_price
                adjusted_gas_price = int(gas_price * GAS_PRICE_MULTIPLIER)
                
                # Get nonce
                nonce = self.w3.eth.get_transaction_count(self.address)
                
                # Build transaction
                transaction = {
                    'to': self.address,
                    'value': 0,
                    'gas': GAS_LIMIT,
                    'gasPrice': adjusted_gas_price,
                    'nonce': nonce,
                    'data': self.w3.to_hex(text=data_string),
                    'chainId': CHAIN_ID
                }
                
                # Sign transaction
                signed_txn = self.account.sign_transaction(transaction)
                
                # Send transaction
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                # Wait for transaction receipt
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                return {
                    "success": True,
                    "tx_hash": receipt['transactionHash'].hex(),
                    "block_number": receipt['blockNumber'],
                    "gas_used": receipt['gasUsed'],
                    "status": receipt['status'],
                    "mode": "real"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "tx_hash": None,
                    "block_number": None,
                    "mode": "real"
                }
    
    def verify_on_blockchain(self, tx_hash: str) -> Dict:
        """
        Verify a transaction on the blockchain (real or simulated).
        
        Args:
            tx_hash: Transaction hash to verify
            
        Returns:
            Dictionary with verification results
        """
        if self.mode == "simulated":
            # For simulated mode, we can't actually verify on a real blockchain
            # But we can return that it's a simulated transaction
            return {
                "verified": True,
                "tx_hash": tx_hash,
                "mode": "simulated",
                "note": "This is a simulated blockchain transaction. Hash chain provides immutability.",
                "block_number": None,
                "status": 1
            }
        else:
            # Real blockchain verification
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                transaction = self.w3.eth.get_transaction(tx_hash)
                
                # Extract data from transaction
                data = transaction['input']
                
                return {
                    "verified": True,
                    "tx_hash": tx_hash,
                    "block_number": receipt['blockNumber'],
                    "status": receipt['status'],
                    "data": data,
                    "from": transaction['from'],
                    "to": transaction['to'],
                    "mode": "real"
                }
            except Exception as e:
                return {
                    "verified": False,
                    "error": str(e),
                    "tx_hash": tx_hash,
                    "mode": "real"
                }
    
    def get_balance(self) -> float:
        """
        Get account balance in ETH (real blockchain only).
        
        Returns:
            Balance in ETH (0.0 for simulated mode)
        """
        if self.mode == "simulated":
            return 0.0
        balance_wei = self.w3.eth.get_balance(self.address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain."""
        if self.mode == "simulated":
            return True  # Simulated mode is always "connected"
        return self.w3.is_connected()


# Global instance (will be initialized in main.py)
blockchain_service: Optional[BlockchainService] = None

