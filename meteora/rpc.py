from solana.rpc.api import Client
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey
from dotenv import load_dotenv
from typing import Dict, Tuple, Optional, List
import os

from .helpers import bin_id_to_bin_array_index, bin_array_index_from_bitmap, normalize_pubkey, get_bin_index, require_account
from .pda import PROGRAM_ID, derive_bin_array_pda, derive_position_pda, derive_position_bin_data_pda

import struct

load_dotenv()

URL = "https://api.mainnet-beta.solana.com"

DISCRIMINATOR = 986681623081716513

FEE_PRECISION = 1_000_000_000
MAX_FEE_RATE = 100_000_000  # 10%

class  MeteoraRPC:    
    def __init__(self, rpc_url: str):
        self.client = Client(rpc_url)

    def get_account(self, pubkey: str | Pubkey):
        pubkey = normalize_pubkey(pubkey)
        response = self.client.get_account_info(pubkey)

        return require_account(response, pubkey)

    def get_multiple_accounts(self, pubkeys: list):
        if not pubkeys:
            return []
        
        pubkeys = [normalize_pubkey(i) for i in pubkeys]
        response = self.client.get_multiple_accounts(pubkeys, encoding="base64")
        if response is None or response.value is None:
            raise ValueError("get_multiple_accounts failed")
        
        return response.value

    
    def get_lb_pair(self, pubkey: str | Pubkey):
        pubkey = normalize_pubkey(pubkey)
        response = self.client.get_account_info(pubkey)
        account = require_account(response, pubkey)

        return LbPair(account.value.data, pubkey, self)     

    def get_position(self, pubkey: str | Pubkey):
        pubkey = normalize_pubkey(pubkey)
        response = self.client.get_account_info(pubkey)
        account = require_account(response, pubkey)

        return PositionV2(account.value.data, self)  

    def get_positions(self, pubkey: str | Pubkey):
        pubkey = normalize_pubkey(pubkey)
        response = self.client.get_program_accounts(
            PROGRAM_ID,
            encoding="base64",
            filters=[
                MemcmpOpts(
            offset=40,
            bytes=str(pubkey),
                            )
                    ]
            )
        if response is None or response.value is None:
                    raise ValueError("get_multiple_accounts failed")
        
        return [PositionV2(i.account.data, self) for i in response.value]

    def get_bin_array(self, pubkey: str | Pubkey):
        pubkey = normalize_pubkey(pubkey)
        response = self.client.get_account_info(pubkey)
        account = require_account(response, pubkey)

        return BinArray(account.value.data, self)  
    
    def get_balance(self, pubkey: str | Pubkey):
        pubkey = normalize_pubkey(pubkey)
        
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
        self.rewards = [
            RewardInfo(r),
            RewardInfo(r)
        ]

    def __repr__(self):
        return (
            "\n___ Reward Infos ___\n"
            f"rewards: {self.rewards}\n"            
        )
    
class BinArrayBitmap:

    def __init__(self, r: Reader):

        self.values = r.array(r.u64, 16)

    def __repr__(self):
        return (
            "\n___ Bin Array Bitmap ___\n"
            f"values: {self.values}\n"
        )
    def __len__(self):
        return len(self.values)

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
            address = Pubkey.from_string(address)
        
        self.address = address
        self.client = client

        self._x_mint = None
        self._y_mint = None

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
        if self._x_mint is not None and self._y_mint is not None:
            return self._x_mint, self._y_mint

        x_acc = self.client.get_account(self.token_x_mint)
        y_acc = self.client.get_account(self.token_y_mint)

        self._x_mint = TokenMint(x_acc.value.data)
        self._y_mint = TokenMint(y_acc.value.data)
   
        self.x_mint = self._x_mint
        self.y_mint = self._y_mint
        print("load_tokens is work")

        return self._x_mint, self._y_mint   
    
    def get_bin(self, bin_id: int) -> Bin:
        """Выводит Bin из массива BinArray"""
        # проверить на отрицательные числа!!!
        array = self.get_bin_array(bin_id)
        index = get_bin_index(bin_id)

        return array.bins[index]
    
    def get_bins(self, lower_bin_id: int, upper_bin_id: int):
        l_bin_id = lower_bin_id
        u_bin_id = upper_bin_id + 1

        if lower_bin_id > upper_bin_id:
            lower_bin_id, upper_bin_id = upper_bin_id, lower_bin_id
            
        if lower_bin_id < 0:
            lower_bin_id -= 69

        bin_array_list = []
        bin_list = []

        min_bin_array = int(lower_bin_id / 70)
        max_bin_array = int(upper_bin_id / 70)

        if min_bin_array == max_bin_array:            
            bin_array_list.append(self.get_bin_array(lower_bin_id))
        else:
            for _ in range(min_bin_array, max_bin_array+1):
                bin_array = self.get_bin_array(lower_bin_id)
                bin_array_list.append(bin_array)
                lower_bin_id += 70

        for i in range(l_bin_id, u_bin_id):
            index = get_bin_index(i)
            for bin_array in bin_array_list:
                if bin_array.index == bin_id_to_bin_array_index(i):
                    bin_list.append(bin_array.bins[index])

        return bin_list

    def get_bin_array(self, bin_id: int):
        """Выводит BinArray по bin id"""
        bin_array_index = bin_id_to_bin_array_index(bin_id)
        pda, bump = derive_bin_array_pda(self.address, bin_array_index)
        data_bin_array = self.client.get_account(pda)

        return BinArray(data_bin_array.value.data, self.client)  

    def get_bin_arrays(self, lower_bin_id: int, upper_bin_id: int):
        lower = bin_id_to_bin_array_index(lower_bin_id)
        upper = bin_id_to_bin_array_index(upper_bin_id)
       
        bin_arrays = []
        for index in range(lower, upper+1):
            pda, _ =derive_bin_array_pda(self.address, index)
            account = self.client.get_account(pda)
            bin_arrays.append(BinArray(account.value.data, self.client))

        return bin_arrays

    def bin_arrays_index_from_bitmap(self):         
        matrix = []

        for i, value in enumerate(self.bin_array_bitmap.values):           
            if value > 0:
                matrix.append(
                    bin_array_index_from_bitmap(i, value)
                )

        return [x for row in matrix for x in row]
        
    def get_position(self, owner: str | Pubkey,
                     lower_bin_id: int,
                     upper_bin_id: int):
        if isinstance(owner, str):
            owner = Pubkey.from_string(owner)

        wide = upper_bin_id - lower_bin_id + 1
        
        pda, bump = derive_position_pda(
            self.address,
            base=owner,
            lower_bin_id=lower_bin_id,
            width=wide
        )

        return self.client.get_position(pda)

    def get_liquidity_in_range(self, lower: int, upper: int):
        if lower > upper:
            lower, upper = upper, lower

        bins = self.get_bins(lower, upper)
        total_x = 0
        total_y = 0

        for bin in bins:
            x = bin.amount_x
            y = bin.amount_y
            total_x += x
            total_y += y                 

        return total_x, total_y

    def get_liquidity_in_arrays(self, arrays: list):
        if not arrays:
            return 0, 0
        
        total_x = 0
        total_y = 0
        pdas = []

        for index in arrays:            
            pda, bump = derive_bin_array_pda(self.address, index)
            pdas.append(pda)

        accounts = self.client.get_multiple_accounts(pdas)

        for acc in accounts:
            if acc is None:
                continue
            bin_array = BinArray(acc.data, self.client)
            x, y = bin_array.liquidity
            total_x += x
            total_y += y

        return total_x, total_y            

    def swap_quote(
        self,
        amount_in: float,
        swap_for_y: bool,
        slippage_bps: int = 100,   # 100 = 1%
        max_bins: int = 40,
                    ) -> dict:
        """
        Preview свопа (упрощённый, human units).

        amount_in   — UI units (например 100.0 USDC)
        swap_for_y  — True: X→Y, False: Y→X
        slippage_bps — допуск проскальзывания в basis points

        Returns dict с amount_out, fee, min_out, impact, bins_crossed, exhausted.
            """
        if amount_in <= 0:
            raise ValueError("amount_in must be > 0")

        x_mint, y_mint = self._load_tokens()
        x_dec, y_dec = x_mint.decimal, y_mint.decimal

        # --- 1. Fee (упрощённо: одним куском от всего входа) ---        
        fee_rate = max(self.total_fee, 0.0)
        fee = amount_in * fee_rate
        amount_left = amount_in - fee
        if amount_left <= 0:
            return {
                "amount_in": amount_in,
                "amount_out": 0.0,
                "fee": fee,
                "min_out": 0.0,
                "bins_crossed": 0,
                "swap_for_y": swap_for_y,
                "exhausted": True,
                "price_impact": 0.0,
                "start_price": self.price,
                "end_price": self.price,
                "note": "amount_in too small after fee",
            }

        # --- 2. Старт ---
        total_out = 0.0
        bins_crossed = 0
        bin_id = self.active_id
        step = -1 if swap_for_y else 1  # X→Y вниз, Y→X вверх
        start_price = self._price_at_bin(bin_id)
        start_bin_used = None  # первый бин, где реально что-то съели

        # --- 3. Проход по бинам ---
        while amount_left > 1e-12 and bins_crossed < max_bins:
            try:
                b = self.get_bin(bin_id)
            except Exception:
                break

            bin_x = b.amount_x / (10 ** x_dec)
            bin_y = b.amount_y / (10 ** y_dec)
            p = self._price_at_bin(bin_id)

            if p <= 0:
                bin_id += step
                bins_crossed += 1
                continue

            if swap_for_y:
                # X → Y: нужен Y в бине
                if bin_y <= 0:
                    bin_id += step
                    bins_crossed += 1
                    continue

                # max X, который бин переварит: out_y = in_x * p  => in_x = bin_y / p
                max_in = bin_y / p
                used_in = min(amount_left, max_in)
                out = used_in * p
            else:
                # Y → X: нужен X в бине
                if bin_x <= 0:
                    bin_id += step
                    bins_crossed += 1
                    continue

                # out_x = in_y / p  => max_in_y = bin_x * p
                max_in = bin_x * p
                used_in = min(amount_left, max_in)
                out = used_in / p

            if used_in <= 0:
                bin_id += step
                bins_crossed += 1
                continue

            if start_bin_used is None:
                start_bin_used = bin_id

            amount_left -= used_in
            total_out += out
            bins_crossed += 1

            if amount_left > 1e-12:
                bin_id += step

        # --- 4. Итоги ---
        end_price = self._price_at_bin(bin_id)
        if start_price > 0:
            price_impact = abs(end_price - start_price) / start_price
        else:
            price_impact = 0.0

        # min_out с учётом slippage (bps)
        min_out = total_out * (1 - slippage_bps / 10_000)

        return {
            "amount_in": amount_in,
            "amount_out": total_out,
            "fee": fee,
            "amount_left": amount_left,
            "min_out": min_out,
            "bins_crossed": bins_crossed,
            "swap_for_y": swap_for_y,
            "start_price": start_price,
            "end_price": end_price,
            "price_impact": price_impact,
            "exhausted": amount_left > 1e-9,
            "start_bin": start_bin_used,
            "end_bin": bin_id,
            "slippage_bps": slippage_bps,
        }
    
    @property
    def tvl(self):
        bin_arrays = self.bin_arrays_index_from_bitmap()
        total_x, total_y = self.get_liquidity_in_arrays(bin_arrays)

        x_mint, y_mint = self._load_tokens()
        price = self.price

        x = total_x / 10 ** x_mint.decimal
        y = total_y / 10 ** y_mint.decimal

        return {
        "x_raw": total_x,
        "y_raw": total_y,
        "x": x,
        "y": y,
        "price_x_in_y": price,
        "tvl_in_x": x + (y / price if price else 0),
        "tvl_in_y": y + x * price,
        "bin_arrays_count": len(bin_arrays)
        }

    @property
    def price(self) -> float:
        x_mint, y_mint = self._load_tokens()
        raw_price = (
            1 + self.bin_step / 10_000
        ) ** self.active_id

        price = raw_price * 10 ** (x_mint.decimal - y_mint.decimal)

        return price

    def _price_at_bin(self, bin_id: int):
        x_mint, y_mint = self._load_tokens()
        raw_price = (
                    1 + self.bin_step / 10_000
                ) ** bin_id

        price = raw_price * 10 ** (x_mint.decimal - y_mint.decimal)
        
        return price
    
    """     @property
    def fee_rate(self):

        base_fee = (
            self.parameters.base_factor *
            self.bin_step
        )

        return base_fee / 1_000_000 """

    @property
    def fee_rate(self) -> float:
        """Base fee как доля (0.001 = 0.1%)."""
        return self.fee_rate_raw / FEE_PRECISION

    @property
    def variable_fee(self) -> float:
        return self.variable_fee_raw / FEE_PRECISION

    @property
    def total_fee(self) -> float:
        """Total fee как доля 0..1 для swap_quote."""
        return self.total_fee_raw / FEE_PRECISION
        
    """     @property
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
        ) """
    
    @property
    def active_bin(self):
        return self.active_id

    @property
    def fee_rate_raw(self) -> int:
        """Base fee в precision 1e9."""
        p = self.parameters
        return (
            p.base_factor
            * self.bin_step
            * 10
            * (10 ** p.base_fee_power_factor)
        )

    @property
    def variable_fee_raw(self) -> int:
        """Variable fee в precision 1e9."""
        p = self.parameters
        v = self.v_parameters.volatility_accumulator
        if p.variable_fee_control == 0:
            return 0
        numer = p.variable_fee_control * (v * self.bin_step) ** 2
        # ceil division
        return (numer + 100_000_000_000 - 1) // 100_000_000_000

    @property
    def total_fee_raw(self) -> int:
        total = self.fee_rate_raw + self.variable_fee_raw
        return min(total, MAX_FEE_RATE)
    
  




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

    def __init__(self, data: bytes, client: MeteoraRPC):
        r = Reader(data)
        self.client = client

        self.discriminator = r.u64()
        self.index = r.i64()
        self.version = r.u8()
        self.padding1 = r.skip(7)
        self.lb_pair = r.pubkey()
        self.bins = [Bin(r) for _ in range(70)]

    @property
    def liquidity(self):
        total_x = 0
        total_y = 0

        for bin in self.bins:            
            total_x += bin.amount_x
            total_y += bin.amount_y            

        return total_x, total_y
    
    def __repr__(self):
        return(
            f"index: {self.index}\n"
            f"version: {self.version}\n"
            f"lb_pair: {self.lb_pair}\n"
            f"bins: {self.bins}\n"
        )
    
class PositionV2:

    def __init__(self, data: bytes, client: MeteoraRPC):
        r = Reader(data)
        self.client = client

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

    def get_unclaimed_fees_raw(self) -> Tuple[int, int]:
        """Возвращает сырые значения (в lamports/atomic units)"""
        fee_x = sum(info.fee_x_pending for info in self.fee_infos)
        fee_y = sum(info.fee_y_pending for info in self.fee_infos)
        return fee_x, fee_y

    def get_unclaimed_fees(self, lb_pair: Optional["LbPair"] = None) -> Tuple[float, float]:
        """Human-readable fees"""
        fee_x_raw, fee_y_raw = self.get_unclaimed_fees_raw()

        if lb_pair is None:
            lb_pair = self.client.get_lb_pair(self.lb_pair)

        x_mint, y_mint = lb_pair._load_tokens()

        return (
            fee_x_raw / 10 ** x_mint.decimal,
            fee_y_raw / 10 ** y_mint.decimal,
        )
    
    def get_amounts(self, lb_pair=None):
        if lb_pair is None:
            lb_pair = self.client.get_lb_pair(self.lb_pair)     
        
        x_mint, y_mint = lb_pair._load_tokens()
        bins = lb_pair.get_bins(self.lower_bin_id, self.upper_bin_id)

        total_x = 0
        total_y = 0

        for i in range(len(bins)):            
            one_bin = bins[i]            

            if self.liquidity_shares[i] == 0 or one_bin.liquidity_supply == 0:
                continue

            amount_x = (self.liquidity_shares[i] * one_bin.amount_x) // one_bin.liquidity_supply
            amount_y = (self.liquidity_shares[i] * one_bin.amount_y) // one_bin.liquidity_supply

            total_x += amount_x
            total_y += amount_y

        return {
        "x_raw": total_x,
        "y_raw": total_y,
        "x": total_x / 10 ** x_mint.decimal,
        "y": total_y / 10 ** y_mint.decimal        
        }

    def get_value(self, lb_pair=None):
        if lb_pair is None:
            lb_pair = self.client.get_lb_pair(self.lb_pair) 

        price = lb_pair.price
        amounts = self.get_amounts(lb_pair)
        x = amounts["x"]   
        y = amounts["y"]   

        value_in_x = x + (y / price if price else 0)   # в USDC
        value_in_y = y + x * price                     # в SOL

        return {        
        "value_in_x": value_in_x,
        "value_in_y": value_in_y,
        }
       

    def in_range(self, active_id):
        return (
            self.lower_bin_id <=
            active_id <=
            self.upper_bin_id
        )
    

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
    

#lb_pair = rpc.get_lb_pair("2TkcXuNdiWE6GPg68SC7koE4C6wdZTvA3bk7CQU6iPAu") #meteora Meowpin-SOL Fee: 3.00% • Bin Step: 100
#account = rpc.get_account("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd") #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
#account = rpc.get_account("HTvjzsfX3yU6BUodCjZ5vZkUrAxMDTrBs3CJaq43ashR") #meteora SOL-USDC Fee: 0.01% • Bin Step: 1
#account = rpc.get_account("6F4rVnmVc1A2QDqpHn5cpQZfXugapFbGZTXEyaakpvVQ") #meteora HYPE-USDC Fee: 0.10% • Bin Step: 10
#account = rpc.get_account("98sMhvDwXj1RQi5c5Mndm3vPe9cBqPrbLaufMXFNMh5g") 
#account = rpc.get_account("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo")

#rpc = MeteoraRPC(URL)
#pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
#arrays = pool.bin_arrays_index_from_bitmap()
#print(arrays)
#print(pool.get_liquidity_in_arrays(arrays))

#position_address = "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq"
#position = rpc.get_position(position_address)
#position.get_amounts()