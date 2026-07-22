from solana.rpc.api import Client
from solders.pubkey import Pubkey
from dotenv import load_dotenv
import os

from helpers import bin_id_to_bin_array_index
from pda import *

import struct

load_dotenv()

URL = "https://api.mainnet-beta.solana.com"

DISCRIMINATOR = 986681623081716513
#DISCRIMINATOR = b'!\x0b1b\xb5e\xb1\r'


class  MeteoraRPC:

    def __init__(self, rpc_url: str):
        self.client = Client(rpc_url)

    def get_account(self, pubkey):
        if isinstance(pubkey, str):
            pubkey = Pubkey.from_string(pubkey)

        return self.client.get_account_info(pubkey)
    
    def get_lb_pair(self, pubkey: str | Pubkey):
        if isinstance(pubkey, str):
            pubkey = Pubkey.from_string(pubkey)
        response = self.client.get_account_info(pubkey)
        return LbPair(response.value.data, pubkey, self)     

    def get_position(self, pubkey: str | Pubkey):
        if isinstance(pubkey, str):
              pubkey = Pubkey.from_string(pubkey)
        response = self.client.get_account_info(pubkey)
        return PositionV2(response.value.data)  
    
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
    
    def bytes(self, n):
        value = self.data[self.offset:self.offset+n]
        self.offset += n
        return value
    
    def array(self, func, count):
        result = []

        for _ in range(count):
            result.append(func())
        
        return result
    
    def skip(self, n):
        self.offset += n

    def tell(self):
        return self.offset
    
    def boolean(self):
        return bool(self.u8())
    
class TokenMint:

    def __init__(self, data: bytes):
        data = Reader(data)

        self.mint_authority_option = data.u32()
        self.mint_authority  = data.pubkey()
        self.supply = data.u64()
        self.decimal = data.u8()
        self.is_initialized = data.u8()
  
    
class StaticParameters():

    def __init__(self, r: Reader):
        self.base_factor = r.u16() # for fee_rate
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

class ProtocolFee:

    def __init__(self, r: Reader):
        self.amount_x = r.u64()
        self.amount_y = r.u64()

    def __repr__(self):
        return (
            "\n___ Protocol Fee ___\n"
            f"amount_x: {self.amount_x}\n"
            f"amount_y: {self.amount_y}\n"
        )

class RewardInfo:

    def __init__(self, r: Reader):
        self.mint = r.pubkey()  
        self.vault = r.pubkey()  
        self.funder = r.pubkey()  
        self.reward_duration = r.u64()
        self.reward_duration_end = r.u64()
        self.reward_rate = r.u128()
        self.last_update_time = r.u64()
        self.cumulative_seconds_with_empty_liquidity_reward = r.u64()

    def __repr__(self):
        return (
            "\n___ Reward ___\n"
            f"mint: {self.mint}\n"
            f"vault: {self.vault}\n"
            f"funder: {self.funder}\n"
            f"reward_duration: {self.reward_duration}\n"
            f"reward_duration_end: {self.reward_duration_end}\n"
            f"reward_rate: {self.reward_rate}\n"
            f"last_update_time: {self.last_update_time}\n"
            f"cumulative_seconds_with_empty_liquidity_reward: "
            f"{self.cumulative_seconds_with_empty_liquidity_reward}"
        )


class RewardInfos:

    def __init__(self, r: Reader):
        self.zero = RewardInfo(r)
        self.one = RewardInfo(r)

    def __repr__(self):
        return (
            "\n___ Reward Infos ___\n"
            f"zero: {self.zero}\n"
            f"one: {self.one}\n"
        )
    
class BinArrayBitmap:

    def __init__(self, r: Reader):

        self.values = r.array(r.u64, 16)

    def __repr__(self):
        return (
            "\n___ Bin Array Bitmap ___\n"
            f"values: {self.values}\n"
        )

class Bin:

    def __init__(self, r: Reader):        
        self.amount_x = r.u64()
        self.amount_y = r.u64()
        self.price = r.u128()
        self.liquidity_supply = r.u128()
        self.fulfilled_order_amount_x = r.u64()
        self.fulfilled_order_amount_y = r.u64()
        self.limit_order_fee_ask_side = r.u64()
        self.limit_order_fee_bid_side = r.u64()
        self.fee_amount_x_per_token_stored = r.u128()
        self.fee_amount_y_per_token_stored = r.u128()
        self.open_order_amount = r.u64()
        self.total_processing_order_amount = r.u64()
        self.processed_order_remaining_amount = r.u64()
        self.order_age = r.u32()
        self.limit_order_ask_side = r.u8()
        self.padding1 = r.skip(3)
    
    @property
    def is_empty(self):
        return (
            self.amount_x == 0 and
            self.amount_y == 0
        )    
    
    def __repr__(self):
        return (
            f"amount_x: {self.amount_x}, "
            f"amount_y: {self.amount_y}, "
            f"price: {self.price}\n"
        )
    
class UserRewardInfo:

    def __init__(self, r: Reader):
        self.reward_per_token_completes_0 = r.u128()
        self.reward_per_token_completes_1 = r.u128()
        self.reward_pendings_0 = r.u64()
        self.reward_pendings_1 = r.u64()
    
    def __repr__(self):
        return(
            f"reward_per_token_completes_0: {self.reward_per_token_completes_0},\n"
            f"reward_per_token_completes_1: {self.reward_per_token_completes_1},\n"
            f"reward_pendings_0: {self.reward_pendings_0},\n"
            f"reward_pendings_1: {self.reward_pendings_1},\n"
        )
    
class FeeInfo:

    def __init__(self, r: Reader):
        self.fee_x_per_token_complete = r.u128()
        self.fee_y_per_token_complete = r.u128()
        self.fee_x_pending = r.u64()
        self.fee_y_pending = r.u64()

    def __repr__(self):
        return (
            f"fee_x_per_token_complete: {self.fee_x_per_token_complete},\n"
            f"fee_y_per_token_complete: {self.fee_y_per_token_complete},\n"
            f"fee_x_pending: {self.fee_x_pending},\n"
            f"fee_y_pending: {self.fee_y_pending},\n"
        )
    
class LbPair:

    def __init__(self, data: bytes, address: str | Pubkey, client: MeteoraRPC):
        r = Reader(data)

        if isinstance(address, str):
            self.address = Pubkey.from_string(address)
        
        self.address = address
        self.client = client

        self.discriminator = r.u64()

        if self.discriminator != DISCRIMINATOR:
            raise ValueError("Not a Meteora LbPair account")

        self.parameters = StaticParameters(r)
        self.v_parameters = VariableParameters(r)
        self.bump_seed = r.u8()
        self.bin_step_seed_0 = r.u8()
        self.bin_step_seed_1 = r.u8()
        self.pair_type = r.u8()
        self.active_id = r.i32() #for pool price, from bin id to bin array
        self.bin_step = r.u16() #for pool price, fee_rate
        self.status = r.u8()
        self.require_base_factor_seed = r.u8()
        self.base_factor_seed_0 = r.u8()
        self.base_factor_seed_1 = r.u8()
        self.activation_type = r.u8()
        self.creator_pool_on_off_control = r.u8()
        self.token_x_mint = r.pubkey()
        self.token_y_mint = r.pubkey()
        self.reserve_x = r.pubkey()
        self.reserve_y = r.pubkey()
        self.protocol_fee = ProtocolFee(r)
        self._padding1 = r.skip(32)
        self.reward_infos = RewardInfos(r)
        self.oracle = r.pubkey()
        self.bin_array_bitmap = BinArrayBitmap(r)
        self.last_updated_at = r.i64()
        self._padding2 = r.skip(32)
        self.pre_activation_swap_address = r.pubkey()
        self.base_key = r.pubkey()
        self.activation_point = r.u64()
        self.pre_activation_duration = r.u64()
        self._padding3 = r.skip(8)
        self._padding4 = r.u64()
        self.creator = r.pubkey()
        self.token_mint_x_program_flag = r.u8()
        self.token_mint_y_program_flag = r.u8()
        self.version = r.u8()
        self._reserved = r.skip(21)

    def _load_tokens(self):        
        self._token_x_mint = self.client.get_account(self.token_x_mint)
        self._token_y_mint = self.client.get_account(self.token_y_mint)

        self.x_mint = TokenMint(self._token_x_mint.value.data)
        self.y_mint = TokenMint(self._token_y_mint.value.data)

        return self.x_mint, self.y_mint   
    
    def get_bin_array(self, bin_id: int):
        """Выводит BinArray по bin id"""
        bin_array_index = bin_id_to_bin_array_index(bin_id)
        pda, bump = derive_bin_array_pda(self.address, bin_array_index)
        data_bin_array = self.client.get_account(pda)

        return BinArray(data_bin_array.value.data)      
    
    def get_bin(self, bin_id: int):
        """Выводит Bin из массива BinArray"""
        array = self.get_bin_array(bin_id)
        index = bin_id % 70
        if index < 0:
            index += 70
        return array.bins[index]

    @property
    def price(self):
        x_mint, y_mint = self._load_tokens()
        raw_price = (
            1 + self.bin_step / 10_000
        ) ** self.active_id

        price = raw_price * 10 ** (x_mint.decimal - y_mint.decimal)

        return price
    
    @property
    def fee_rate(self):

        base_fee = (
            self.parameters.base_factor *
            self.bin_step
        )

        return base_fee / 1_000_000
    
    @property
    def variable_fee(self):

        v = self.v_parameters.volatility_accumulator

        return (
            (
                self.bin_step *
                v
            ) ** 2 *
            self.parameters.variable_fee_control
        ) / 1_00_000_000_000_000_000


    @property
    def total_fee(self):

        return (
            self.fee_rate +
            self.variable_fee
        )
    
    @property
    def active_bin(self):
        return self.active_id
    
  
    """     @property
    def min_price(self):

        return (
            1 + self.bin_step / 10000
        ) ** self.parameters.min_bin_id
    
    @property
    def max_price(self):

        return (
            1 + self.bin_step / 10000
        ) ** self.parameters.max_bin_id
     """



    def __repr__(self):
        return (
            "\n___ Lb Pair ___\n"
            f"discriminator: {self.discriminator}\n"
            f"parameters: {self.parameters}\n"
            f"v_parameters: {self.v_parameters}\n"
            f"bump_seed: {self.bump_seed}\n"
            f"bin_step_seed_0: {self.bin_step_seed_0}\n"
            f"bin_step_seed_1: {self.bin_step_seed_1}\n"
            f"pair_type: {self.pair_type}\n"
            f"active_id: {self.active_id}\n"
            f"bin_step: {self.bin_step}\n"
            f"status: {self.status}\n"
            f"require_base_factor_seed: {self.require_base_factor_seed}\n"
            f"base_factor_seed_0: {self.base_factor_seed_0}\n"
            f"base_factor_seed_1: {self.base_factor_seed_1}\n"
            f"activation_type: {self.activation_type}\n"
            f"creator_pool_on_off_control: {self.creator_pool_on_off_control}\n"
            f"token_x_mint: {self.token_x_mint}\n"
            f"token_y_mint: {self.token_y_mint}\n"
            f"reserve_x: {self.reserve_x}\n"
            f"reserve_y: {self.reserve_y}\n"
            f"protocol_fee: {self.protocol_fee}\n"
            f"reward_infos: {self.reward_infos}\n"
            f"oracle: {self.oracle}\n"
            f"bin_array_bitmap: {self.bin_array_bitmap}\n"
            f"last_updated_at: {self.last_updated_at}\n"
            f"pre_activation_swap_address: {self.pre_activation_swap_address}\n"
            f"base_key: {self.base_key}\n"
            f"activation_point: {self.activation_point}\n"
            f"pre_activation_duration: {self.pre_activation_duration}\n"
            f"creator: {self.creator}\n"
            f"token_mint_x_program_flag: {self.token_mint_x_program_flag}\n"
            f"token_mint_y_program_flag: {self.token_mint_y_program_flag}\n"
            f"version: {self.version}\n"
        )
    
class BinArray:

    def __init__(self, data):
        r = Reader(data)
        self.discriminator = r.u64()
        self.index = r.i64()
        self.version = r.u8()
        self.padding1 = r.skip(7)
        self.lb_pair = r.pubkey()
        self.bins = [Bin(r) for _ in range(70)]
    
    def __repr__(self):
        return(
            f"index: {self.index}\n"
            f"version: {self.version}\n"
            f"lb_pair: {self.lb_pair}\n"
            f"bins: {self.bins}\n"
        )
    
class PositionV2:

    def __init__(self, data):
        r = Reader(data)
        self.discriminator = r.u64()
        self.lb_pair = r.pubkey()
        self.owner = r.pubkey()
        self.liquidity_shares = r.array(r.u128, 70)
        self.reward_infos = [UserRewardInfo(r) for _ in range(70)]
        self.fee_infos = [FeeInfo(r) for _ in range(70)]
        self.lower_bin_id = r.i32()
        self.upper_bin_id = r.i32()
        self.last_updated_at = r.i64()
        self.total_claimed_fee_x_amount = r.u64()
        self.total_claimed_fee_y_amount = r.u64()
        self.total_claimed_rewards_0 = r.u64()
        self.total_claimed_rewards_1 = r.u64()
        self.operator = r.pubkey()
        self.lock_release_point = r.u64()
        self.padding0 = r.skip(1)
        self.fee_owner = r.pubkey()
        self.version = r.u8()
        self.permissionless_operation_bits = r.u8()
        self.reserved = r.skip(85)

    @property
    def bin_ids(self):
        return list(
            range(
                self.lower_bin_id,
                self.upper_bin_id + 1,
            )
        )
    
    @property
    def width(self):
        return self.upper_bin_id - self.lower_bin_id + 1    

    def in_range(self, active_id):
        return (
            self.lower_bin_id <=
            active_id <=
            self.upper_bin_id
        )

    def __repr__(self):
        return (
            f"lb_pair: {self.lb_pair},\n"
            f"owner: {self.owner},\n"
            f"liquidity_shares: {self.liquidity_shares},\n"
            #f"reward_infos: {self.reward_infos},\n"
            #f"fee_infos: {self.fee_infos},\n"
            f"lower_bin_id: {self.lower_bin_id},\n"
            f"upper_bin_id: {self.upper_bin_id},\n"
            f"last_updated_at: {self.last_updated_at},\n"
            f"total_claimed_fee_x_amount: {self.total_claimed_fee_x_amount},\n"
            f"total_claimed_fee_y_amount: {self.total_claimed_fee_y_amount},\n"
            f"total_claimed_rewards_0: {self.total_claimed_rewards_0},\n"
            f"total_claimed_rewards_1: {self.total_claimed_rewards_1},\n"
            f"operator: {self.operator},\n"
            f"lock_release_point: {self.lock_release_point},\n"
            f"fee_owner: {self.fee_owner},\n"
            f"version: {self.version},\n"
            f"permissionless_operation_bits: {self.permissionless_operation_bits},\n"
        )
    


    
rpc = MeteoraRPC(URL)

#lb_pair = rpc.get_lb_pair("2TkcXuNdiWE6GPg68SC7koE4C6wdZTvA3bk7CQU6iPAu") #meteora Meowpin-SOL Fee: 3.00% • Bin Step: 100
#account = rpc.get_account("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd") #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
#account = rpc.get_account("HTvjzsfX3yU6BUodCjZ5vZkUrAxMDTrBs3CJaq43ashR") #meteora SOL-USDC Fee: 0.01% • Bin Step: 1
#account = rpc.get_account("6F4rVnmVc1A2QDqpHn5cpQZfXugapFbGZTXEyaakpvVQ") #meteora HYPE-USDC Fee: 0.10% • Bin Step: 10
#account = rpc.get_account("98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g") 
#account = rpc.get_account("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo")

position = rpc.get_position("4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq")
#print(account)

#print(account)
#print("-"*50)

#data = bytes(account.value.data)
#lb = LbPair(data, "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd", rpc)
#print(lb.total_liquidity)

#print(lb.price)
#print(lb.fee_rate)
#print(lb.variable_fee)
#print(lb.total_fee)

#print(lb_pair.active_bin)
#print(lb_pair.price)
#print(lb_pair.total_fee)
#print(lb_pair.parameters.base_fee_power_factor)
#print(lb_pair.get_bin(lb_pair.active_id))

print(position.bin_ids)
print(position.in_range(214))

""" lb_pair = Pubkey.from_string("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
base = Pubkey.from_string("6NYPquPNfZALPDCVLTjADvzVsarRriGi1HS26ydo6s2C")

pda, bump = derive_position_pda(lb_pair=lb_pair,
    base=base,
    lower_bin_id=213,
    width=69,
) 

print(pda)"""

##position_bin_data, bump2 = derive_position_bin_data_pda(lb_pair)
#print(position_bin_data)
#4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq
