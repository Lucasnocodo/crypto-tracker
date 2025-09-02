import React from 'react';
import { Card, Typography } from 'antd';

const { Text } = Typography;

const FeatureBanner = ({ isDarkMode }) => {
  return (
    <Card style={{
      marginBottom: '16px',
      background: isDarkMode 
        ? 'linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)' 
        : 'linear-gradient(90deg, rgba(16, 185, 129, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)',
      border: `1px solid ${isDarkMode ? 'rgba(16, 185, 129, 0.3)' : 'rgba(16, 185, 129, 0.2)'}`,
      textAlign: 'center'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
        <span style={{ fontSize: '16px' }}>✨</span>
        <Text style={{
          fontSize: '14px',
          fontWeight: '600',
          color: isDarkMode ? '#10b981' : '#059669'
        }}>
          新功能已啟用：實時Logo顯示、多時間段價格變動（1h/24h/7d）、數據來源標識、24小時最高/最低價
        </Text>
        <span style={{ fontSize: '16px' }}>🚀</span>
      </div>
    </Card>
  );
};

export default FeatureBanner;