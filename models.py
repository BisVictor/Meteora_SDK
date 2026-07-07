import requests
from enum import Enum

BASE_URL = "https://dlmm.datapi.meteora.ag"

class TokenValue:

    def __init__(self, p):
        self.amount = float(p.get("amount", 0))
        self.usd = float(p.get("usd", 0))
        self.sol = float(p.get("amountSol", 0))

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ActivePoolSort(str, Enum):
    CURRENT_BALANCES = "current_balances"
    UNCLAIMED_FEE = "unclaimed_fee"
    FEE_PER_TVL24H = "fee_per_tvl24h"

class TokenInfo:

    def __init__(self, p):
        self.address = p.get("address")
        self.name = p.get("name")
        self.symbol = p.get("symbol")

        self.decimals = int(p.get("decimals", 0))
        self.is_verified = bool(p.get("is_verified", False))

        self.holders = int(p.get("holders", 0))
        self.freeze_authority_disabled = bool(p.get("freeze_authority_disabled", False))

        self.total_supply = float(p.get("total_supply", 0))
        self.price = float(p.get("price", 0))
        self.market_cap = float(p.get("market_cap", 0))

class PoolConfig:

    def __init__(self, p):
        self.bin_step = int(p.get("bin_step", 0))
        self.base_fee_pct = float(p.get("base_fee_pct", 0))
        self.max_fee_pct = float(p.get("max_fee_pct", 0))
        self.protocol_fee_pct = float(p.get("protocol_fee_pct", 0))
        self.collect_fee_mode = int(p.get("collect_fee_mode", 0))

class PoolMetrics:

    def __init__(self, p):
        self.m30 = float(p.get("30m", 0))
        self.h1 = float(p.get("1h", 0))
        self.h2 = float(p.get("2h", 0))
        self.h4 = float(p.get("4h", 0))
        self.h12 = float(p.get("12h", 0))
        self.h24 = float(p.get("24h", 0))

class CumulativeMetrics:

    def __init__(self, p):
        self.volume = float(p.get("volume", 0))
        self.fees = float(p.get("fees", 0))

class Amounts:

    def __init__(self, p):
        #temp 
        total = p.get("total", {})
        #token X & Y
        self.tokenX = TokenValue(p.get("tokenX", {}))
        self.tokenY = TokenValue(p.get("tokenY", {}))        
        #total        
        self.total_usd = float(total.get("usd", 0))
        self.total_sol = float(total.get("sol", 0))

class UnrealizedPnl:
    def __init__(self, p):
        self.balances = float(p.get("balances", 0)) 
        self.balancesSol = float(p.get("balancesSol", 0))
        self.balanceTokenX = TokenValue(p.get("balanceTokenX", {}))
        self.balanceTokenY = TokenValue(p.get("balanceTokenY", {}))
        self.unclaimedFeeTokenX = TokenValue(p.get("unclaimedFeeTokenX", {}))
        self.unclaimedFeeTokenY = TokenValue(p.get("unclaimedFeeTokenY", {}))
        self.unclaimedRewardTokenX = TokenValue(p.get("unclaimedRewardTokenX", {}))
        self.unclaimedRewardTokenY = TokenValue(p.get("unclaimedRewardTokenY", {}))
        

class MeteoraPosition:

    def __init__(self, p):
        self.address = p.get("positionAddress", None)
        self.minPrice =  float(p.get("minPrice", 0))
        self.maxPrice =  float(p.get("maxPrice", 0))
        self.lowerBinId = p.get("lowerBinId", 0)
        self.upperBinId = p.get("upperBinId", 0)
        self.poolActiveBinId = p.get("poolActiveBinId", 0)
        self.isOutOfRange= p.get("isOutOfRange", False)
        self.poolActivePrice =  float(p.get("poolActivePrice", 0))
        self.feePerTvl24h=  float(p.get("feePerTvl24h", 0))
        self.isClosed = p.get("isClosed", False)
        self.createdAt = p.get("createdAt", 0)
        self.closedAt = p.get("closedAt", None)
        self.pnlUsd = float(p.get("pnlUsd", 0))
        self.pnlSol = float(p.get("pnlSol", 0))
        self.pnlPctChange =  float(p.get("pnlPctChange", 0))
        self.pnlSolPctChange =  float(p.get("pnlSolPctChange", 0))
        self.allTimeDeposits = Amounts(p.get("allTimeDeposits", {}))
        self.allTimeWithdrawals = Amounts(p.get("allTimeWithdrawals", {}))
        self.allTimeFees = Amounts(p.get("allTimeFees", {}))
        self.unrealizedPnl = UnrealizedPnl(p.get("unrealizedPnl", {}))

    def __repr__(self):
        return (
            f"MeteoraPosition("
            f"position={self.address}, "
            f"pnl={self.pnlUsd:.2f}, "
            f"balance={self.total_current_balance_usd:.2f})"
        )

    @property
    def total_current_balance_usd(self):
        return (self.unrealizedPnl.balances
                + self.unrealizedPnl.unclaimedFeeTokenX.usd
                + self.unrealizedPnl.unclaimedFeeTokenY.usd
                + self.allTimeFees.total_usd)
    
    @property
    def total_current_balance_sol(self):
        return (self.unrealizedPnl.balancesSol
                + self.unrealizedPnl.unclaimedFeeTokenX.sol 
                + self.unrealizedPnl.unclaimedFeeTokenY.sol 
                + self.allTimeFees.total_sol)
    
    @property
    def rewards_usd(self):
        return (self.unrealizedPnl.unclaimedRewardTokenX.usd 
                + self.unrealizedPnl.unclaimedRewardTokenY.usd)
    
    @property
    def fees_usd(self):
        return (
            self.unrealizedPnl.unclaimedFeeTokenX.usd
            + self.unrealizedPnl.unclaimedFeeTokenY.usd
        )
    
    @property
    def fees_sol(self):
        return (
            self.unrealizedPnl.unclaimedFeeTokenX.sol
            + self.unrealizedPnl.unclaimedFeeTokenY.sol
        )
    
class ActivePositionsTotal:

    def __init__(self, p):
        self.totalPositions = int(p.get("totalPositions", 0))
        self.balances = float(p.get("balances", 0))
        self.balancesSol = float(p.get("balancesSol", 0))
        self.unclaimedFees = float(p.get("unclaimedFees", 0))
        self.unclaimedFeesSol = float(p.get("unclaimedFeesSol", 0))
        self.pnl = float(p.get("pnl", 0))
        self.pnlSol = float(p.get("pnlSol", 0))
        self.pnlPctChange = float(p.get("pnlPctChange", 0))
        self.pnlSolPctChange = float(p.get("pnlPctChange", 0))

class ActivePositionsPools:

    def __init__(self, p):
        self.poolAddress = str(p.get("poolAddress", ""))
        self.binStep = int(p.get("binStep", 0))
        self.baseFee = float(p.get("baseFee", 0))
        self.collectFeeMode = float(p.get("collectFeeMode", 0))
        self.tokenXMint = str(p.get("tokenXMint", ""))
        self.tokenYMint = str(p.get("tokenYMint", ""))
        self.tokenXIcon = str(p.get("tokenXIcon", ""))
        self.tokenYIcon = str(p.get("tokenYIcon", ""))
        self.tokenX = str(p.get("tokenX", ""))
        self.tokenY = str(p.get("tokenY", ""))
        self.rewardX = float(p.get("rewardX") or 0)
        self.rewardY = float(p.get("rewardY") or 0)
        self.balances = float(p.get("balances", 0))
        self.balancesSol = float(p.get("balancesSol", 0))
        self.unclaimedFees = float(p.get("unclaimedFees", 0))
        self.unclaimedFeesSol = float(p.get("unclaimedFeesSol", 0))
        self.feePerTvl24h = float(p.get("feePerTvl24h", 0))
        self.pnl = float(p.get("pnl", 0))
        self.pnlSol = float(p.get("pnlSol", 0))
        self.pnlPctChange = float(p.get("pnlPctChange", 0))
        self.pnlSolPctChange = float(p.get("pnlSolPctChange", 0))
        self.totalDeposit = float(p.get("totalDeposit", 0))
        self.totalDepositSol = float(p.get("totalDepositSol", 0))
        self.openPositionCount = int(p.get("openPositionCount", 0))
        self.listPositions = list(p.get("listPositions", []))
        self.outOfRange = bool(p.get("outOfRange", False))
        self.positionsOutOfRange = list(p.get("positionsOutOfRange", []))
        self.poolPrice = float(p.get("poolPrice", 0))
        self.poolStateUpdatedAtSlot = int(p.get("poolStateUpdatedAtSlot", 0))
        self.poolStateUpdatedAtBlockTime = int(p.get("poolStateUpdatedAtBlockTime", 0))
    
class MeteoraPool:

    def __init__(self, data):
        self.address = data["address"]
        self.name = data["name"]
        self.token_x = TokenInfo(data.get("token_x", {}))
        self.token_y = TokenInfo(data.get("token_y", {}))
        self.reserve_x = data["reserve_x"]
        self.reserve_y = data["reserve_y"]
        self.token_x_amount = data["token_x_amount"]
        self.token_y_amount = data["token_y_amount"]
        self.created_at = data["created_at"]
        self.reward_mint_x = data["reward_mint_x"]
        self.reward_mint_y = data["reward_mint_y"]
        self.pool_config = PoolConfig(data.get("pool_config", {}))
        self.dynamic_fee_pct = float(data["dynamic_fee_pct"])
        self.tvl = float(data["tvl"])
        self.current_price = float(data["current_price"])
        self.apr =  float(data["apr"])
        self.apy = float(data["apy"])
        self.has_farm = bool(data["has_farm"])
        self.farm_apr = float(data["farm_apr"])
        self.farm_apy = float(data["farm_apy"])
        self.volume = PoolMetrics(data.get("volume", {}))
        self.fees = PoolMetrics(data.get("fees", {}))
        self.protocol_fees = PoolMetrics(data.get("protocol_fees", {}))
        self.fee_tvl_ratio = PoolMetrics(data.get("fee_tvl_ratio", {}))
        self.cumulative_metrics = CumulativeMetrics(data.get("cumulative_metrics", {}))
        self.is_blacklisted = bool(data["is_blacklisted"])
        self.launchpad = data["launchpad"]
        self.tags = list(data["tags"])

    def __repr__(self):
        farm = "FARM" if self.has_farm else "NO_FARM"
        status = "BLACKLISTED" if self.is_blacklisted else "OK"

        return (
            f"MeteoraPool("
            f"name={self.name}, "
            f"status={status}, "            
            f"tvl=${self.tvl:,.2f}, "
            f"price={self.current_price:.6f}, "
            f"apr={self.apr:.2%}, "
            f"apy={self.apy:.2%}, "
            f"fee24h=${self.fees.h24:.2f}, "
            f"vol24h=${self.volume.h24:.2f}, "
            f"dyn_fee={self.dynamic_fee_pct:.2f}%, "
            f"farm={farm})"
            "\n"
    )

class MeteoraPools:

    def __init__(self, data):
        self.total = int(data.get("total", 0))
        self.pages = int(data.get("pages", 0))
        self.current_page = int(data.get("current_page", 0))
        self.page_size = int(data.get("page_size", 0))

        self.data = [MeteoraPool(pool) for pool in data.get("data", [])]

    def __repr__(self):
        return(
            f"total pools: {self.total}, page {self.current_page} of {self.pages} (page size: {self.page_size})\n"
            f"{self.data}"
        )

class ActivePositions:

    def __init__(self, data):
        self.page = int(data["page"])
        self.pageSize = int(data["pageSize"])
        self.hasNext = bool(data["hasNext"])
        self.totalCount = int(data["totalCount"])
        self.totalPositions = int(data["totalPositions"])
        self.total = ActivePositionsTotal(data.get("total", {}))

        self.solPrice = float(data["solPrice"])
        self.pools = [ActivePositionsPools(i) for i in data.get("pools", [])]

    def __repr__(self):
        return (
            f"Total positions: {round(self.totalPositions, 2)}\n"
            f"Balance: {round(self.total.balances, 2)}\n"
            f"Balance SOL: {round(self.total.balancesSol, 2)}\n"
            f"Unclaimed fees: {round(self.total.unclaimedFees, 2)}\n"
            f"Unclaimed fees SOL: {round(self.total.unclaimedFeesSol, 2)}\n"
        )


class MeteoraPoolData:

    def __init__(self, data):
        # Общая информация
        self.tokenX = data["tokenX"]
        self.tokenY = data["tokenY"]
        self.totalCount = int(data["totalCount"])

        self.tokenXPrice = float(data["tokenXPrice"])
        self.tokenYPrice = float(data["tokenYPrice"])
        self.rewardTokenX = data["rewardTokenX"]
        self.rewardTokenY = data["rewardTokenY"]
        self.rewardTokenXPrice = data["rewardTokenXPrice"]
        self.rewardTokenYPrice = data["rewardTokenYPrice"]
        self.solPrice = float(data["solPrice"])

        self.positions = [MeteoraPosition(p) for p in data["positions"]]

class MeteoraClient:
    """Client for Meteora DLMM API."""
    def __init__(self, wallet: str):
        self.wallet = wallet
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        
        url = f"{BASE_URL}/{endpoint}"       
        response = self.session.get(url, timeout=10, params=params)      
        response.raise_for_status()

        return response.json()

    def get_positions(self, pool: str)-> MeteoraPoolData:
        """
            Returns all DLMM positions for the current wallet in the specified pool.

            Parameters
            ----------
            pool : str
                Pool address.

            Returns
            -------
            MeteoraPoolData
        """        
        return MeteoraPoolData(self._get(f"positions/{pool}/pnl?user={self.wallet}"))
    
    def get_pool(self, pool: str)-> MeteoraPool:
        
        return MeteoraPool((self._get(f"pools/{pool}")))
    
    def get_pools(self,
                  page: int = 1,
                  page_size: int = 10,
                  query: str | None = None,
                  sort_by: str | None = None,
                  filter_by: str | None = None):
        
        params = {
            "page": page,
            "page_size": page_size,
        }

        if query:
            params["query"] = query
        if sort_by:
            params["sort_by"] = sort_by
        if filter_by:
            params["filter_by"] = filter_by
                             
        return MeteoraPools(self._get("pools", params=params))
    
    def get_active_pools(self,
                         page: int = 1,
                         page_size: int = 10,
                         sort_direction: SortDirection | str | None = None,
                         sort_by: ActivePoolSort | str | None = None
                         )-> ActivePositions:
        
        if isinstance(sort_direction, str):
            sort_direction = SortDirection(sort_direction)

        if isinstance(sort_by, str):
            sort_by = ActivePoolSort(sort_by)

        params = {
            "page": page,
            "page_size": page_size,
        }
        if sort_direction:
            params["sort_direction"] = sort_direction.value
        if sort_by:
            params["sort_by"] = sort_by.value

        return ActivePositions(self._get(f"portfolio/open?user={self.wallet}", params=params))
        
        

#  Необходимо сделать:
#  ☑ client.get_pools(page=1)
#  ☑  client.search_pools("SOL")
#  ☑ client.get_top_pools(sort="tvl")
#  ▢ client.get_top_pools(sort="apr")
#  ☑ client.get_wallet_positions()      # все позиции кошелька
#  ▢ client.get_pool_history()          # если API поддерживает
#  ▢ client.get_bin_array()
#  ▢ client.get_transactions()

   
    def get_top_pools(self,
                    query: str | None = None,
                    sort_by="tvl:desc",
                    page: int = 1,
                    page_size: int = 10                    
                    ):
        
        return self.get_pools(page=page, page_size=page_size, query=query, sort_by=sort_by)



        
        
        