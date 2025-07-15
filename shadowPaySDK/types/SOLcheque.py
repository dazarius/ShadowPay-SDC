
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
from spl.token.instructions import get_associated_token_address, create_associated_token_account,TransferCheckedParams, transfer_checked, transfer, close_account, TransferParams
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

PROGRAM_ID = Pubkey.from_string("CrfYLvU4FdVjkBno2rRi6u5U6nGCykpQnQKSBg3uVXTw")

CONFIG_PDA=Pubkey.find_program_address([b"config"], PROGRAM_ID)
TRESSARY = Pubkey.from_string("FRCYiNg7BV73bHRrQKAPgFKhafqiQD7aCFn2YZ6LE5oE") 
PROGRAM_ID_STR = "5nfYDCgBgm72XdpYFEtWX2X1JQSyZdeBH2uuBZ6ZvQfi"

class SOLCheque:
        def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com", key: Wallet = None):
            self.rpc_url = rpc_url
            if key:
                self.key = solders.keypair.Keypair.from_base58_string(key)
            self.provider = Client(rpc_url)
            self.WRAPED_SOL = spl_constants.WRAPPED_SOL_MINT    # wrapped SOL token mint address
            # self.idl = Idl.from_json(sol_interface.Idl)  # Load the IDL for the program
        def get(self, keypair = None):
              pubkey = SOL.get_pubkey(KEYPAIR=solders.keypair.Keypair.from_base58_string(self.key))

              return pubkey
        def get_config(self):
            config_pda, _ = Pubkey.find_program_address([b"config"], PROGRAM_ID)

            response = self.provider.get_account_info(config_pda)
            if response.value is None:
                print("❌ Config PDA not found.")
                return None

            # 🧠 У тебя data — это list[int], его нужно превратить в bytes
            raw = bytes(response.value.data)

            if len(raw) < 89:
                print("❌ Invalid config data length.")
                return None

            admin = Pubkey.from_bytes(raw[0:32])
            treasury = Pubkey.from_bytes(raw[32:64])
            fee_bps = struct.unpack("<Q", raw[64:72])[0]
            token_in_bps = struct.unpack("<Q", raw[72:80])[0]
            token_out_bps = struct.unpack("<Q", raw[80:88])[0]
            initialized = bool(raw[88])

            print(f"📘 Config PDA: {config_pda}")
            print(f"Admin: {admin}")
            print(f"Treasury: {treasury}")
            print(f"Fee BPS: {fee_bps}")
            print(f"Token In BPS: {token_in_bps}")
            print(f"Token Out BPS: {token_out_bps}")
            print(f"Initialized: {initialized}")

            return {
                "pda": str(config_pda),
                "admin": str(admin),
                "treasury": str(treasury),
                "fee_bps": fee_bps,
                "token_in_bps": token_in_bps,
                "token_out_bps": token_out_bps,
                "initialized": initialized,
            }
        def set_params(self, rpc_url = None, key = None):
            if rpc_url:
                self.rpc_url = rpc_url
                self.provider = Client(rpc_url)
            if key:
                self.key = solders.keypair.Keypair.from_base58_string(key)

        def init_cheque(self, cheque_amount, recipient: str, SPACE: int = 100):
            """
            Initialize a cheque withc the specified amount and recipient.
            """
            if not self.key:
                raise ValueError("Keypair is not set. Please set the keypair before initializing a cheque.")
            CHEQUE_PDA_SIGNATURE = None
            CHEQUE_SPACE = SPACE  
            CHEQUE_RENT = self.provider.get_minimum_balance_for_rent_exemption(CHEQUE_SPACE)
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

            data = bytes([0]) + bytes(r) + struct.pack("<Q", total_lamports)

            

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
            confirm = self.provider.confirm_transaction(response.value)
            
            data = {
                "cheque_pda": str(CHEQUE_PDA),
                "signature": str(response.value),
                "create_signature": str(CHEQUE_PDA_SIGNATURE),
                "cheque_amount": cheque_amount,
                "pda_rent_sol": CHEQUE_RENT.value / LAMPORTS_PER_SOL,
            }
            return data

        def claim_cheque(self, pda_acc: str, rent_resiver:str = None ):
            instruction_data = bytes([1])
            payer = self.key
            payer_pubkey = payer.pubkey()
            if not rent_resiver:
                    rent_resiver = payer_pubkey
            rent_resiver = Pubkey.from_string(rent_resiver)
            cfg = self.get_config()
            treasury = Pubkey.from_string(cfg["treasury"])
            ix = Instruction(
                program_id=PROGRAM_ID,
                data=instruction_data,
                accounts = [
                    AccountMeta(pubkey=payer_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=Pubkey.from_string(pda_acc), is_signer=False, is_writable=True),
                    AccountMeta(pubkey=CONFIG_PDA[0], is_signer=False, is_writable=True),  # rent receiver
                    AccountMeta(pubkey=treasury, is_signer=False, is_writable=True)  # rent receiver 
                ]
            )

            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[ix], payer=payer_pubkey)
            tx = Transaction(message=message, from_keypairs=[payer], recent_blockhash=recent_blockhash)
            response = self.provider.send_transaction(tx,opts=TxOpts(skip_preflight=True))
            return {
                "signature": str(response.value),
                "pda_account": pda_acc,
            }


        def init_token_cheque(self, token_mint: str, token_amount,token_decimals, recipient: str, treasury: str, CHEQUE_SPACE: int = 105):
            if not self.key:
                raise ValueError("Keypair not set")

            payer = self.key
            payer_pubkey = payer.pubkey()
            token_mint_pubkey = Pubkey.from_string(token_mint)
            recipient_pubkey = Pubkey.from_string(recipient)
            treasury_pubkey = Pubkey.from_string(treasury)

            cheque_acc = solders.keypair.Keypair()
            cheque_pda = cheque_acc.pubkey()

            rent = self.provider.get_minimum_balance_for_rent_exemption(CHEQUE_SPACE).value

            create_cheque_acc = create_account(
                CreateAccountParams(
                    from_pubkey=payer_pubkey,
                    to_pubkey=cheque_pda,
                    lamports=rent,
                    space=CHEQUE_SPACE,
                    owner=PROGRAM_ID
                )
            )

            tx1 = Transaction(
                message=Message(instructions=[create_cheque_acc], payer=payer_pubkey),
                recent_blockhash=self.provider.get_latest_blockhash().value.blockhash,
                from_keypairs=[payer, cheque_acc]
            )
            self.provider.send_transaction(tx1, opts=TxOpts(skip_preflight=True))

            sender_ata = get_associated_token_address(payer_pubkey, token_mint_pubkey)
            cheque_ata = get_associated_token_address(cheque_pda, token_mint_pubkey)
            treasury_ata = get_associated_token_address(treasury_pubkey, token_mint_pubkey)

            ix_create_ata = create_associated_token_account(payer_pubkey, cheque_pda, token_mint_pubkey)

            amount = int(token_amount * (10 ** token_decimals))
            


            data = bytes([2]) + struct.pack("<Q", amount)

            ix_program = Instruction(
                program_id=PROGRAM_ID,
                data=data,
                accounts=[
                    AccountMeta(payer_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(cheque_pda, is_signer=True, is_writable=True),
                    AccountMeta(token_mint_pubkey, is_signer=False, is_writable=True),
                    AccountMeta(sender_ata, is_signer=False, is_writable=True),
                    AccountMeta(cheque_ata, is_signer=False, is_writable=True),
                    AccountMeta(treasury_ata, is_signer=False, is_writable=True),
                    AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),
                ]
            )

            # === 6. Собираем и отправляем всё в одном tx ===
            print("Accounts (ix_program):")
            for i, acc in enumerate(ix_program.accounts):
                print(f"[{i}] {acc.pubkey} | signer={acc.is_signer} | writable={acc.is_writable}")

            tx2 = Transaction(
                message=Message(instructions=[ix_create_ata,  ix_program], payer=payer_pubkey),
                recent_blockhash=self.provider.get_latest_blockhash().value.blockhash,
                from_keypairs=[payer, cheque_acc]
            )

            sig = self.provider.send_transaction(tx2, opts=TxOpts(skip_preflight=True)).value
            return {
                "cheque_pda": str(cheque_pda),
                "signature": str(sig),
                "amount": token_amount
            }