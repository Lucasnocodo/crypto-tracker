# cryptoapis_top10.py
# 依據 Crypto APIs v2:
# - /market-data/assets/by-symbol/{assetSymbol}
# - /market-data/exchange-rates/by-symbol/{fromAssetSymbol}/{toAssetSymbol}
# 認證：HTTP Header 'X-API-Key'
# Base URL: https://rest.cryptoapis.io

import asyncio
import aiohttp
from typing import Any, Dict, List, Optional

BASE = "https://rest.cryptoapis.io"
DEFAULT_TOP10 = ["BTC","ETH","USDT","BNB","SOL","XRP","USDC","DOGE","TON","ADA"]

class CryptoAPIsClient:
    def __init__(self, api_key: str, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key
        self._external_session = session

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    async def _request_json(self, method: str, url: str) -> Dict[str, Any]:
        # 使用傳入的 session（測試時可重用）或自建
        _own = False
        sess = self._external_session
        if sess is None:
            sess = aiohttp.ClientSession()
            _own = True
        try:
            async with sess.request(method, url, headers=self._headers(), timeout=aiohttp.ClientTimeout(total=20)) as resp:
                text = await resp.text()
                if resp.status // 100 != 2:
                    raise RuntimeError(f"HTTP {resp.status}: {text[:300]}")
                try:
                    return await resp.json()
                except Exception:
                    # 有些錯誤頁可能非 JSON
                    raise RuntimeError(f"Bad JSON response: {text[:300]}")
        finally:
            if _own:
                await sess.close()

    async def get_asset_details_by_symbol(self, symbol: str) -> Dict[str, Any]:
        url = f"{BASE}/market-data/assets/by-symbol/{symbol}"
        return await self._request_json("GET", url)

    async def get_exchange_rate_by_symbols(self, frm: str, to: str = "USD") -> Dict[str, Any]:
        url = f"{BASE}/market-data/exchange-rates/by-symbol/{frm}/{to}"
        return await self._request_json("GET", url)

async def fetch_top_assets(
    api_key: str,
    symbols: Optional[List[str]] = None,
    to_fiat: str = "USD",
    concurrency: int = 5,
    use_exchange_rate_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    回傳每個幣的彙整資料：
      {
        symbol, name, latestPriceUSD, latestPriceAt, change1h, change24h, change7d,
        logoBase64, unit, referenceId
      }
    其中 latestPriceUSD 若 asset 詳情未給 USD，會用 exchange-rate 端點補上。
    """
    symbols = symbols or DEFAULT_TOP10
    sem = asyncio.Semaphore(concurrency)
    client = CryptoAPIsClient(api_key)

    async def _one(sym: str) -> Dict[str, Any]:
        async with sem:
            try:
                if use_exchange_rate_only:
                    rate = await client.get_exchange_rate_by_symbols(sym, to_fiat)
                    item = rate.get("data", {}).get("item", {})
                    return {
                        "symbol": item.get("fromAssetSymbol") or sym,
                        "name": None,
                        "latestPriceUSD": float(item["rate"]) if item.get("toAssetSymbol") == "USD" and item.get("rate") is not None else None,
                        "latestPriceAt": item.get("calculationTimestamp"),
                        "change1h": None,
                        "change24h": None,
                        "change7d": None,
                        "logoBase64": None,
                        "unit": item.get("toAssetSymbol"),
                        "referenceId": item.get("fromAssetId"),
                    }

                # 先拿資產詳情（通常含最新價與波動）
                details = await client.get_asset_details_by_symbol(sym)
                d = details.get("data", {}).get("item", {}) or {}
                latest = d.get("latestRate", {}) or {}
                # 不同文件版本對「變動」欄位命名可能略異，容錯取法
                changes = d.get("rateChange") or d.get("rateChanges") or {}

                result = {
                    "symbol": d.get("originalSymbol") or d.get("symbol") or sym,
                    "name": d.get("name"),
                    "latestPriceUSD": float(latest["amount"]) if latest.get("unit") == "USD" and latest.get("amount") is not None else None,
                    "latestPriceAt": latest.get("calculationTimestamp"),
                    "change1h": _to_float(changes.get("hour") or changes.get("lastHour") or changes.get("1h")),
                    "change24h": _to_float(changes.get("day") or changes.get("lastDay") or changes.get("24h")),
                    "change7d": _to_float(changes.get("week") or changes.get("lastWeek") or changes.get("7d")),
                    "logoBase64": (d.get("logo") or {}).get("imageData"),
                    "unit": latest.get("unit"),
                    "referenceId": d.get("referenceId"),
                }

                # 若沒拿到 USD 價，補打一個匯率端點
                if result["latestPriceUSD"] is None and to_fiat == "USD":
                    rate = await client.get_exchange_rate_by_symbols(sym, to_fiat)
                    item = rate.get("data", {}).get("item", {}) or {}
                    if item.get("toAssetSymbol") == "USD" and item.get("rate") is not None:
                        result["latestPriceUSD"] = float(item["rate"])
                        result["latestPriceAt"] = result["latestPriceAt"] or item.get("calculationTimestamp")
                        result["unit"] = "USD"

                return result
            except Exception as e:
                # 確保單一幣失敗不會中斷整體
                return {"symbol": sym, "error": str(e)}

    tasks = [_one(s) for s in symbols]
    out = await asyncio.gather(*tasks)
    # 有價的排前面
    out.sort(key=lambda x: (x.get("latestPriceUSD") is None, -(x.get("latestPriceUSD") or 0)))
    return out

def _to_float(v):
    try:
        return None if v is None else float(v)
    except Exception:
        return None

# --- 範例執行 ---
# 若你把此檔另存為 cryptoapis_top10.py，直接用：
#   export CRYPTOAPIS_KEY="你的API金鑰"
#   python3 -m cryptoapis_top10
if __name__ == "__main__":
    import os, json
    key = os.getenv("CRYPTO_API_KEY")
    if not key:
        raise RuntimeError("請先 export CRYPTO_API_KEY=你的API金鑰")
    data = asyncio.run(fetch_top_assets(key))
    print(json.dumps(data, ensure_ascii=False, indent=2))
