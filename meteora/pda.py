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

#derive_position_pda()
#derive_oracle_pda()
#derive_bin_array_pda()
#derive_event_authority_pda()