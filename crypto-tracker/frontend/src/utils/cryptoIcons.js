// Cryptocurrency icon mapping utilities
export const getCryptoIcon = (symbol) => {
  const iconIds = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'AVAX': 'avalanche-2',
    'DOT': 'polkadot',
    'MATIC': 'matic-network',
    'LINK': 'chainlink',
    'UNI': 'uniswap',
    'LTC': 'litecoin',
    'BCH': 'bitcoin-cash',
    'ATOM': 'cosmos',
    'ETC': 'ethereum-classic',
    'USDC': 'usd-coin',
    'USDT': 'tether',
    'DAI': 'dai'
  };
  return iconIds[symbol] || 'cryptocurrency';
};