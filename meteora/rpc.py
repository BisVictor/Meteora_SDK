from solana.rpc.api import Client
from solders.pubkey import Pubkey

import struct

URL = "https://api.mainnet-beta.solana.com"
#pubkey = "6NYPquPNfZALPDCVLTjADvzVsarRriGi1HS26ydo6s2C"

class  MeteoraRPC:

    def __init__(self, rpc_url: str):
        self.client = Client(rpc_url)

    def get_account(self, pubkey):
        pubkey = Pubkey.from_string(pubkey)
        return self.client.get_account_info(pubkey)
    
    def get_balance(self, pubkey):
        pubkey = Pubkey.from_string(pubkey)
        return self.client.get_balance(pubkey)

def u64(data, offset):
    return int.from_bytes(
        data[offset:offset+8],
        "little"
    )

def read_pubkey(data, offset):
    return str(
        Pubkey.from_bytes(
            data[offset:offset+32]
        )
    )

rpc = MeteoraRPC(URL)
#account = rpc.get_account("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd") #meteora USDC-SOL my
account = rpc.get_account("AUgbdzNob9S8MiVHm4Qruqz3VsZGoqtMZnSzv45juDbL") #meteora USDC-SOL 4-bin
#account = rpc.get_account("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo")
print(account)

data = bytes(account.value.data)

print("-"*50)
print("owner:", account.value.owner)
print("size :", len(data))
print("disc :", data[:8].hex())

for offset in range(8, 88, 8):
    print(offset, u64(data, offset))
    
print("-"*50)

for offset in range(88, 880, 32):
    print(offset, read_pubkey(data, offset))



#print(datetime.utcfromtimestamp(1782069297))


print("binStep     :", struct.unpack("<H", data[80:82])[0])
print("flags       :", struct.unpack("<H", data[82:84])[0])
print("fee_factor  :", struct.unpack("<I", data[84:88])[0])

print("active_id   :", struct.unpack("<i", data[48:52])[0])

print("state_a     :", struct.unpack("<I", data[72:76])[0])
print("state_b     :", struct.unpack("<i", data[76:80])[0])
