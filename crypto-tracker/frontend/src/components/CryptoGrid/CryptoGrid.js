import React from 'react';
import { Typography, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import CryptoCard from '../CryptoCard/CryptoCard';

const { Title, Text } = Typography;

const CryptoGrid = ({ 
  marketData, 
  previousMarketData, 
  isUpdating, 
  isDarkMode, 
  networkError, 
  manualRefresh 
}) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
      gap: '24px',
      marginBottom: '40px'
    }}>
      {marketData?.prices && marketData.prices.length > 0 ? (
        marketData.prices.map((crypto, index) => {
          // Find previous data for this crypto
          const previousCrypto = previousMarketData?.prices?.find(
            prev => prev.symbol === crypto.symbol
          );

          return (
            <div 
              key={crypto.symbol || index}
              style={{
                transform: 'translateY(0)',
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                animation: `fadeInUp 0.6s ease-out ${index * 0.1}s backwards`
              }}
              className="crypto-grid-item"
            >
              <CryptoCard
                data={crypto}
                isUpdating={isUpdating}
                previousData={previousCrypto}
                isDarkMode={isDarkMode}
              />
            </div>
          );
        })
      ) : (
        <div style={{
          gridColumn: '1 / -1',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '60px 20px',
          background: isDarkMode
            ? 'linear-gradient(145deg, rgba(26, 26, 46, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 250, 255, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px',
          border: isDarkMode
            ? '1px solid rgba(239, 68, 68, 0.2)'
            : '1px solid rgba(239, 68, 68, 0.15)',
          boxShadow: isDarkMode
            ? '0 10px 40px rgba(0, 0, 0, 0.4)'
            : '0 10px 40px rgba(239, 68, 68, 0.1)'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ 
              fontSize: '48px', 
              marginBottom: '16px',
              filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))'
            }}>
              {networkError ? '⚠️' : '⏳'}
            </div>
            
            <Title level={4} style={{
              color: networkError ? '#ef4444' : (isDarkMode ? '#ffffff' : '#1e3c72'),
              marginBottom: '8px',
              fontWeight: '700'
            }}>
              {networkError ? "網絡連接錯誤" : "載入中..."}
            </Title>
            
            <Text style={{
              color: isDarkMode ? '#a0aec0' : '#64748b',
              fontSize: '14px',
              marginBottom: '20px',
              display: 'block'
            }}>
              {networkError ? "請檢查網絡連接或嘗試手動刷新" : "正在獲取最新加密貨幣數據..."}
            </Text>
            
            {networkError && (
              <Button
                icon={<ReloadOutlined />}
                onClick={manualRefresh}
                style={{
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  border: 'none',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '8px 24px',
                  height: 'auto',
                  fontWeight: '600'
                }}
              >
                重新載入
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CryptoGrid;