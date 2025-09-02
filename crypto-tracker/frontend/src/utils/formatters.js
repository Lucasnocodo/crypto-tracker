// Utility functions for formatting data

export const formatTimeAgo = (dateString) => {
  const now = new Date();
  const publishedDate = new Date(dateString);
  const diffInHours = Math.floor((now - publishedDate) / (1000 * 60 * 60));

  if (diffInHours < 1) return '剛才';
  if (diffInHours < 24) return `${diffInHours}小時前`;
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays === 1) return '1天前';
  if (diffInDays < 7) return `${diffInDays}天前`;
  return publishedDate.toLocaleDateString('zh-TW');
};

export const getSentimentColor = (sentiment) => {
  switch (sentiment) {
    case 'bullish': return '#52c41a';
    case 'bearish': return '#ff4d4f';
    default: return '#faad14';
  }
};

export const getSentimentIcon = (sentiment) => {
  switch (sentiment) {
    case 'bullish': return '📈';
    case 'bearish': return '📉';
    default: return '📊';
  }
};

export const getSentimentText = (sentiment) => {
  switch (sentiment) {
    case 'bullish': return '看漲';
    case 'bearish': return '看跌';
    default: return '中性';
  }
};

export const formatPrice = (price) => {
  if (price == null) return 'N/A';
  
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  if (isNaN(numPrice)) return 'N/A';
  
  if (numPrice >= 1000) {
    return `$${numPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  } else if (numPrice >= 1) {
    return `$${numPrice.toFixed(4)}`;
  } else {
    return `$${numPrice.toFixed(6)}`;
  }
};

export const formatChange = (change) => {
  if (change == null) return 'N/A';
  
  const numChange = typeof change === 'string' ? parseFloat(change) : change;
  if (isNaN(numChange)) return 'N/A';
  
  const sign = numChange >= 0 ? '+' : '';
  return `${sign}${numChange.toFixed(2)}%`;
};

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return 'N/A';
  }
};

export const formatMarketCap = (marketCap) => {
  if (marketCap == null) return 'N/A';
  
  const numMarketCap = typeof marketCap === 'string' ? parseFloat(marketCap) : marketCap;
  if (isNaN(numMarketCap)) return 'N/A';
  
  if (numMarketCap >= 1e12) {
    return `$${(numMarketCap / 1e12).toFixed(2)}T`;
  } else if (numMarketCap >= 1e9) {
    return `$${(numMarketCap / 1e9).toFixed(2)}B`;
  } else if (numMarketCap >= 1e6) {
    return `$${(numMarketCap / 1e6).toFixed(2)}M`;
  } else {
    return `$${numMarketCap.toFixed(2)}`;
  }
};

export const formatVolume = (volume) => {
  return formatMarketCap(volume); // Same formatting logic
};