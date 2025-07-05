import httpx
import json
from typing import Optional
from web3 import Web3

__MAIN__URL__= "http://0.0.0.0:8000"
__CREATE__CHEQUE__ = f"{__MAIN__URL__}/validate"
__MY__CHEQUES__ = f"{__MAIN__URL__}/mycheque"



async def __validate__cheque__(id, sender,action,  receiver:Optional[str] = None,  chain_id: Optional[int] = None, type:Optional[str] = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            __CREATE__CHEQUE__,
            json={
                "cheque_id": id,
                "chain_id":chain_id, 
                "receiver": receiver,
                "type": type,
                "sender":sender,
                "action": action
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to create cheque: {response.text}")
            return False


async def get_my_cheques(private_key):
    if not private_key:
        raise ValueError("Private key is required to fetch cheques.")
    sender = Web3.eth.account.from_key(private_key).address
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            __MY__CHEQUES__,
            params={
                "sender": sender
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch cheques: {response.text}")
            return False