
import anchorpy
from anchorpy import Idl, Provider, Wallet
import solders
from shadowPaySDK.interface.sol import SOL
import solders  
import spl.token.constants as spl_constants



class SOLCheque:
        def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com", keystore: Wallet = None):
            self.rpc_url = rpc_url
            self.keystore = keystore
            self.provider = Provider(self.rpc_url, self.keystore)
            self.WRAPED_SOL = spl_constants.WRAPPED_SOL_MINT    # wrapped SOL token mint address
            # self.idl = Idl.from_json(sol_interface.Idl)  # Load the IDL for the program
        def get(self, keypair = None):
              pubkey = SOL.get_pubkey(KEYPAIR=solders.keypair.Keypair.from_base58_string(self.keystore))

              return pubkey
        



  