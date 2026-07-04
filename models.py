import requests

class TokenValue:

    def __init__(self, p):
        self.amount = float(p.get("amount", 0))
        self.usd = float(p.get("usd", 0))
        self.sol = float(p.get("amountSol", 0))

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
    
class MeteoraPool:

    def __init__(self, data):
        

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
        url = f"https://dlmm.datapi.meteora.ag/positions/{pool}/pnl?user={self.wallet}"
        pool_data = self.session.get(url, timeout=10)
        pool_data.raise_for_status()
        return MeteoraPoolData(pool_data.json())
    
    def get_pool(self, pool: str):
        pass

    
        