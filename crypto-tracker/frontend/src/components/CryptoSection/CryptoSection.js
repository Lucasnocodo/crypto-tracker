import React from 'react';
import { Typography } from 'antd';

const { Title, Text } = Typography;

const CryptoSection = ({ marketData, isDarkMode }) => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '24px',
      padding: '0 4px'
    }}>
      <Title level={3} style={{
        margin: 0,
        background: isDarkMode
          ? 'linear-gradient(135deg, #40a9ff 0%, #69c0ff 100%)'
          : 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
        fontSize: '24px',
        fontWeight: '800',
        letterSpacing: '0.5px'
      }}>
        🏆 Top Cryptocurrencies
      </Title>
      
      {marketData?.prices && marketData.prices.length > 0 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: isDarkMode
            ? 'rgba(64, 169, 255, 0.1)'
            : 'rgba(30, 60, 114, 0.05)',
          padding: '8px 16px',
          borderRadius: '20px',
          border: isDarkMode
            ? '1px solid rgba(64, 169, 255, 0.2)'
            : '1px solid rgba(30, 60, 114, 0.1)'
        }}>
          <span style={{ fontSize: '12px' }}>📈</span>
          <Text style={{
            fontSize: '12px',
            fontWeight: '600',
            color: isDarkMode ? '#40a9ff' : '#1e3c72'
          }}>
            {marketData.prices.length} Assets
          </Text>
        </div>
      )}
    </div>
  );
};

export default CryptoSection;