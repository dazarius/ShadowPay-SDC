
import anchorpy
from anchorpy import Idl, Provider, Wallet
import solders
from shadowPaySDK.interface.sol import SOL
import solders  
import spl.token.constants as spl_constants
from solana.rpc.api import Client

import asyncio
import solana
from solana.rpc.async_api import AsyncClient, GetTokenAccountsByOwnerResp
from solders.transaction import Transaction
from solders.system_program import TransferParams as p
from solders.instruction import Instruction, AccountMeta
from solders.rpc.config import RpcSendTransactionConfig
from solders.message import Message
import spl
import spl.token
import spl.token.constants
from spl.token.instructions import get_associated_token_address, create_associated_token_account, transfer, close_account, TransferParams
from solders.system_program import transfer as ts
from solders.system_program import TransferParams as tsf
from solders.pubkey import Pubkey
import os
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.rpc.types import TxOpts
import solders
from solders.message import Message
from solders.system_program import create_account,CreateAccountParams

# from solders.pubkey import Pubkey
# from solders.keypair import Keypair
# from solders.signature import Signature
# from solders.transaction import Transaction
from spl.token.async_client import AsyncToken


from solana.rpc.commitment import Confirmed
from solana.rpc.async_api import AsyncClient
import anchorpy
from anchorpy import Provider, Wallet, Idl
import pprint
import httpx
import base64
import re
import struct
from shadowPaySDK.const import LAMPORTS_PER_SOL

PROGRAM_ID = Pubkey.from_string("5nfYDCgBgm72XdpYFEtWX2X1JQSyZdeBH2uuBZ6ZvQfi")


# PROGRAM_ID = "5nfYDCgBgm72XdpYFEtWX2X1JQSyZdeBH2uuBZ6ZvQfi"

class SOLCheque:
        def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com", key: Wallet = None):
            self.rpc_url = rpc_url
            self.key = solders.keypair.Keypair.from_base58_string(key)
            self.provider = Client(rpc_url)
            self.WRAPED_SOL = spl_constants.WRAPPED_SOL_MINT    # wrapped SOL token mint address
            # self.idl = Idl.from_json(sol_interface.Idl)  # Load the IDL for the program
        def get(self, keypair = None):
              pubkey = SOL.get_pubkey(KEYPAIR=solders.keypair.Keypair.from_base58_string(self.keystore))

              return pubkey
        def set_params(self, rpc_url = None, key = None):
            if rpc_url:
                self.rpc_url = rpc_url
                self.provider = Client(rpc_url)
            if key:
                self.key = key

        def init_cheque(self, cheque_amount, recipient: str, SPACE: int = 100):
            """
            Initialize a cheque withc the specified amount and recipient.
            """
            if not self.key:
                raise ValueError("Keypair is not set. Please set the keypair before initializing a cheque.")
            CHEQUE_PDA_SIGNATURE = None
            CHEQUE_SPACE = SPACE  
            CHEQUE_RENT = self.provider.get_minimum_balance_for_rent_exemption(CHEQUE_SPACE)
            print("Minimum balance for rent exemption:", CHEQUE_RENT.value / LAMPORTS_PER_SOL, "SOL")
            sol = SOL(
                KEYPAIR=self.key  
            )
            payer = self.key
            pubkey = self.key.pubkey()
            newAcc = solders.keypair.Keypair()
            newAccPubkey = newAcc.pubkey()
            ix_create = create_account(
                params=CreateAccountParams(
                from_pubkey=pubkey,
                to_pubkey=newAccPubkey,
                lamports=CHEQUE_RENT.value,
                space=CHEQUE_SPACE,
                owner=PROGRAM_ID
                )
            )
            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[ix_create], payer=pubkey)

            t = Transaction(message=message, from_keypairs=[payer, newAcc], recent_blockhash=recent_blockhash)
            r = self.provider.send_transaction(t,opts=TxOpts())
            CHEQUE_PDA_SIGNATURE = r.value
            CHEQUE_PDA = newAccPubkey  



            total_lamports = int(cheque_amount * LAMPORTS_PER_SOL)


            r = Pubkey.from_string(recipient)  

            # 1 byte - tag
            # 32 bytes - recipient pubkey
            # 8 bytes - lamports (u64 LE)
            data = bytes([0]) + bytes(r) + struct.pack("<Q", total_lamports)

            # === Инструкция ===
            

            instruction = Instruction(
                program_id=PROGRAM_ID,
                data=data,  
                accounts=[
                    AccountMeta(pubkey=pubkey, is_signer=True, is_writable=True),     # payer
                    AccountMeta(pubkey=CHEQUE_PDA, is_signer=False, is_writable=True), # cheque PDA
                    AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False)

                ]
            )

            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[instruction], payer=pubkey)
            tx = Transaction(message=message, from_keypairs=[payer], recent_blockhash=recent_blockhash)
            response = self.provider.send_transaction(tx,opts=TxOpts(skip_preflight=True))
            data = {
                "signature": response.value,
                "amount": cheque_amount,
                "create_pda": CHEQUE_PDA_SIGNATURE,
                "cheque_pda": CHEQUE_PDA,
                "rent_pda": CHEQUE_RENT.value / LAMPORTS_PER_SOL,

            }
            return data

        def claim_cheque(self, pda_acc: str):
            instruction_data = bytes([1])
            payer = self.key
            payer_pubkey = payer.pubkey()
            

            ix = Instruction(
                program_id=PROGRAM_ID,
                data=instruction_data,
                accounts = [
                    AccountMeta(pubkey=payer_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=Pubkey.from_string(pda_acc), is_signer=False, is_writable=True),
                ]
            )

            # Создаём и отправляем транзакцию
            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[instruction_data], payer=payer_pubkey)
            tx = Transaction(message=message, from_keypairs=[payer], recent_blockhash=recent_blockhash)
            response = self.provider.send_transaction(tx,opts=TxOpts(skip_preflight=True))
            return response.value



  