from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import json
import subprocess
import sys

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
import logging
from contextlib import asynccontextmanager

# Import our custom crypto price service
try:
    from getCryptoPrice import fetch_top_assets
    CRYPTO_PRICE_SERVICE_AVAILABLE = True
except ImportError:
    print("Warning: getCryptoPrice.py service not available")
    CRYPTO_PRICE_SERVICE_AVAILABLE = False

load_dotenv()

app = FastAPI(title="Crypto Tracker API", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class CryptoPrice(BaseModel):
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime
    high_24h: float
    low_24h: float

class TechnicalIndicators(BaseModel):
    symbol: str
    rsi: float
    macd: Dict[str, float]
    moving_averages: Dict[str, float]
    bollinger_bands: Dict[str, float]
    support_resistance: Dict[str, float]

class InvestmentRecommendation(BaseModel):
    symbol: str
    recommendation: str  # "BUY", "SELL", "HOLD"
    confidence: float
    timeframe: str  # "short", "medium", "long"
    reasoning: str
    target_price: float
    stop_loss: float
    risk_level: str

class MarketOverview(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    bitcoin_dominance: float
    fear_greed_index: float
    trending_coins: List[str]
    market_sentiment: str

class CryptoNews(BaseModel):
    title: str
    description: str
    url: str
    image_url: Optional[str]
    source: str
    published_at: datetime
    sentiment: Optional[str] = None

# Global cache for API rate limiting
price_cache = {}
cache_expiry = {}

# News cache for crypto news
news_cache = {}
news_cache_expiry = {}

# CRITICAL: 30-second cache for expensive CryptoAPIs service to avoid high costs
crypto_apis_cache = {}
crypto_apis_cache_expiry = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.last_broadcast_data = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logging.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, data: dict):
        # Only broadcast if data has changed significantly
        if self._has_significant_change(data):
            self.last_broadcast_data = data
            message = json.dumps(data, cls=DateTimeEncoder)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected websockets
            for conn in disconnected:
                self.disconnect(conn)

    def _has_significant_change(self, new_data: dict) -> bool:
        """Check if there's a significant change in data to warrant broadcasting"""
        if not self.last_broadcast_data:
            return True
            
        # Check for price changes
        if 'data' in new_data and 'prices' in new_data['data']:
            new_prices = new_data['data']['prices']
            old_prices = self.last_broadcast_data.get('data', {}).get('prices', [])
            
            if len(new_prices) != len(old_prices):
                return True
                
            for new_price, old_price in zip(new_prices, old_prices):
                if new_price.get('symbol') != old_price.get('symbol'):
                    continue
                    
                # Broadcast if price changed by more than 0.05% for major coins
                # or 0.1% for smaller coins
                old_price_val = old_price.get('price', 0)
                new_price_val = new_price.get('price', 0)
                
                if old_price_val > 0:
                    price_change_percent = abs(new_price_val - old_price_val) / old_price_val * 100
                    threshold = 0.05 if new_price.get('symbol') in ['BTC', 'ETH', 'BNB'] else 0.1
                    
                    if price_change_percent > threshold:
                        logging.info(f"Significant price change detected for {new_price.get('symbol')}: {price_change_percent:.2f}%")
                        return True
                
                # Also check for 24h change differences
                old_change = old_price.get('change_24h', 0)
                new_change = new_price.get('change_24h', 0)
                if abs(new_change - old_change) > 0.5:  # 0.5% change in daily percentage
                    return True
        
        # Always broadcast if it's been more than 30 seconds since last broadcast
        last_update = self.last_broadcast_data.get('timestamp')
        if last_update:
            try:
                last_time = datetime.fromisoformat(last_update.replace('Z', '+00:00').replace('+00:00', ''))
                time_diff = (datetime.now() - last_time).total_seconds()
                if time_diff > 30:
                    return True
            except:
                return True  # If timestamp parsing fails, broadcast anyway
                
        return False

manager = ConnectionManager()

# CoinGecko API configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum", 
    "BNB": "binancecoin",
    "SOL": "solana",
    "ADA": "cardano",
    "XRP": "ripple",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "ATOM": "cosmos",
    "ETC": "ethereum-classic",
    "USDC": "usd-coin",
    "USDT": "tether",
    "DAI": "dai"
}

async def get_real_crypto_prices() -> List[Dict[str, Any]]:
    """Get real-time crypto prices using HIGH-QUALITY MOCK DATA (APIs disabled for development)"""
    global crypto_apis_cache, crypto_apis_cache_expiry
    
    try:
        # CRITICAL: Check 30-second cache first to prevent excessive processing
        if crypto_apis_cache_expiry and datetime.now() < crypto_apis_cache_expiry:
            print(f"Using cached Mock data (expires in {(crypto_apis_cache_expiry - datetime.now()).seconds} seconds)")
            return crypto_apis_cache
            
        print("🎭 USING HIGH-QUALITY MOCK DATA - No API costs, perfect for development!")
        
        # High-quality mock data with realistic prices and variations
        import random
        import base64
        
        # Base prices and realistic market data
        mock_crypto_data = {
            "BTC": {
                "name": "Bitcoin",
                "price": 43250.75 + random.uniform(-500, 500),
                "change_1h": round(random.uniform(-1.5, 1.5), 2),
                "change_24h": round(random.uniform(-5.0, 5.0), 2),
                "change_7d": round(random.uniform(-10.0, 10.0), 2),
                "volume_24h": 25000000000 + random.uniform(-2000000000, 2000000000),
                "market_cap": 847000000000 + random.uniform(-50000000000, 50000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/bitcoin.png"
            },
            "ETH": {
                "name": "Ethereum", 
                "price": 2650.85 + random.uniform(-100, 100),
                "change_1h": round(random.uniform(-1.2, 1.2), 2),
                "change_24h": round(random.uniform(-4.5, 4.5), 2),
                "change_7d": round(random.uniform(-8.0, 8.0), 2),
                "volume_24h": 12000000000 + random.uniform(-1000000000, 1000000000),
                "market_cap": 318000000000 + random.uniform(-20000000000, 20000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/ethereum.png"
            },
            "BNB": {
                "name": "Binance Coin",
                "price": 315.25 + random.uniform(-15, 15),
                "change_1h": round(random.uniform(-0.8, 0.8), 2),
                "change_24h": round(random.uniform(-3.5, 3.5), 2),
                "change_7d": round(random.uniform(-6.0, 6.0), 2),
                "volume_24h": 800000000 + random.uniform(-100000000, 100000000),
                "market_cap": 47000000000 + random.uniform(-3000000000, 3000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/binancecoin.png"
            },
            "SOL": {
                "name": "Solana",
                "price": 98.45 + random.uniform(-8, 8),
                "change_1h": round(random.uniform(-1.8, 1.8), 2),
                "change_24h": round(random.uniform(-6.0, 6.0), 2),
                "change_7d": round(random.uniform(-12.0, 12.0), 2),
                "volume_24h": 2500000000 + random.uniform(-300000000, 300000000),
                "market_cap": 42000000000 + random.uniform(-4000000000, 4000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/solana.png"
            },
            "XRP": {
                "name": "XRP",
                "price": 0.6125 + random.uniform(-0.05, 0.05),
                "change_1h": round(random.uniform(-1.0, 1.0), 2),
                "change_24h": round(random.uniform(-4.0, 4.0), 2),
                "change_7d": round(random.uniform(-8.0, 8.0), 2),
                "volume_24h": 1800000000 + random.uniform(-200000000, 200000000),
                "market_cap": 33000000000 + random.uniform(-3000000000, 3000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/ripple.png"
            },
            "ADA": {
                "name": "Cardano",
                "price": 0.485 + random.uniform(-0.03, 0.03),
                "change_1h": round(random.uniform(-1.2, 1.2), 2),
                "change_24h": round(random.uniform(-5.0, 5.0), 2),
                "change_7d": round(random.uniform(-9.0, 9.0), 2),
                "volume_24h": 650000000 + random.uniform(-80000000, 80000000),
                "market_cap": 17000000000 + random.uniform(-2000000000, 2000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/cardano.png"
            },
            "AVAX": {
                "name": "Avalanche",
                "price": 37.82 + random.uniform(-3, 3),
                "change_1h": round(random.uniform(-1.5, 1.5), 2),
                "change_24h": round(random.uniform(-5.5, 5.5), 2),
                "change_7d": round(random.uniform(-10.0, 10.0), 2),
                "volume_24h": 500000000 + random.uniform(-50000000, 50000000),
                "market_cap": 14000000000 + random.uniform(-1500000000, 1500000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/avalanche.png"
            },
            "DOT": {
                "name": "Polkadot",
                "price": 7.25 + random.uniform(-0.5, 0.5),
                "change_1h": round(random.uniform(-1.0, 1.0), 2),
                "change_24h": round(random.uniform(-4.5, 4.5), 2),
                "change_7d": round(random.uniform(-8.5, 8.5), 2),
                "volume_24h": 350000000 + random.uniform(-40000000, 40000000),
                "market_cap": 9500000000 + random.uniform(-800000000, 800000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/polkadot.png"
            },
            "MATIC": {
                "name": "Polygon",
                "price": 0.825 + random.uniform(-0.08, 0.08),
                "change_1h": round(random.uniform(-1.3, 1.3), 2),
                "change_24h": round(random.uniform(-6.0, 6.0), 2),
                "change_7d": round(random.uniform(-11.0, 11.0), 2),
                "volume_24h": 420000000 + random.uniform(-50000000, 50000000),
                "market_cap": 7800000000 + random.uniform(-700000000, 700000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/matic.png"
            },
            "LINK": {
                "name": "Chainlink",
                "price": 14.65 + random.uniform(-1.2, 1.2),
                "change_1h": round(random.uniform(-0.9, 0.9), 2),
                "change_24h": round(random.uniform(-4.0, 4.0), 2),
                "change_7d": round(random.uniform(-7.5, 7.5), 2),
                "volume_24h": 280000000 + random.uniform(-30000000, 30000000),
                "market_cap": 8600000000 + random.uniform(-600000000, 600000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/chainlink.png"
            },
            "UNI": {
                "name": "Uniswap",
                "price": 6.85 + random.uniform(-0.6, 0.6),
                "change_1h": round(random.uniform(-1.4, 1.4), 2),
                "change_24h": round(random.uniform(-5.5, 5.5), 2),
                "change_7d": round(random.uniform(-9.5, 9.5), 2),
                "volume_24h": 180000000 + random.uniform(-25000000, 25000000),
                "market_cap": 5200000000 + random.uniform(-400000000, 400000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/uniswap.png"
            },
            "LTC": {
                "name": "Litecoin",
                "price": 73.15 + random.uniform(-5, 5),
                "change_1h": round(random.uniform(-0.8, 0.8), 2),
                "change_24h": round(random.uniform(-3.5, 3.5), 2),
                "change_7d": round(random.uniform(-6.5, 6.5), 2),
                "volume_24h": 450000000 + random.uniform(-50000000, 50000000),
                "market_cap": 5400000000 + random.uniform(-400000000, 400000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/litecoin.png"
            },
            "BCH": {
                "name": "Bitcoin Cash",
                "price": 245.80 + random.uniform(-15, 15),
                "change_1h": round(random.uniform(-1.1, 1.1), 2),
                "change_24h": round(random.uniform(-4.8, 4.8), 2),
                "change_7d": round(random.uniform(-8.8, 8.8), 2),
                "volume_24h": 320000000 + random.uniform(-40000000, 40000000),
                "market_cap": 4800000000 + random.uniform(-300000000, 300000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/bitcoin-cash.png"
            },
            "ATOM": {
                "name": "Cosmos",
                "price": 9.85 + random.uniform(-0.8, 0.8),
                "change_1h": round(random.uniform(-1.6, 1.6), 2),
                "change_24h": round(random.uniform(-5.8, 5.8), 2),
                "change_7d": round(random.uniform(-10.5, 10.5), 2),
                "volume_24h": 95000000 + random.uniform(-15000000, 15000000),
                "market_cap": 3800000000 + random.uniform(-300000000, 300000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/cosmos.png"
            },
            "ETC": {
                "name": "Ethereum Classic",
                "price": 20.45 + random.uniform(-1.5, 1.5),
                "change_1h": round(random.uniform(-1.2, 1.2), 2),
                "change_24h": round(random.uniform(-4.2, 4.2), 2),
                "change_7d": round(random.uniform(-7.8, 7.8), 2),
                "volume_24h": 85000000 + random.uniform(-12000000, 12000000),
                "market_cap": 3000000000 + random.uniform(-250000000, 250000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/ethereum-classic.png"
            },
            "USDC": {
                "name": "USD Coin",
                "price": 1.0002 + random.uniform(-0.0005, 0.0005),
                "change_1h": round(random.uniform(-0.02, 0.02), 4),
                "change_24h": round(random.uniform(-0.05, 0.05), 4),
                "change_7d": round(random.uniform(-0.08, 0.08), 4),
                "volume_24h": 4200000000 + random.uniform(-200000000, 200000000),
                "market_cap": 24500000000 + random.uniform(-500000000, 500000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/usd-coin.png"
            },
            "USDT": {
                "name": "Tether",
                "price": 0.9998 + random.uniform(-0.0008, 0.0008),
                "change_1h": round(random.uniform(-0.03, 0.03), 4),
                "change_24h": round(random.uniform(-0.06, 0.06), 4),
                "change_7d": round(random.uniform(-0.1, 0.1), 4),
                "volume_24h": 28000000000 + random.uniform(-2000000000, 2000000000),
                "market_cap": 91000000000 + random.uniform(-2000000000, 2000000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/tether.png"
            },
            "DAI": {
                "name": "Dai",
                "price": 1.0001 + random.uniform(-0.0006, 0.0006),
                "change_1h": round(random.uniform(-0.02, 0.02), 4),
                "change_24h": round(random.uniform(-0.04, 0.04), 4),
                "change_7d": round(random.uniform(-0.07, 0.07), 4),
                "volume_24h": 180000000 + random.uniform(-20000000, 20000000),
                "market_cap": 5300000000 + random.uniform(-200000000, 200000000),
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/dai.png"
            }
        }
        
        # Create simple placeholder logos (small base64 encoded SVG icons)
        def create_simple_logo(symbol: str) -> str:
            """Create a simple SVG logo encoded as base64"""
            svg_content = f'''<svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
                <circle cx="16" cy="16" r="15" fill="#{'f7931a' if symbol == 'BTC' else '627eea' if symbol == 'ETH' else 'f3ba2f' if symbol == 'BNB' else '9945ff' if symbol == 'SOL' else '23292f'}"/>
                <text x="16" y="20" text-anchor="middle" fill="white" font-size="10" font-family="Arial">{symbol[:3]}</text>
            </svg>'''
            return base64.b64encode(svg_content.encode()).decode()
        
        # Transform to our expected format with all required fields
        result = []
        current_time = datetime.now()
        
        for symbol, data in mock_crypto_data.items():
            price = round(data["price"], 4)
            
            price_data = {
                # Core price information (backward compatible)
                "symbol": symbol,
                "price": price,
                "change_24h": data["change_24h"],
                "volume_24h": round(data["volume_24h"]),
                "market_cap": round(data["market_cap"]),
                "high_24h": round(price * (1 + abs(data["change_24h"])/100 + random.uniform(0.005, 0.02)), 4),
                "low_24h": round(price * (1 - abs(data["change_24h"])/100 - random.uniform(0.005, 0.02)), 4),
                "timestamp": current_time.isoformat(),
                
                # Additional enhanced fields
                "name": data["name"],
                "change_1h": data["change_1h"],
                "change_7d": data["change_7d"],
                "logo": create_simple_logo(symbol),  # Base64 encoded simple SVG
                "logo_url": data["logo_url"],  # External URL for better quality
                "unit": "USD",
                "reference_id": f"mock-{symbol.lower()}-{int(current_time.timestamp())}",
                
                # Data source indicator
                "data_source": "Mock"
            }
            result.append(price_data)
        
        # CRITICAL: Cache the result for exactly 30 seconds to simulate real API behavior
        crypto_apis_cache = result
        crypto_apis_cache_expiry = datetime.now() + timedelta(seconds=30)
        print(f"✅ Mock data cached for 30 seconds (until {crypto_apis_cache_expiry.strftime('%H:%M:%S')})")
        print(f"📊 Generated {len(result)} high-quality mock crypto prices")
        
        return result
        
    except Exception as e:
        print(f"Error generating mock crypto prices: {str(e)}")
        # Fallback to minimal mock data if even the mock generation fails
        fallback_data = [
            {
                "symbol": "BTC",
                "price": 43500.0,
                "change_24h": 2.5,
                "volume_24h": 25000000000,
                "market_cap": 850000000000,
                "high_24h": 44000.0,
                "low_24h": 42500.0,
                "timestamp": datetime.now().isoformat(),
                "name": "Bitcoin",
                "change_1h": 0.8,
                "change_7d": 5.2,
                "logo": "",
                "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/bitcoin.png",
                "unit": "USD",
                "reference_id": "mock-btc-fallback",
                "data_source": "Mock"
            }
        ]
        return fallback_data

async def get_real_time_price(symbol: str) -> Dict[str, Any]:
    """Get real-time price data from CoinGecko API with minimal caching for real-time updates"""
    try:
        # Reduce cache time to 10 seconds for more real-time data
        if symbol in price_cache and symbol in cache_expiry:
            if datetime.now() < cache_expiry[symbol]:
                return price_cache[symbol]
        
        # Special handling for stablecoins
        stablecoins = ["USDC", "USDT", "DAI"]
        if symbol.upper() in stablecoins:
            return {
                # Core price information (backward compatible)
                "symbol": symbol.upper(),
                "price": 1.0,
                "change_24h": 0.0,
                "volume_24h": 1000000000,  # High volume for stablecoins
                "market_cap": 10000000000,  # Large market cap for stablecoins
                "high_24h": 1.01,
                "low_24h": 0.99,
                "timestamp": datetime.now().isoformat(),
                
                # Additional fields for stablecoins
                "name": f"{symbol.upper()} Stablecoin",
                "change_1h": 0.0,
                "change_7d": 0.0,
                "logo": "",
                "unit": "USD",
                "reference_id": f"stablecoin-{symbol.lower()}",
                
                # Data source indicator
                "data_source": "Stablecoin"
            }
        
        coin_id = COINGECKO_COINS.get(symbol.upper())
        if not coin_id:
            raise ValueError(f"Unsupported cryptocurrency: {symbol}")
        
        # Get current price data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COINGECKO_BASE_URL}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true",
                    "include_market_cap": "true",
                    "include_last_updated_at": "true"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"CoinGecko API error: {response.status_code}")
            
            data = response.json()
            if coin_id not in data:
                raise ValueError(f"No data available for {symbol}")
            
            coin_data = data[coin_id]
            
            # Get historical data for high/low
            hist_response = await client.get(
                f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart",
                params={
                    "vs_currency": "usd",
                    "days": "1",
                    "interval": "hourly"
                },
                timeout=10.0
            )
            
            if hist_response.status_code == 200:
                hist_data = hist_response.json()
                prices = hist_data.get("prices", [])
                if prices:
                    high_24h = max(price[1] for price in prices)
                    low_24h = min(price[1] for price in prices)
                else:
                    high_24h = coin_data["usd"]
                    low_24h = coin_data["usd"]
            else:
                high_24h = coin_data["usd"]
                low_24h = coin_data["usd"]
            
            price_data = {
                # Core price information (backward compatible)
                "symbol": symbol.upper(),
                "price": round(coin_data["usd"], 4),
                "change_24h": round(coin_data.get("usd_24h_change", 0), 2),
                "volume_24h": round(coin_data.get("usd_24h_vol", 0), 2),
                "market_cap": round(coin_data.get("usd_market_cap", 0), 2),
                "high_24h": round(high_24h, 4),
                "low_24h": round(low_24h, 4),
                "timestamp": datetime.now().isoformat(),
                
                # Additional fields (CoinGecko doesn't provide these, so use defaults)
                "name": coin_id.replace('-', ' ').title(),  # Convert coin_id to name
                "change_1h": 0.0,  # CoinGecko doesn't provide 1h change in this endpoint
                "change_7d": 0.0,  # CoinGecko doesn't provide 7d change in this endpoint
                "logo": "",  # CoinGecko doesn't provide logo in this endpoint
                "unit": "USD",
                "reference_id": coin_id,
                
                # Data source indicator
                "data_source": "CoinGecko"
            }
            
            # Cache the data for 3 seconds for real-time updates (faster for WebSocket)
            price_cache[symbol.upper()] = price_data
            cache_expiry[symbol.upper()] = datetime.now() + timedelta(seconds=3)
            
            return price_data
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        # Fallback to mock data if API fails
        return {
            # Core price information (backward compatible)
            "symbol": symbol.upper(),
            "price": 50000.0,
            "change_24h": 2.5,
            "volume_24h": 1000000,
            "market_cap": 1000000000,
            "high_24h": 51000.0,
            "low_24h": 49000.0,
            "timestamp": datetime.now().isoformat(),
            
            # Additional fields (mock data)
            "name": f"{symbol.upper()} Token",
            "change_1h": 0.5,
            "change_7d": 5.0,
            "logo": "",
            "unit": "USD",
            "reference_id": f"mock-{symbol.lower()}",
            
            # Data source indicator
            "data_source": "Mock"
        }

async def calculate_technical_indicators(symbol: str) -> Dict[str, Any]:
    """Calculate technical indicators for a cryptocurrency using CoinGecko historical data"""
    try:
        coin_id = COINGECKO_COINS.get(symbol.upper())
        if not coin_id:
            raise ValueError(f"Unsupported cryptocurrency: {symbol}")
        
        # Get historical data for technical analysis (60 days)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart",
                params={
                    "vs_currency": "usd",
                    "days": "60"
                },
                timeout=15.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"CoinGecko API error: {response.status_code}")
            
            data = response.json()
            prices = data.get("prices", [])
            
            if len(prices) < 50:
                raise ValueError(f"Insufficient data for technical analysis of {symbol}")
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['price'] = df['price'].astype(float)
            
            # Calculate RSI
            rsi_indicator = RSIIndicator(df['price'])
            rsi = rsi_indicator.rsi().iloc[-1]
            
            # Calculate MACD
            macd_indicator = MACD(df['price'])
            macd_line = macd_indicator.macd().iloc[-1]
            macd_signal = macd_indicator.macd_signal().iloc[-1]
            macd_histogram = macd_indicator.macd_diff().iloc[-1]
            
            # Calculate Moving Averages
            sma_20 = SMAIndicator(df['price'], window=20).sma_indicator().iloc[-1]
            sma_50 = SMAIndicator(df['price'], window=50).sma_indicator().iloc[-1]
            ema_12 = EMAIndicator(df['price'], window=12).ema_indicator().iloc[-1]
            
            # Calculate Bollinger Bands
            bb_indicator = BollingerBands(df['price'])
            bb_upper = bb_indicator.bollinger_hband().iloc[-1]
            bb_middle = bb_indicator.bollinger_mavg().iloc[-1]
            bb_lower = bb_indicator.bollinger_lband().iloc[-1]
            
            # Calculate Support and Resistance levels
            recent_highs = df['price'].tail(20)
            recent_lows = df['price'].tail(20)
            resistance = recent_highs.max()
            support = recent_lows.min()
            
            return {
                "symbol": symbol.upper(),
                "rsi": round(rsi, 2) if not pd.isna(rsi) else 50.0,
                "macd": {
                    "macd": round(macd_line, 4) if not pd.isna(macd_line) else 0.0,
                    "signal": round(macd_signal, 4) if not pd.isna(macd_signal) else 0.0,
                    "histogram": round(macd_histogram, 4) if not pd.isna(macd_histogram) else 0.0
                },
                "moving_averages": {
                    "sma_20": round(sma_20, 4) if not pd.isna(sma_20) else 0.0,
                    "sma_50": round(sma_50, 4) if not pd.isna(sma_50) else 0.0,
                    "ema_12": round(ema_12, 4) if not pd.isna(ema_12) else 0.0
                },
                "bollinger_bands": {
                    "upper": round(bb_upper, 4) if not pd.isna(bb_upper) else 0.0,
                    "middle": round(bb_middle, 4) if not pd.isna(bb_middle) else 0.0,
                    "lower": round(bb_lower, 4) if not pd.isna(bb_lower) else 0.0
                },
                "support_resistance": {
                    "resistance": round(resistance, 4),
                    "support": round(support, 4)
                }
            }
        
    except Exception as e:
        print(f"Error calculating technical indicators for {symbol}: {str(e)}")
        # Fallback to mock data
        return {
            "symbol": symbol.upper(),
            "rsi": 45.5,
            "macd": {"macd": 100, "signal": 95, "histogram": 5},
            "moving_averages": {"sma_20": 49000, "sma_50": 48000, "ema_12": 50500},
            "bollinger_bands": {"upper": 52000, "middle": 50000, "lower": 48000},
            "support_resistance": {"resistance": 52000, "support": 48000}
        }

async def generate_investment_recommendation(symbol: str, timeframe: str = "medium") -> Dict[str, Any]:
    """Generate AI-powered investment recommendations based on technical analysis"""
    try:
        # Get technical indicators
        tech_data = await calculate_technical_indicators(symbol)
        
        # Get current price
        price_data = await get_real_time_price(symbol)
        current_price = price_data['price']
        
        # Simple recommendation logic based on technical indicators
        rsi = tech_data['rsi']
        macd_histogram = tech_data['macd']['histogram']
        price_vs_sma20 = current_price / tech_data['moving_averages']['sma_20']
        
        recommendation = "HOLD"
        confidence = 0.5
        reasoning = []
        
        # RSI analysis
        if rsi < 30:
            recommendation = "BUY"
            confidence += 0.2
            reasoning.append("RSI indicates oversold conditions")
        elif rsi > 70:
            recommendation = "SELL"
            confidence += 0.2
            reasoning.append("RSI indicates overbought conditions")
        
        # MACD analysis
        if macd_histogram > 0 and macd_histogram > tech_data['macd']['histogram']:
            if recommendation == "BUY":
                confidence += 0.1
            reasoning.append("MACD showing bullish momentum")
        elif macd_histogram < 0:
            if recommendation == "SELL":
                confidence += 0.1
            reasoning.append("MACD showing bearish momentum")
        
        # Moving average analysis
        if current_price > tech_data['moving_averages']['sma_20']:
            if recommendation == "BUY":
                confidence += 0.1
            reasoning.append("Price above 20-day moving average")
        else:
            if recommendation == "SELL":
                confidence += 0.1
            reasoning.append("Price below 20-day moving average")
        
        # Calculate target price and stop loss
        if recommendation == "BUY":
            target_price = current_price * 1.15  # 15% upside
            stop_loss = current_price * 0.92    # 8% downside
        elif recommendation == "SELL":
            target_price = current_price * 0.85  # 15% downside
            stop_loss = current_price * 1.08    # 8% upside
        else:
            target_price = current_price
            stop_loss = current_price * 0.95
        
        # Determine risk level
        risk_level = "LOW" if confidence < 0.6 else "MEDIUM" if confidence < 0.8 else "HIGH"
        
        return {
            "symbol": symbol.upper(),
            "recommendation": recommendation,
            "confidence": round(confidence, 2),
            "timeframe": timeframe,
            "reasoning": " | ".join(reasoning) if reasoning else f"Based on technical analysis for {timeframe}-term outlook",
            "target_price": round(target_price, 4),
            "stop_loss": round(stop_loss, 4),
            "risk_level": risk_level
        }
        
    except Exception as e:
        print(f"Error generating recommendation for {symbol}: {str(e)}")
        # Fallback recommendation
        return {
            "symbol": symbol.upper(),
            "recommendation": "HOLD",
            "confidence": 0.5,
            "timeframe": timeframe,
            "reasoning": f"Unable to generate recommendation due to data issues for {timeframe}-term outlook",
            "target_price": 0.0,
            "stop_loss": 0.0,
            "risk_level": "UNKNOWN"
        }

async def get_market_overview() -> Dict[str, Any]:
    """Get overall market overview with real-time data from CoinGecko"""
    try:
        # Get global market data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{COINGECKO_BASE_URL}/global",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                global_data = data.get("data", {})
                
                # Get top cryptocurrencies data
                top_coins = ["BTC", "ETH", "BNB", "SOL", "ADA"]
                market_data = []
                
                for coin in top_coins:
                    try:
                        price_data = await get_real_time_price(coin)
                        market_data.append(price_data)
                    except:
                        continue
                
                if market_data:
                    total_market_cap = global_data.get("total_market_cap", {}).get("usd", 0)
                    total_volume_24h = global_data.get("total_volume", {}).get("usd", 0)
                    
                    # Calculate Bitcoin dominance
                    btc_data = next((coin for coin in market_data if coin['symbol'] == 'BTC'), None)
                    bitcoin_dominance = (btc_data['market_cap'] / total_market_cap * 100) if btc_data and total_market_cap > 0 else 50.0
                    
                    # Simple fear/greed calculation based on average 24h change
                    avg_change = np.mean([coin['change_24h'] for coin in market_data])
                    if avg_change > 5:
                        fear_greed_index = 75  # Greed
                        market_sentiment = "Bullish"
                    elif avg_change < -5:
                        fear_greed_index = 25  # Fear
                        market_sentiment = "Bearish"
                    else:
                        fear_greed_index = 50  # Neutral
                        market_sentiment = "Neutral"
                    
                    # Get trending coins (top performers in last 24h)
                    trending_coins = sorted(market_data, key=lambda x: x['change_24h'], reverse=True)[:5]
                    trending_symbols = [coin['symbol'] for coin in trending_coins]
                    
                    return {
                        "total_market_cap": round(total_market_cap, 2),
                        "total_volume_24h": round(total_volume_24h, 2),
                        "bitcoin_dominance": round(bitcoin_dominance, 2),
                        "fear_greed_index": fear_greed_index,
                        "trending_coins": trending_symbols,
                        "market_sentiment": market_sentiment,
                        "last_updated": datetime.now()
                    }
        
    except Exception as e:
        print(f"Error fetching market overview: {str(e)}")
    
    # Fallback data
    return {
        "total_market_cap": 2500000000000,
        "total_volume_24h": 50000000000,
        "bitcoin_dominance": 52.5,
        "fear_greed_index": 45,
        "trending_coins": ["BTC", "ETH", "BNB", "SOL", "ADA"],
        "market_sentiment": "Neutral",
        "last_updated": datetime.now()
    }

async def get_crypto_news() -> List[Dict[str, Any]]:
    """Get cryptocurrency news from NewsAPI or other free news sources with cache"""
    try:
        # Check cache first - 5 minutes expiry for news
        cache_key = "crypto_news"
        if cache_key in news_cache and cache_key in news_cache_expiry:
            if datetime.now() < news_cache_expiry[cache_key]:
                return news_cache[cache_key]
        
        # NewsAPI 的替代方案：使用免費的 CryptoCompare 新聞 API
        async with httpx.AsyncClient() as client:
            # Try CryptoCompare News API first (free tier)
            response = await client.get(
                "https://min-api.cryptocompare.com/data/v2/news/",
                params={
                    "lang": "EN",
                    "sortOrder": "latest",
                    "extraParams": "crypto-tracker"
                },
                timeout=10.0
            )
            
            news_items = []
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("Data", [])[:10]  # Get top 10 news
                
                for article in articles:
                    # Convert timestamp to datetime
                    published_timestamp = article.get("published_on", 0)
                    published_at = datetime.fromtimestamp(published_timestamp) if published_timestamp else datetime.now()
                    
                    # Clean up title and body
                    title = article.get("title", "").strip()
                    body = article.get("body", "").strip()
                    
                    # Truncate body to reasonable length
                    if len(body) > 200:
                        body = body[:200] + "..."
                    
                    news_item = {
                        "title": title,
                        "description": body,
                        "url": article.get("url", ""),
                        "image_url": article.get("imageurl", ""),
                        "source": article.get("source_info", {}).get("name", "CryptoCompare"),
                        "published_at": published_at,
                        "sentiment": "neutral"  # Default sentiment
                    }
                    
                    if title and body:  # Only add if we have essential content
                        news_items.append(news_item)
            
            # Fallback to manual crypto news if API fails
            if len(news_items) < 5:
                fallback_news = [
                    {
                        "title": "比特幣價格分析：技術面顯示強勁支撐位",
                        "description": "最新的技術分析顯示，比特幣在關鍵支撐位獲得強勁支持，多項指標暗示可能出現反彈趨勢...",
                        "url": "https://example.com/btc-analysis",
                        "image_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/bitcoin.png",
                        "source": "Crypto Analytics",
                        "published_at": datetime.now() - timedelta(hours=1),
                        "sentiment": "bullish"
                    },
                    {
                        "title": "以太坊2.0質押量突破新高",
                        "description": "以太坊網絡的質押總量達到歷史新高，顯示投資者對該網絡長期發展的信心持續增強...",
                        "url": "https://example.com/eth-staking",
                        "image_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/ethereum.png",
                        "source": "Ethereum News",
                        "published_at": datetime.now() - timedelta(hours=2),
                        "sentiment": "bullish"
                    },
                    {
                        "title": "幣安智能鏈生態系統持續擴張",
                        "description": "BNB Chain上的DeFi項目數量持續增長，新興項目為生態系統帶來更多創新和流動性...",
                        "url": "https://example.com/bnb-ecosystem",
                        "image_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/binancecoin.png",
                        "source": "DeFi Times",
                        "published_at": datetime.now() - timedelta(hours=3),
                        "sentiment": "bullish"
                    },
                    {
                        "title": "加密貨幣監管環境逐漸明朗",
                        "description": "各國監管機構正在制定更清晰的加密貨幣監管框架，為行業發展提供更穩定的環境...",
                        "url": "https://example.com/crypto-regulation",
                        "image_url": "https://via.placeholder.com/300x200?text=Regulation+News",
                        "source": "Regulatory Watch",
                        "published_at": datetime.now() - timedelta(hours=4),
                        "sentiment": "neutral"
                    },
                    {
                        "title": "DeFi總鎖倉價值(TVL)創今年新高",
                        "description": "去中心化金融協議的總鎖倉價值突破新的里程碑，反映了市場對DeFi產品的持續需求...",
                        "url": "https://example.com/defi-tvl",
                        "image_url": "https://via.placeholder.com/300x200?text=DeFi+News",
                        "source": "DeFi Pulse",
                        "published_at": datetime.now() - timedelta(hours=5),
                        "sentiment": "bullish"
                    }
                ]
                
                # Add fallback news if we don't have enough real news
                while len(news_items) < 10 and fallback_news:
                    news_items.append(fallback_news.pop(0))
            
            # Cache the results for 5 minutes
            news_cache[cache_key] = news_items
            news_cache_expiry[cache_key] = datetime.now() + timedelta(minutes=5)
            
            return news_items
        
    except Exception as e:
        print(f"Error fetching crypto news: {str(e)}")
        
        # Return fallback news data
        fallback_news = [
            {
                "title": "加密貨幣市場今日總覽",
                "description": "今日加密貨幣市場表現穩定，主要貨幣維持在關鍵支撐位附近，市場情緒保持謹慎樂觀...",
                "url": "https://example.com/market-overview",
                "image_url": "https://via.placeholder.com/300x200?text=Market+News",
                "source": "Crypto Daily",
                "published_at": datetime.now() - timedelta(minutes=30),
                "sentiment": "neutral"
            },
            {
                "title": "機構投資者持續增持比特幣",
                "description": "多家知名投資機構本週宣布增持比特幣，顯示機構資金對加密貨幣資產類別的信心持續增強...",
                "url": "https://example.com/institutional-investment",
                "image_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/bitcoin.png",
                "source": "Investment Weekly",
                "published_at": datetime.now() - timedelta(hours=1),
                "sentiment": "bullish"
            },
            {
                "title": "區塊鏈技術在傳統金融領域應用擴大",
                "description": "越來越多傳統金融機構開始探索區塊鏈技術的實際應用，為加密貨幣行業發展帶來新機遇...",
                "url": "https://example.com/blockchain-adoption",
                "image_url": "https://via.placeholder.com/300x200?text=Blockchain+Tech",
                "source": "FinTech Review",
                "published_at": datetime.now() - timedelta(hours=2),
                "sentiment": "bullish"
            }
        ]
        
        return fallback_news

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Crypto Tracker API is running", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "websocket_connections": len(manager.active_connections),
        "version": "2.0.0"
    }

@app.get("/api/websocket/status")
async def websocket_status():
    """Get WebSocket connection statistics"""
    return {
        "active_connections": len(manager.active_connections),
        "last_broadcast": manager.last_broadcast_data.get('timestamp') if manager.last_broadcast_data else None,
        "server_status": "healthy",
        "timestamp": datetime.now()
    }

@app.get("/api/crypto/prices/{symbol}")
async def get_crypto_price(symbol: str):
    """Get current price data for a cryptocurrency"""
    try:
        if symbol.upper() not in COINGECKO_COINS:
            raise HTTPException(status_code=400, detail=f"Unsupported cryptocurrency: {symbol}")
        
        price_data = await get_real_time_price(symbol)
        return price_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crypto/prices")
async def get_all_crypto_prices():
    """Get current price data for all supported cryptocurrencies"""
    try:
        all_prices = []
        for symbol in COINGECKO_COINS.keys():
            try:
                price_data = await get_real_time_price(symbol)
                all_prices.append(price_data)
            except:
                continue
        
        return {
            "prices": all_prices,
            "count": len(all_prices),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crypto/real-prices")
async def get_real_crypto_prices_endpoint():
    """Get current real-time price data using HIGH-QUALITY MOCK DATA (APIs disabled)"""
    try:
        # Always use Mock data - no fallback to real APIs during development
        print("🎭 Serving high-quality mock crypto data")
        mock_prices = await get_real_crypto_prices()
        
        if mock_prices and len(mock_prices) > 0:
            return {
                "prices": mock_prices,
                "count": len(mock_prices),
                "timestamp": datetime.now(),
                "source": "Mock_Data"
            }
        else:
            # If mock data fails, return minimal fallback
            return {
                "prices": [{
                    "symbol": "BTC",
                    "price": 43500.0,
                    "change_24h": 2.5,
                    "volume_24h": 25000000000,
                    "market_cap": 850000000000,
                    "high_24h": 44000.0,
                    "low_24h": 42500.0,
                    "timestamp": datetime.now().isoformat(),
                    "name": "Bitcoin",
                    "change_1h": 0.8,
                    "change_7d": 5.2,
                    "logo": "",
                    "logo_url": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/bitcoin.png",
                    "unit": "USD",
                    "reference_id": "mock-btc-minimal",
                    "data_source": "Mock"
                }],
                "count": 1,
                "timestamp": datetime.now(),
                "source": "Mock_Fallback"
            }
        
    except Exception as e:
        print(f"Error in mock crypto prices endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mock data service error: {str(e)}")

@app.get("/api/crypto/technical/{symbol}")
async def get_technical_indicators(symbol: str):
    """Get technical analysis indicators for a cryptocurrency"""
    try:
        if symbol.upper() not in COINGECKO_COINS:
            raise HTTPException(status_code=400, detail=f"Unsupported cryptocurrency: {symbol}")
        
        tech_data = await calculate_technical_indicators(symbol)
        return tech_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations/{symbol}")
async def get_investment_recommendation(symbol: str, timeframe: str = "medium"):
    """Get AI-powered investment recommendations"""
    try:
        if symbol.upper() not in COINGECKO_COINS:
            raise HTTPException(status_code=400, detail=f"Unsupported cryptocurrency: {symbol}")
        
        if timeframe not in ["short", "medium", "long"]:
            timeframe = "medium"
        
        recommendation = await generate_investment_recommendation(symbol, timeframe)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/overview")
async def get_market_overview_endpoint():
    """Get overall market overview"""
    try:
        market_data = await get_market_overview()
        return market_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crypto/supported")
async def get_supported_cryptocurrencies():
    """Get list of supported cryptocurrencies"""
    return {
        "supported_coins": list(COINGECKO_COINS.keys()),
        "count": len(COINGECKO_COINS),
        "timestamp": datetime.now()
    }

@app.get("/api/crypto/search/{query}")
async def search_cryptocurrencies(query: str):
    """Search for cryptocurrencies by name or symbol"""
    try:
        query = query.upper()
        results = []
        
        for symbol, coin_id in COINGECKO_COINS.items():
            if query in symbol or query in coin_id:
                try:
                    price_data = await get_real_time_price(symbol)
                    results.append(price_data)
                except:
                    continue
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/analyze")
async def analyze_portfolio():
    """Analyze portfolio performance and provide insights"""
    try:
        # Get market overview for context
        market_data = await get_market_overview()
        
        # Get top cryptocurrencies for portfolio analysis
        top_coins = ["BTC", "ETH", "BNB", "SOL", "ADA"]
        portfolio_data = []
        
        for coin in top_coins:
            try:
                price_data = await get_real_time_price(coin)
                tech_data = await calculate_technical_indicators(coin)
                recommendation = await generate_investment_recommendation(coin, "medium")
                
                portfolio_data.append({
                    "symbol": coin,
                    "price": price_data['price'],
                    "change_24h": price_data['change_24h'],
                    "rsi": tech_data['rsi'],
                    "recommendation": recommendation['recommendation'],
                    "confidence": recommendation['confidence'],
                    "risk_level": recommendation['risk_level']
                })
            except:
                continue
        
        # Calculate portfolio metrics
        total_change = sum(coin['change_24h'] for coin in portfolio_data)
        avg_change = total_change / len(portfolio_data) if portfolio_data else 0
        
        # Determine portfolio sentiment
        if avg_change > 3:
            sentiment = "Bullish"
            risk_level = "Medium-High"
        elif avg_change < -3:
            sentiment = "Bearish"
            risk_level = "High"
        else:
            sentiment = "Neutral"
            risk_level = "Medium"
        
        # Generate portfolio recommendations
        recommendations = []
        if avg_change < -5:
            recommendations.append("Consider rebalancing portfolio to reduce risk")
        if any(coin['rsi'] > 70 for coin in portfolio_data):
            recommendations.append("Some assets may be overbought - consider taking profits")
        if any(coin['rsi'] < 30 for coin in portfolio_data):
            recommendations.append("Some assets may be oversold - consider buying opportunities")
        
        return {
            "portfolio_summary": {
                "total_assets": len(portfolio_data),
                "average_change_24h": round(avg_change, 2),
                "sentiment": sentiment,
                "risk_level": risk_level
            },
            "assets": portfolio_data,
            "market_context": {
                "market_sentiment": market_data['market_sentiment'],
                "fear_greed_index": market_data['fear_greed_index'],
                "bitcoin_dominance": market_data['bitcoin_dominance']
            },
            "recommendations": recommendations,
            "last_updated": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crypto/news")
async def get_crypto_news_endpoint():
    """Get latest cryptocurrency news"""
    try:
        news_data = await get_crypto_news()
        return {
            "news": news_data,
            "count": len(news_data),
            "last_updated": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = f"client_{len(manager.active_connections) + 1}_{datetime.now().timestamp()}"
    
    try:
        await manager.connect(websocket)
        logging.info(f"WebSocket client {client_id} connected")
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "server_status": "healthy"
        }, cls=DateTimeEncoder))
        
        # Send initial data
        try:
            initial_data = await get_all_market_data()
            if initial_data and (initial_data.get('prices') or initial_data.get('overview')):
                await websocket.send_text(json.dumps({
                    "type": "initial_data",
                    "data": initial_data,
                    "timestamp": datetime.now().isoformat(),
                    "client_id": client_id
                }, cls=DateTimeEncoder))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Unable to fetch initial market data",
                    "timestamp": datetime.now().isoformat()
                }, cls=DateTimeEncoder))
        except Exception as e:
            logging.error(f"Error sending initial data to {client_id}: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Failed to load initial data",
                "timestamp": datetime.now().isoformat()
            }, cls=DateTimeEncoder))
        
        # Message handling loop
        while True:
            try:
                # Wait for messages with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                message = json.loads(data)
                
                # Handle different message types from client
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat(),
                        "client_id": client_id
                    }))
                    
                elif message.get("type") == "request_data":
                    try:
                        market_data = await get_all_market_data()
                        if market_data:
                            await websocket.send_text(json.dumps({
                                "type": "market_update",
                                "data": market_data,
                                "timestamp": datetime.now().isoformat(),
                                "client_id": client_id,
                                "requested": True
                            }))
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": "No market data available",
                                "timestamp": datetime.now().isoformat()
                            }))
                    except Exception as e:
                        logging.error(f"Error fetching requested data for {client_id}: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Failed to fetch market data",
                            "timestamp": datetime.now().isoformat()
                        }))
                        
                elif message.get("type") == "subscribe":
                    # Future: Handle specific symbol subscriptions
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "symbols": message.get("symbols", ["all"]),
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except asyncio.TimeoutError:
                # Send keepalive ping if no messages received
                try:
                    await websocket.send_text(json.dumps({
                        "type": "keepalive",
                        "timestamp": datetime.now().isoformat()
                    }))
                except:
                    break
                    
            except WebSocketDisconnect:
                logging.info(f"WebSocket client {client_id} disconnected normally")
                break
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }))
                
            except Exception as e:
                logging.error(f"Error processing message from {client_id}: {e}")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Message processing error",
                        "timestamp": datetime.now().isoformat()
                    }))
                except:
                    break
                
    except WebSocketDisconnect:
        logging.info(f"WebSocket client {client_id} disconnected during setup")
    except Exception as e:
        logging.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        manager.disconnect(websocket)
        logging.info(f"WebSocket client {client_id} cleanup completed")

async def get_all_market_data():
    """Get all market data in a single call for WebSocket broadcasting"""
    try:
        # Get crypto prices
        crypto_symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOT', 'MATIC']
        prices = []
        for symbol in crypto_symbols:
            try:
                price_data = await get_real_time_price(symbol)
                prices.append(price_data)
            except:
                continue
        
        # Get market overview
        overview = await get_market_overview()
        
        return {
            "prices": prices,
            "overview": overview
        }
    except Exception as e:
        logging.error(f"Error getting all market data: {e}")
        return {"prices": [], "overview": {}}

# Background task for real-time data broadcasting
async def broadcast_market_data():
    """Background task that broadcasts market data to all connected clients"""
    consecutive_errors = 0
    max_errors = 5
    
    while True:
        try:
            if manager.active_connections:
                market_data = await get_all_market_data()
                if market_data and (market_data.get('prices') or market_data.get('overview')):
                    await manager.broadcast({
                        "type": "market_update",
                        "data": market_data,
                        "timestamp": datetime.now().isoformat(),
                        "server_status": "healthy",
                        "active_connections": len(manager.active_connections)
                    })
                    consecutive_errors = 0  # Reset error counter on success
                else:
                    logging.warning("Empty market data received, skipping broadcast")
            else:
                # No active connections, wait longer to save resources
                await asyncio.sleep(15)
                continue
                
        except Exception as e:
            consecutive_errors += 1
            logging.error(f"Error broadcasting market data (attempt {consecutive_errors}/{max_errors}): {e}")
            
            # If too many consecutive errors, wait longer before retrying
            if consecutive_errors >= max_errors:
                logging.error(f"Too many consecutive errors, waiting 30 seconds before retry")
                await asyncio.sleep(30)
                consecutive_errors = 0
                continue
        
        # Adaptive delay based on connection count and error state
        if consecutive_errors > 0:
            delay = min(10 + consecutive_errors * 2, 30)  # Exponential backoff with max 30s
        else:
            delay = 3 if len(manager.active_connections) > 0 else 10  # Faster updates when clients connected
        
        await asyncio.sleep(delay)

# Start background task when the application starts
@app.on_event("startup")
async def startup_event():
    # Start the background task for broadcasting
    asyncio.create_task(broadcast_market_data())
    logging.info("Real-time data broadcasting started")

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)