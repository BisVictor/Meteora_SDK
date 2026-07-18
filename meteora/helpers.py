def bin_id_to_bin_array_index(active_id: int) -> int:
    quotient = int(active_id / 70)      
    remainder = active_id - quotient * 70

    if active_id < 0 and remainder != 0:
        quotient -= 1

    return quotient