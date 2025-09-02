from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = relationship("PriceData", back_populates="cryptocurrency")
    technical_indicators = relationship("TechnicalIndicator", back_populates="cryptocurrency")
    recommendations = relationship("InvestmentRecommendation", back_populates="cryptocurrency")

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    price = Column(Float)
    volume_24h = Column(Float)
    market_cap = Column(Float)
    change_1h = Column(Float)
    change_24h = Column(Float)
    change_7d = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="prices")

class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    
    # Moving Averages
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    ema_12 = Column(Float)
    ema_26 = Column(Float)
    
    # Oscillators
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    
    # Bollinger Bands
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    
    # Volume indicators
    volume_sma = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="technical_indicators")

class MarketSentiment(Base):
    __tablename__ = "market_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    
    sentiment_score = Column(Float)  # -1 to 1
    news_count = Column(Integer)
    positive_mentions = Column(Integer)
    negative_mentions = Column(Integer)
    neutral_mentions = Column(Integer)
    fear_greed_index = Column(Float)
    
    source = Column(String(50))  # 'news', 'social', 'reddit', etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class InvestmentRecommendation(Base):
    __tablename__ = "investment_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    
    recommendation = Column(String(10))  # BUY, SELL, HOLD
    confidence_score = Column(Float)  # 0 to 1
    timeframe = Column(String(10))  # short, medium, long
    
    target_price = Column(Float)
    stop_loss = Column(Float)
    reasoning = Column(Text)
    
    # Scores from different analysis methods
    technical_score = Column(Float)
    fundamental_score = Column(Float)
    sentiment_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="recommendations")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    subscription_expires = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")

class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlist")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    
    quantity = Column(Float)
    average_buy_price = Column(Float)
    total_invested = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(1000))
    source = Column(String(100))
    
    sentiment_score = Column(Float)
    relevance_score = Column(Float)
    
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Related cryptocurrencies (many-to-many relationship)
    mentioned_cryptos = Column(String(500))  # JSON string of crypto symbols