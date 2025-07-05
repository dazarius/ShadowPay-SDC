import json
from typing import Optional, Union
from web3 import Web3




def parse_tx(tx):
    """
    Parses a transaction dictionary to extract relevant information.
    
    Args:
        tx (dict): The transaction dictionary.
        
    Returns:
        dict: A dictionary containing the parsed transaction details.
    """
    return {
        "hash": tx.get("hash"),
        "from": tx.get("from"),
        "to": tx.get("to"),
        "value": Web3.from_wei(tx.get("value", 0), 'ether'),
        "gas": tx.get("gas"),
        "gas_price": Web3.from_wei(tx.get("gasPrice", 0), 'gwei'),
        "nonce": tx.get("nonce"),
        "block_number": tx.get("blockNumber"),
        "timestamp": tx.get("timestamp")
    }