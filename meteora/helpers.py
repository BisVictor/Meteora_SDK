from solders.pubkey import Pubkey

def bin_id_to_bin_array_index(active_id: int) -> int:
    quotient = int(active_id / 70)      
    remainder = active_id - quotient * 70

    if active_id < 0 and remainder != 0:
        quotient -= 1

    return quotient

def bin_array_index_from_bitmap(index: int, bitmap_values: int):
    count = 0
    array = []

    if index < 8:
        for bit in range(64,-1,-1):

            if (bitmap_values >> bit) & 1:            
                array.append(count*-1)
            count += 1   

    else:
        for bit in range(64):

            if (bitmap_values >> bit) & 1:            
                array.append(count)
            count += 1

    return array

def normalize_pubkey(pubkey: str | Pubkey) -> Pubkey:
    if isinstance(pubkey, str):
        pubkey = Pubkey.from_string(pubkey)

    elif type(pubkey) != Pubkey and type(pubkey) != str:
        raise ValueError("Pubkey must be str or type Pubkey")

    return pubkey

def get_bin_index(bin_id: int):    
    if bin_id < 0:
        bin_id = abs(bin_id) - 1

    return bin_id % 70

def require_account(response, pubkey=None):
    """Проверяет, что RPC вернул аккаунт."""
    if response is None or response.value is None:
        where = f" ({pubkey})" if pubkey is not None else ""
        raise ValueError(f"Account not found{where}")
    
    return response
