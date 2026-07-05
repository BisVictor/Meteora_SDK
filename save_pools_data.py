import csv
import os
from datetime import datetime
import requests
from models import *
from dotenv import load_dotenv

load_dotenv()

FILE_NAME = "meteora_positions.csv"

HEADER = [
    "date",
    "timestamp",
    "createdAt",
    "position",
    "pool",
    "SOLprice",
    "pnlUsd",
    "pnlSOL",
    "%USD",
    "%SOL",
    "feePerTvl24h",
    "minPrice",
    "maxPrice",
    "activePrice",
    "outOfRange",
    "Current_deposit",
    "Current_depositSOL",
    "Total_current_balanceUsd",
    "Total_current_balanceSOL",
    "withdraw_feesUsd",
    "rewardsUsd",
    "depositUsd",
    "depositSOL",
]   

def save_position(meteora_data: MeteoraPoolData, pool: str)-> None:
    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if (not file_exists) or os.path.getsize(FILE_NAME) == 0:
            writer.writerow(HEADER)
        for position in meteora_data.positions:
            #position = meteora_data.positions[i]
            writer.writerow([
                #date
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                #timestamp
                int(datetime.now().timestamp()),
                #createdAt
                position.createdAt,
                #position addres
                position.address,
                #pool
                pool,
                #SOLprice
                round(meteora_data.solPrice, 2),
                #pnlUsd
                round(position.pnlUsd, 2),
                #pnlSOL
                round(position.pnlSol, 2),
                #%USD
                round(position.pnlPctChange, 2),
                #%SOL
                round(position.pnlSolPctChange, 2),
                #feePerTvl24h
                round(position.feePerTvl24h, 2),
                #minPrice
                round(position.minPrice, 6),
                #maxPrice
                round(position.maxPrice, 6),
                #activePrice
                round(position.poolActivePrice, 6),
                #outOfRange
                position.isOutOfRange, 
                #Current_deposit
                round(position.unrealizedPnl.balances, 2),
                #Current_depositSOL
                round(position.unrealizedPnl.balancesSol, 2),
                #Total_current_balanceUsd
                round(position.total_current_balance_usd, 2),
                #Total_current_balanceSOL
                round(position.total_current_balance_sol, 2),
                #withdraw_feesUsd
                round(position.allTimeFees.total_usd, 2),
                #rewardsUsd
                round(position.rewards_usd, 2),
                #depositUsd
                round(position.allTimeDeposits.total_usd, 2),
                #depositSOL
                round(position.allTimeDeposits.total_sol, 2),
            ])


user = os.getenv("USER_PUBLIC_KEY")
pool1 = os.getenv("POOL1")
pool2 = os.getenv("POOL2")

client = MeteoraClient(user)
data1 = client.get_positions(pool1)
data2 = client.get_positions(pool2)
#pool = client.get_pool(pool1)
#print(pool)

save_position(data1, pool="USDC-SOL")
save_position(data2, pool="SPCX-USDC")
print("All is OK")

