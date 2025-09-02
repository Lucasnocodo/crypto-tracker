import React from 'react';
import { Card, Typography } from 'antd';
import './MarketOverview.css';

const { Text } = Typography;

const MarketOverview = ({ marketData, isDarkMode }) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '24px',
      marginBottom: '32px'
    }}>
      {/* Total Market Cap Card */}
      <Card
        className="market-stat-card-modern"
        style={{
          background: isDarkMode
            ? 'linear-gradient(145deg, rgba(26, 26, 46, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 250, 255, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: isDarkMode 
            ? '1px solid rgba(16, 185, 129, 0.2)' 
            : '1px solid rgba(30, 60, 114, 0.15)',
          borderRadius: '24px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: isDarkMode
            ? '0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
            : '0 10px 40px rgba(30, 60, 114, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)'
        }}
        bodyStyle={{ padding: '20px' }}
      >
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '50%',
          background: 'linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, transparent 100%)',
          borderRadius: '24px 24px 0 0'
        }} />
        
        <div style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <div style={{
            fontSize: '24px',
            marginBottom: '12px',
            filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))'
          }}>🏦</div>
          
          <Text style={{
            fontSize: '11px',
            color: isDarkMode ? '#9ca3af' : '#6b7280',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            display: 'block',
            marginBottom: '8px'
          }}>
            Total Market Cap
          </Text>
          
          <Text style={{
            fontSize: '24px',
            fontWeight: '900',
            color: isDarkMode ? '#ffffff' : '#1e3c72',
            display: 'block',
            textShadow: isDarkMode 
              ? '0 2px 4px rgba(0, 0, 0, 0.3)' 
              : '0 1px 2px rgba(30, 60, 114, 0.1)',
            fontVariantNumeric: 'tabular-nums'
          }}>
            ${marketData?.overview.total_market_cap ? (marketData.overview.total_market_cap / 1000000000000).toFixed(2) : '0.00'}T
          </Text>
        </div>
      </Card>

      {/* 24H Volume Card */}
      <Card
        className="market-stat-card-modern"
        style={{
          background: isDarkMode
            ? 'linear-gradient(145deg, rgba(26, 26, 46, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 250, 255, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: isDarkMode 
            ? '1px solid rgba(64, 169, 255, 0.2)' 
            : '1px solid rgba(30, 60, 114, 0.15)',
          borderRadius: '24px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: isDarkMode
            ? '0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
            : '0 10px 40px rgba(30, 60, 114, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)'
        }}
        bodyStyle={{ padding: '20px' }}
      >
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '50%',
          background: 'linear-gradient(180deg, rgba(64, 169, 255, 0.05) 0%, transparent 100%)',
          borderRadius: '24px 24px 0 0'
        }} />
        
        <div style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <div style={{
            fontSize: '24px',
            marginBottom: '12px',
            filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))'
          }}>📊</div>
          
          <Text style={{
            fontSize: '11px',
            color: isDarkMode ? '#9ca3af' : '#6b7280',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            display: 'block',
            marginBottom: '8px'
          }}>
            24H Volume
          </Text>
          
          <Text style={{
            fontSize: '24px',
            fontWeight: '900',
            color: isDarkMode ? '#ffffff' : '#1e3c72',
            display: 'block',
            textShadow: isDarkMode 
              ? '0 2px 4px rgba(0, 0, 0, 0.3)' 
              : '0 1px 2px rgba(30, 60, 114, 0.1)',
            fontVariantNumeric: 'tabular-nums'
          }}>
            ${marketData?.overview.total_volume_24h ? (marketData.overview.total_volume_24h / 1000000000).toFixed(1) : '0.0'}B
          </Text>
        </div>
      </Card>

      {/* BTC Dominance Card */}
      <Card
        className="market-stat-card-modern"
        style={{
          background: isDarkMode
            ? 'linear-gradient(145deg, rgba(26, 26, 46, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 250, 255, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: isDarkMode 
            ? '1px solid rgba(245, 158, 11, 0.2)' 
            : '1px solid rgba(245, 158, 11, 0.15)',
          borderRadius: '24px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: isDarkMode
            ? '0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
            : '0 10px 40px rgba(30, 60, 114, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)'
        }}
        bodyStyle={{ padding: '20px' }}
      >
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '50%',
          background: 'linear-gradient(180deg, rgba(245, 158, 11, 0.05) 0%, transparent 100%)',
          borderRadius: '24px 24px 0 0'
        }} />
        
        <div style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <div style={{
            fontSize: '24px',
            marginBottom: '12px',
            filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))'
          }}>₿</div>
          
          <Text style={{
            fontSize: '11px',
            color: isDarkMode ? '#9ca3af' : '#6b7280',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            display: 'block',
            marginBottom: '8px'
          }}>
            BTC Dominance
          </Text>
          
          <Text style={{
            fontSize: '24px',
            fontWeight: '900',
            color: '#f59e0b',
            display: 'block',
            textShadow: '0 2px 4px rgba(245, 158, 11, 0.2)',
            fontVariantNumeric: 'tabular-nums'
          }}>
            {marketData?.overview.bitcoin_dominance || '0'}%
          </Text>
        </div>
      </Card>

      {/* Fear & Greed Index Card */}
      <Card
        className="market-stat-card-modern"
        style={{
          background: isDarkMode
            ? 'linear-gradient(145deg, rgba(26, 26, 46, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 250, 255, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: isDarkMode 
            ? `1px solid ${marketData?.overview.fear_greed_index > 50 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}` 
            : `1px solid ${marketData?.overview.fear_greed_index > 50 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)'}`,
          borderRadius: '24px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: isDarkMode
            ? '0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
            : '0 10px 40px rgba(30, 60, 114, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)'
        }}
        bodyStyle={{ padding: '20px' }}
      >
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '50%',
          background: marketData?.overview.fear_greed_index > 50 
            ? 'linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, transparent 100%)'
            : 'linear-gradient(180deg, rgba(239, 68, 68, 0.05) 0%, transparent 100%)',
          borderRadius: '24px 24px 0 0'
        }} />
        
        <div style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <div style={{
            fontSize: '24px',
            marginBottom: '12px',
            filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))'
          }}>
            {marketData?.overview.fear_greed_index > 50 ? '😤' : '😨'}
          </div>
          
          <Text style={{
            fontSize: '11px',
            color: isDarkMode ? '#9ca3af' : '#6b7280',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            display: 'block',
            marginBottom: '8px'
          }}>
            Fear & Greed
          </Text>
          
          <Text style={{
            fontSize: '24px',
            fontWeight: '900',
            color: marketData?.overview.fear_greed_index > 50 ? '#10b981' : '#ef4444',
            display: 'block',
            textShadow: marketData?.overview.fear_greed_index > 50 
              ? '0 2px 4px rgba(16, 185, 129, 0.2)' 
              : '0 2px 4px rgba(239, 68, 68, 0.2)',
            fontVariantNumeric: 'tabular-nums'
          }}>
            {marketData?.overview.fear_greed_index || '50'}
          </Text>
          
          <Text style={{
            fontSize: '10px',
            color: isDarkMode ? '#6b7280' : '#9ca3af',
            fontWeight: '600',
            marginTop: '4px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            {marketData?.overview.fear_greed_index > 50 ? 'Greed' : 'Fear'}
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default MarketOverview;