import React from 'react';
import { Card, Typography } from 'antd';
import './RecommendationCard.css';

const { Text } = Typography;

const RecommendationCard = ({ rec, isDarkMode }) => (
  <Card
    size="small"
    className="recommendation-card"
    style={{
      height: '100%',
      background: isDarkMode ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
      border: isDarkMode ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)'
    }}
  >
    <div style={{ textAlign: 'center' }}>
      <Text strong style={{ fontSize: '16px', display: 'block', marginBottom: '8px' }}>
        {rec.symbol}
      </Text>
      <Text style={{
        fontSize: '14px',
        color: rec.recommendation === 'BUY' ? '#52c41a' :
          rec.recommendation === 'SELL' ? '#ff4d4f' : '#faad14',
        fontWeight: '600',
        display: 'block',
        marginBottom: '4px'
      }}>
        {rec.recommendation}
      </Text>
      <Text style={{ fontSize: '12px', color: '#8c8c8c', display: 'block', marginBottom: '4px' }}>
        Confidence: {(rec.confidence * 100).toFixed(0)}%
      </Text>
      <Text style={{ fontSize: '12px', color: '#8c8c8c', display: 'block' }}>
        Risk: {rec.risk_level}
      </Text>
    </div>
  </Card>
);

export default RecommendationCard;