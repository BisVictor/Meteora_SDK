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

class Reader:

    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def u8(self):
        #u8
        value = self.data[self.offset]
        self.offset += 1
        return value

    def u16(self):
        value = struct.unpack_from("<H", self.data, self.offset)[0]
        self.offset += 2
        return value

    def u32(self):
        #u32
        value = struct.unpack_from("<I", self.data, self.offset)[0]
        self.offset += 4
        return value

    def u64(self):
        value = struct.unpack_from("<Q", self.data, self.offset)[0]
        self.offset += 8
        return value

    def i32(self):
        value = struct.unpack_from("<i", self.data, self.offset)[0]
        self.offset += 4
        return value

    def i64(self):
        value = struct.unpack_from("<q", self.data, self.offset)[0]
        self.offset += 8
        return value
    
    def u128(self):
        value = int.from_bytes(
            self.data[self.offset:self.offset+16],
            byteorder="little",
            signed=False,
        )
        self.offset += 16
        return value

    def pubkey(self):
        value = self.data[self.offset:self.offset + 32]
        self.offset += 32
        return value
    
    def pubkey(self):
        value = Pubkey.from_bytes(
            self.data[self.offset:self.offset + 32]
        )
        self.offset += 32
        return value
    
    def skip(self, n):
        self.offset += n

    def tell(self):
        return self.offset
    
    def boolean(self):
        return bool(self.u8())
    
rpc = MeteoraRPC(URL)
#account = rpc.get_account("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd") #meteora USDC-SOL my
account = rpc.get_account("HPQxZ91SJ62AJ7WBSqop2Ttkz1j6cwGNFtxvFdysyjb7") #meteora 
#account = rpc.get_account("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo")
#print(account)

data = bytes(account.value.data)

r = Reader(data)
r.offset = 8
base_factor = r.u16()
filter_period = r.u16()



