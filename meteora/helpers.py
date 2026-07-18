def bin_id_to_bin_array_index(bin_id: int) -> int:
    quotient = int(bin_id / 70)      
    remainder = bin_id - quotient * 70

    if bin_id < 0 and remainder != 0:
        quotient -= 1

    return quotient