import React from 'react';
import { Card, Typography } from 'antd';
import { getSentimentColor, getSentimentIcon, getSentimentText, formatTimeAgo } from '../../utils/formatters';
import './NewsCard.css';

const { Title, Text } = Typography;

const NewsCard = ({ newsItem, isDarkMode }) => {
  return (
    <Card
      size="small"
      className="news-card"
      hoverable
      style={{
        height: '100%',
        background: isDarkMode ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        border: isDarkMode ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
        transition: 'all 0.3s ease',
        cursor: 'pointer'
      }}
      onClick={() => {
        if (newsItem.url && newsItem.url !== 'https://example.com/btc-analysis') {
          window.open(newsItem.url, '_blank', 'noopener,noreferrer');
        }
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* News image */}
        {newsItem.image_url && newsItem.image_url !== 'https://via.placeholder.com/300x200?text=Market+News' && (
          <div style={{
            width: '100%',
            height: '120px',
            marginBottom: '12px',
            borderRadius: '8px',
            overflow: 'hidden',
            background: `url(${newsItem.image_url}) center/cover no-repeat`,
            backgroundColor: isDarkMode ? '#333' : '#f5f5f5'
          }} />
        )}

        {/* Sentiment indicator */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', gap: '6px' }}>
          <span style={{ fontSize: '14px' }}>{getSentimentIcon(newsItem.sentiment)}</span>
          <Text style={{
            fontSize: '11px',
            color: getSentimentColor(newsItem.sentiment),
            fontWeight: '600',
            textTransform: 'uppercase',
            padding: '2px 6px',
            borderRadius: '4px',
            background: `${getSentimentColor(newsItem.sentiment)}15`
          }}>
            {getSentimentText(newsItem.sentiment)}
          </Text>
          <Text style={{
            fontSize: '10px',
            color: isDarkMode ? '#999' : '#666',
            marginLeft: 'auto'
          }}>
            {newsItem.source}
          </Text>
        </div>

        {/* Title */}
        <Title level={5} style={{
          margin: '0 0 8px 0',
          fontSize: '14px',
          fontWeight: '600',
          lineHeight: '1.4',
          color: isDarkMode ? '#ffffff' : '#1e3c72',
          display: '-webkit-box',
          WebkitBoxOrient: 'vertical',
          WebkitLineClamp: 2,
          overflow: 'hidden',
          textOverflow: 'ellipsis'
        }}>
          {newsItem.title}
        </Title>

        {/* Description */}
        <Text style={{
          fontSize: '12px',
          color: isDarkMode ? '#cccccc' : '#666666',
          lineHeight: '1.5',
          display: '-webkit-box',
          WebkitBoxOrient: 'vertical',
          WebkitLineClamp: 3,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          marginBottom: '12px',
          flex: 1
        }}>
          {newsItem.description}
        </Text>

        {/* Footer with time */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: 'auto',
          paddingTop: '8px',
          borderTop: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)'}`
        }}>
          <Text style={{
            fontSize: '10px',
            color: isDarkMode ? '#999999' : '#999999',
            fontWeight: '500'
          }}>
            {formatTimeAgo(newsItem.published_at)}
          </Text>
          <Text style={{
            fontSize: '10px',
            color: '#1890ff',
            fontWeight: '600'
          }}>
            ±€ô ’
          </Text>
        </div>
      </div>
    </Card>
  );
};

export default NewsCard;