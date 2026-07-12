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
    
class StaticParameters():

    def __init__(self, r: Reader):
        self.base_factor = r.u16()
        self.filter_period = r.u16()
        self.decay_period = r.u16()
        self.reduction_factor = r.u16()
        self.variable_fee_control = r.u32()
        self.max_volatility_accumulator = r.u32()
        self.min_bin_id = r.i32()
        self.max_bin_id = r.i32()
        self.protocol_share = r.u16()
        self.base_fee_power_factor = r.u8()
        self.function_type = r.u8()
        self.collect_fee_mode = r.u8()
        self._padding = r.skip(3)

    def __repr__(self):
        return (
            "\n___ StaticParameters ___\n"
            f"base_factor: {self.base_factor}\n"
            f"filter_period: {self.filter_period}\n"
            f"decay_period: {self.decay_period}\n"
            f"reduction_factor: {self.reduction_factor}\n"
            f"variable_fee_control: {self.variable_fee_control}\n"
            f"max_volatility_accumulator: {self.max_volatility_accumulator}\n"
            f"min_bin_id: {self.min_bin_id}\n"
            f"max_bin_id: {self.max_bin_id}\n"
            f"protocol_share: {self.protocol_share}\n"
            f"base_fee_power_factor: {self.base_fee_power_factor}\n"
            f"function_type: {self.function_type}\n"
            f"collect_fee_mode: {self.collect_fee_mode}\n"
        )
    
class  VariableParameters:

    def __init__(self, r: Reader):
        self.volatility_accumulator = r.u32()
        self.volatility_reference = r.u32()
        self.index_reference = r.i32()
        self._padding = r.skip(4)
        self.last_update_timestamp = r.i64()
        self._padding1 = r.skip(8)

    def __repr__(self):
        return (
            "\n___ Variable Parameters ___\n"
            f"volatility_accumulator: {self.volatility_accumulator}\n"
            f"volatility_reference: {self.volatility_reference}\n"
            f"index_reference: {self.index_reference}\n"
            f"last_update_timestamp: {self.last_update_timestamp}\n"
        )

       
    
class LbPair:

    def __init__(self, data):
        r = Reader(data)
        self.discriminator = r.i64()
        self.parameters = StaticParameters(r)
        self.v_parameters = VariableParameters(r)

    def __repr__(self):
        return(
            f"discriminator: {self.discriminator}"
            f"parameters: {self.parameters}"
            f"v_parameters: {self.v_parameters}"
        )



        
    
rpc = MeteoraRPC(URL)
#account = rpc.get_account("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd") #meteora USDC-SOL my
account = rpc.get_account("HPQxZ91SJ62AJ7WBSqop2Ttkz1j6cwGNFtxvFdysyjb7") #meteora 
#account = rpc.get_account("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo")
#print(account)

data = bytes(account.value.data)

lb = LbPair(data)
print(lb)



