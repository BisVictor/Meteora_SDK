import pytest
from meteora.rpc import MeteoraRPC, LbPair, Bin, URL

""" def test_1_lb_pair_price():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address)  # Meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)

    print("lb.price:", lb.price)

    assert lb.price < 1


def test_2_lb_pair_fee_rate():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address)  # Meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)

    print("lb.fee_rate:", lb.fee_rate)

    assert lb.fee_rate == 0.1


def test_3_lb_pair_variable_fee():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address)  # Meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)

    print("lb.variable_fee:", lb.variable_fee)

    assert lb.variable_fee >= 0


def test_4_lb_pair_total_fee():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address)  # Meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)

    print("lb.total_fee:", lb.total_fee)

    assert lb.total_fee >= 0.1


def test_5_lb_pair_active_bin():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address)  # Meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)

    print("lb.active_bin:", lb.active_bin)

    assert lb.active_bin >= 0

def test_6_position_bin_ids():
    rpc = MeteoraRPC(URL)
    position_address = "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq"
    position = rpc.get_position(position_address)
    print("position.bin_ids: ", position.bin_ids)

    assert position.bin_ids != None
    assert isinstance(position.bin_ids, list)
    
def test_7_position_in_range():
    rpc = MeteoraRPC(URL)
    pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
    position_address = "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq"
    position = rpc.get_position(position_address)

    print("position.in_range(pool.active_bin): ", position.in_range(pool.active_bin))

    assert position.in_range(pool.active_bin) == True
    assert isinstance(position.in_range(pool.active_bin), bool)

def test_8_lb_pair_get_bin():
    rpc = MeteoraRPC(URL)
    pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
    bin = pool.get_bin(pool.active_bin)

    print("pool.get_bin(pool.active_bin): ", bin)

    assert isinstance(bin, Bin)

def test_9_lb_pair_get_bins():
    rpc = MeteoraRPC(URL)
    pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
    bin = pool.get_bins(100, 105)

    print("pool.get_bins(100, 105)): ", bin)

    assert isinstance(bin, list)

def test_10_position_get_unclaimed_fees():
    rpc = MeteoraRPC(URL)    
    position_address = "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq"
    position = rpc.get_position(position_address)

    x, y = position.get_unclaimed_fees()
    print("osition.get_unclaimed_fees): ", x, y)

def test_11_lb_pair_get_bins():
    rpc = MeteoraRPC(URL)
    pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
    bin = pool.get_liquidity_in_range(260, 266)

    print("pool.get_liquidity_in_range(100, 105)): ", bin)   """

def test_12_lb_pair_bin_arrays_index_from_bitmap():
    a = 265 % 70
    b = 200 % 70
    c = 280 % 70

    print(a, b, c)

    rpc = MeteoraRPC(URL)
    #pool = rpc.get_lb_pair("GMcDowNwC6yozAeZZHgJWMmH7gUpudDq55C84uv1WQkn")
    pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
    bit_map = pool.bin_array_bitmap
    print("len: ",len(pool.bin_array_bitmap))
    print(pool.bin_array_bitmap)
    print(f"{pool.bin_array_bitmap.values[8]:064b}")
    print(pool.active_bin)
    print(pool.bin_arrays_index_from_bitmap())

def test_13_lb_pair_get_liquidity_in_arrays():
    rpc = MeteoraRPC(URL)
    pool = rpc.get_lb_pair("AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd")
    arrays = pool.bin_arrays_index_from_bitmap()
    print(arrays)
    print(pool.get_liquidity_in_arrays(arrays))