import pytest
from meteora.rpc import MeteoraRPC, LbPair, URL

def test_lb_pair_price():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address) #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)
    print("lb.price: ", lb.price)
    assert lb.price < 1

def test_lb_pair_fee_rate():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address) #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)
    print("lb.fee_rate: ",lb.fee_rate)
    assert lb.fee_rate == 0.1

def test_lb_pair_variable_fee():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address) #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)
    print("lb.variable_fee: ",lb.variable_fee)
    assert lb.variable_fee >= 0

def test_lb_pair_total_fee():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address) #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)
    print("lb.total_fee: ",lb.total_fee)
    assert lb.total_fee >= 0.1

def test_lb_pair_active_bin():
    rpc = MeteoraRPC(URL)
    pool_address = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
    account = rpc.get_account(pool_address) #meteora USDC-SOL Fee: 0.10% • Bin Step: 100
    data = bytes(account.value.data)
    lb = LbPair(data, pool_address, rpc)
    print("lb.active_bin: ",lb.active_bin)
    assert lb.active_bin >= 0