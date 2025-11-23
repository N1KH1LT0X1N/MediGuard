"""
Blockchain configuration for committing hash chain to Ethereum/Polygon.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Blockchain configuration
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
BLOCKCHAIN_NETWORK = os.getenv("BLOCKCHAIN_NETWORK", "sepolia")  # sepolia, mumbai, mainnet, polygon
BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS")  # Optional: if using smart contract
BLOCKCHAIN_SIMULATED = os.getenv("BLOCKCHAIN_SIMULATED", "true")  # Use simulated mode by default (no ETH required)
BLOCKCHAIN_MODE = "simulated" if BLOCKCHAIN_SIMULATED.lower() == "true" else "real"

# Network chain IDs
CHAIN_IDS = {
    "sepolia": 11155111,
    "mumbai": 80001,
    "mainnet": 1,
    "polygon": 137
}

# Get chain ID for current network
CHAIN_ID = CHAIN_IDS.get(BLOCKCHAIN_NETWORK.lower(), 11155111)  # Default to Sepolia

# Gas settings
GAS_LIMIT = int(os.getenv("BLOCKCHAIN_GAS_LIMIT", "100000"))
GAS_PRICE_MULTIPLIER = float(os.getenv("BLOCKCHAIN_GAS_PRICE_MULTIPLIER", "1.2"))  # 20% buffer

