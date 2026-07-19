from solders.pubkey import Pubkey

PROGRAM_ID = Pubkey.from_string(
    "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"
)

def derive_bin_array_pda(base_key: str | Pubkey,
                         array_index: int):

    if isinstance(base_key, str):
        base_key = Pubkey.from_string(base_key)

    pda, bump = Pubkey.find_program_address(
        [
            b"bin_array",
            bytes(base_key),
            array_index.to_bytes(8, "little", signed=True),
        ],
        PROGRAM_ID,
    )

    return pda, bump

def derive_position_pda(lb_pair: Pubkey,
    base: Pubkey,
    lower_bin_id: int,
    width: int,
):
    pda, bump = Pubkey.find_program_address(
        [
            b"position",
            bytes(lb_pair),
            bytes(base),
            lower_bin_id.to_bytes(4, "little", signed=True),
            width.to_bytes(4, "little", signed=False),
        ],
        PROGRAM_ID,
    )

    return pda, bump

#derive_position_pda()
#derive_oracle_pda()
#derive_bin_array_pda()
#derive_event_authority_pda()