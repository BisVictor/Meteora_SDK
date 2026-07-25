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