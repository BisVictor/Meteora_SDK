import requests
user = "6NYPquPNfZALPDCVLTjADvzVsarRriGi1HS26ydo6s2C"
pool = "AcQPrTHx3ggWau1yU1fe5mQ89HeqPTsEoWC7ejL67wfd"
url = f"https://dlmm.datapi.meteora.ag/positions/{pool}/pnl?user={user}"
request = requests.get(url)
data = request.json()
tokenX = data["tokenX"]
tokenY = data["tokenY"]
p = data["positions"]
p = p[0]
positionAddress = p.get("positionAddress", "")

minPrice = p.get("minPrice", 0)
maxPrice = p.get("maxPrice", 0)
lowerBinId = p.get("lowerBinId", 0)
upperBinId = p.get("upperBinId", 0)
poolActiveBinId = p.get("poolActiveBinId", 0)
isOutOfRange= p.get("isOutOfRange", False)
poolActivePrice = p.get("poolActivePrice", 0)
feePerTvl24h= p.get("feePerTvl24h", 0)
isClosed= p.get("isClosed", False)
createdAt= p.get("createdAt", 0)
closedAt= p.get("closedAt", None)
pnlUsd= p.get("pnlUsd", 0)
pnlSol= p.get("pnlSol", 0)
pnlPctChange= p.get("pnlPctChange", 0)
pnlSolPctChange= p.get("pnlSolPctChange", 0)

#allTimeDeposits
allTimeDeposits= p.get("allTimeDeposits", {})
aTD_tokenX = allTimeDeposits.get("tokenX", {})
aTD_tokenX_amount = aTD_tokenX.get("amount", 0)
aTD_tokenX_usd = aTD_tokenX.get("usd", 0)
aTD_tokenX_amountSol = aTD_tokenX.get("amountSol", 0)

aTD_tokenY = allTimeDeposits.get("tokenY", {})
aTD_tokenY_amount = aTD_tokenY.get("amount", 0)
aTD_tokenY_usd = aTD_tokenY.get("usd", 0)
aTD_tokenY_amountSol = aTD_tokenY.get("amount", 0)

aTD_total = allTimeDeposits.get("total", {})
aTD_total_usd = aTD_total.get("usd", 0)
aTD_total_sol = aTD_total.get("sol", 0)

#allTimeWithdrawals
allTimeWithdrawals = p.get("allTimeWithdrawals", {})
aTW_tokenX = allTimeWithdrawals.get("tokenX", {})
aTW_tokenX_amount = aTW_tokenX.get("amount", 0)
aTW_tokenX_usd = aTW_tokenX.get("usd", 0)
aTW_tokenX_amountSol = aTW_tokenX.get("amountSol", 0)

aTW_tokenY = allTimeWithdrawals.get("tokenY", {})
aTW_tokenY_amount = aTW_tokenY.get("amount", 0)
aTW_tokenY_usd = aTW_tokenY.get("usd", 0)
aTW_tokenY_amountSol = aTW_tokenY.get("amountSol", 0)

aTW_total = allTimeWithdrawals.get("total", {})
aTW_total_usd = aTW_total.get("usd", 0)
aTW_total_sol = aTW_total.get("sol", 0)

#allTimeFees
allTimeFees = p.get("allTimeFees", {})
aTF_tokenX = allTimeFees.get("tokenX", {})
aTF_tokenX_amount = aTF_tokenX.get("amount", 0)
aTF_tokenX_usd = aTF_tokenX.get("usd", 0)
aTF_tokenX_amountSol = aTF_tokenX.get("amountSol", 0)

aTF_tokenY = allTimeFees.get("tokenY", {})
aTF_tokenY_amount = aTF_tokenY.get("amount", 0)
aTF_tokenY_usd = aTF_tokenY.get("usd", 0)
aTF_tokenY_amountSol = aTF_tokenY.get("amountSol", 0)

print(aTF_tokenY_usd)