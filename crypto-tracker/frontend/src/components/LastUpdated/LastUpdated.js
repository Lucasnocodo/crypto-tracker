import React from 'react';
import { Typography } from 'antd';

const { Text } = Typography;

const LastUpdated = ({ marketData, isDarkMode }) => {
  if (!marketData?.overview.last_updated) {
    return null;
  }

  return (
    <div style={{
      textAlign: 'center',
      marginBottom: '24px',
      padding: '12px 24px',
      background: isDarkMode
        ? 'rgba(255, 255, 255, 0.02)'
        : 'rgba(0, 0, 0, 0.02)',
      borderRadius: '16px',
      backdropFilter: 'blur(10px)',
      border: isDarkMode
        ? '1px solid rgba(255, 255, 255, 0.05)'
        : '1px solid rgba(0, 0, 0, 0.05)'
    }}>
      <Text style={{ 
        fontSize: '11px', 
        color: isDarkMode ? '#9ca3af' : '#6b7280',
        fontWeight: '500',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px'
      }}>
        <span>🕒</span>
        Market data last updated: {new Date(marketData.overview.last_updated).toLocaleString()}
      </Text>
    </div>
  );
};

export default LastUpdated;