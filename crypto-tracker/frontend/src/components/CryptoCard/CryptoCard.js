import React from 'react';
import { Card, Typography } from 'antd';
import { getCryptoIcon } from '../../utils/cryptoIcons';
import './CryptoCard.css';

const { Text } = Typography;

const CryptoCard = ({ data, isUpdating = false, previousData = null, isDarkMode }) => {
  // Detect price changes for flash effect
  const priceChanged = previousData && previousData.price !== data.price;
  const priceIncreased = priceChanged && data.price > previousData.price;

  return (
    <div className="crypto-card-container">
      <Card
        size="small"
        className={`crypto-card-modern ${isUpdating ? 'updating' : ''} ${priceChanged ? 'price-changed' : ''}`}
        style={{
          height: '100%',
          background: isDarkMode 
            ? 'linear-gradient(145deg, rgba(26, 26, 46, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%)'
            : 'linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(250, 250, 255, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: isDarkMode 
            ? '1px solid rgba(64, 169, 255, 0.2)' 
            : '1px solid rgba(30, 60, 114, 0.15)',
          borderRadius: '24px',
          overflow: 'hidden',
          position: 'relative',
          cursor: 'pointer',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isDarkMode
            ? '0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
            : '0 10px 40px rgba(30, 60, 114, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8)'
        }}
        bodyStyle={{
          padding: '20px',
          background: 'transparent'
        }}
      >
        {/* Gradient overlay effect */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '40%',
          background: isDarkMode
            ? 'linear-gradient(180deg, rgba(64, 169, 255, 0.05) 0%, transparent 100%)'
            : 'linear-gradient(180deg, rgba(30, 60, 114, 0.03) 0%, transparent 100%)',
          borderRadius: '24px 24px 0 0',
          pointerEvents: 'none'
        }} />

        {/* Shimmer effect */}
        {isUpdating && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent)',
            animation: 'shimmer 2s infinite',
            borderRadius: '24px'
          }} />
        )}

        <div style={{ textAlign: 'center', position: 'relative', zIndex: 2 }}>
          {/* Update indicator */}
          {isUpdating && (
            <div style={{
              position: 'absolute',
              top: '-10px',
              right: '-10px',
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #40a9ff, #69c0ff)',
              animation: 'pulse 1.5s ease-in-out infinite',
              boxShadow: '0 0 20px rgba(64, 169, 255, 0.6)',
              border: '2px solid rgba(255, 255, 255, 0.3)'
            }} />
          )}

          {/* Price change flash indicator */}
          {priceChanged && (
            <div style={{
              position: 'absolute',
              top: '-10px',
              left: '-10px',
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: priceIncreased 
                ? 'linear-gradient(135deg, #10b981, #34d399)' 
                : 'linear-gradient(135deg, #ef4444, #f87171)',
              animation: 'priceFlash 2s ease-out',
              boxShadow: `0 0 20px ${priceIncreased ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'}`,
              border: '2px solid rgba(255, 255, 255, 0.3)'
            }} />
          )}

          {/* Data source indicator */}
          {data.data_source && (
            <div style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              fontSize: '9px',
              fontWeight: '700',
              color: '#ffffff',
              background: data.data_source === 'CryptoAPIs' 
                ? 'linear-gradient(135deg, #10b981, #34d399)' 
                : data.data_source === 'CoinGecko' 
                ? 'linear-gradient(135deg, #1890ff, #40a9ff)' 
                : 'linear-gradient(135deg, #faad14, #fbbf24)',
              padding: '3px 8px',
              borderRadius: '12px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              {data.data_source === 'CryptoAPIs' ? 'LIVE' : 
               data.data_source === 'CoinGecko' ? 'CG' : 
               data.data_source === 'Mock' ? 'DEMO' : data.data_source}
            </div>
          )}

          {/* Logo with enhanced styling */}
          <div style={{
            width: '56px',
            height: '56px',
            margin: '16px auto 16px',
            background: data.logo 
              ? `url(data:image/png;base64,${data.logo}) center/contain no-repeat`
              : `url(https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/${getCryptoIcon(data.symbol)}.png) center/contain no-repeat`,
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: isUpdating ? 'rotate(10deg) scale(1.1)' : 'rotate(0deg) scale(1)',
            borderRadius: '28px',
            position: 'relative',
            filter: 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15))'
          }}>
            {/* Logo background glow */}
            <div style={{
              position: 'absolute',
              inset: '-4px',
              background: isDarkMode 
                ? 'linear-gradient(135deg, rgba(64, 169, 255, 0.1), rgba(105, 192, 255, 0.05))'
                : 'linear-gradient(135deg, rgba(30, 60, 114, 0.05), rgba(42, 82, 152, 0.02))',
              borderRadius: '32px',
              opacity: isUpdating ? 1 : 0,
              transition: 'opacity 0.4s ease'
            }} />
          </div>

          {/* Symbol with enhanced styling */}
          <Text strong className="crypto-symbol-modern" style={{
            fontSize: '18px',
            display: 'block',
            marginBottom: '4px',
            color: isDarkMode ? '#ffffff' : '#1e3c72',
            fontWeight: '800',
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
            textShadow: isDarkMode 
              ? '0 2px 4px rgba(0, 0, 0, 0.3)' 
              : '0 1px 2px rgba(30, 60, 114, 0.1)'
          }}>
            {data.symbol}
          </Text>

          {/* Full name with improved styling */}
          {data.name && (
            <Text style={{
              fontSize: '12px',
              color: isDarkMode ? '#a0aec0' : '#64748b',
              display: 'block',
              marginBottom: '16px',
              fontWeight: '500',
              opacity: 0.8
            }}>
              {data.name}
            </Text>
          )}

          {/* Price with dramatic styling */}
          <div style={{
            background: isDarkMode
              ? 'linear-gradient(135deg, rgba(64, 169, 255, 0.1), rgba(105, 192, 255, 0.05))'
              : 'linear-gradient(135deg, rgba(30, 60, 114, 0.05), rgba(42, 82, 152, 0.02))',
            borderRadius: '16px',
            padding: '12px',
            marginBottom: '16px',
            border: isDarkMode
              ? '1px solid rgba(64, 169, 255, 0.2)'
              : '1px solid rgba(30, 60, 114, 0.1)'
          }}>
            <Text className={`crypto-price-modern ${priceChanged ? 'flash' : ''}`} style={{
              fontSize: '20px',
              fontWeight: '900',
              color: priceChanged 
                ? (priceIncreased ? '#10b981' : '#ef4444')
                : (isDarkMode ? '#ffffff' : '#1e3c72'),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.6s ease',
              textShadow: isDarkMode 
                ? '0 2px 4px rgba(0, 0, 0, 0.4)' 
                : '0 1px 2px rgba(0, 0, 0, 0.1)',
              fontVariantNumeric: 'tabular-nums'
            }}>
              ${data.price.toLocaleString()}
              {priceChanged && (
                <span style={{
                  fontSize: '14px',
                  color: priceIncreased ? '#10b981' : '#ef4444',
                  animation: 'bounce 1s ease-in-out'
                }}>
                  {priceIncreased ? '=È' : '=É'}
                </span>
              )}
            </Text>
          </div>

          {/* Multi-timeframe changes in a modern grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(60px, 1fr))',
            gap: '8px',
            marginBottom: '16px'
          }}>
            {/* 1 hour change */}
            {data.change_1h !== undefined && (
              <div style={{
                background: isDarkMode
                  ? 'rgba(255, 255, 255, 0.03)'
                  : 'rgba(0, 0, 0, 0.02)',
                borderRadius: '12px',
                padding: '8px 4px',
                border: isDarkMode
                  ? '1px solid rgba(255, 255, 255, 0.05)'
                  : '1px solid rgba(0, 0, 0, 0.05)'
              }}>
                <div style={{
                  fontSize: '9px',
                  color: isDarkMode ? '#9ca3af' : '#6b7280',
                  fontWeight: '600',
                  marginBottom: '2px',
                  textTransform: 'uppercase'
                }}>1H</div>
                <div style={{
                  fontSize: '11px',
                  fontWeight: '700',
                  color: data.change_1h >= 0 ? '#10b981' : '#ef4444'
                }}>
                  {data.change_1h >= 0 ? '+' : ''}{data.change_1h.toFixed(2)}%
                </div>
              </div>
            )}

            {/* 24 hour change */}
            <div style={{
              background: data.change_24h >= 0 
                ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05))'
                : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05))',
              borderRadius: '12px',
              padding: '8px 4px',
              border: `1px solid ${data.change_24h >= 0 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
            }}>
              <div style={{
                fontSize: '9px',
                color: data.change_24h >= 0 ? '#10b981' : '#ef4444',
                fontWeight: '600',
                marginBottom: '2px',
                textTransform: 'uppercase'
              }}>24H</div>
              <div style={{
                fontSize: '11px',
                fontWeight: '700',
                color: data.change_24h >= 0 ? '#10b981' : '#ef4444'
              }}>
                {data.change_24h >= 0 ? '+' : ''}{data.change_24h.toFixed(2)}%
              </div>
            </div>

            {/* 7 day change */}
            {data.change_7d !== undefined && (
              <div style={{
                background: isDarkMode
                  ? 'rgba(255, 255, 255, 0.03)'
                  : 'rgba(0, 0, 0, 0.02)',
                borderRadius: '12px',
                padding: '8px 4px',
                border: isDarkMode
                  ? '1px solid rgba(255, 255, 255, 0.05)'
                  : '1px solid rgba(0, 0, 0, 0.05)'
              }}>
                <div style={{
                  fontSize: '9px',
                  color: isDarkMode ? '#9ca3af' : '#6b7280',
                  fontWeight: '600',
                  marginBottom: '2px',
                  textTransform: 'uppercase'
                }}>7D</div>
                <div style={{
                  fontSize: '11px',
                  fontWeight: '700',
                  color: data.change_7d >= 0 ? '#10b981' : '#ef4444'
                }}>
                  {data.change_7d >= 0 ? '+' : ''}{data.change_7d.toFixed(2)}%
                </div>
              </div>
            )}
          </div>

          {/* Volume and market info */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: isDarkMode
              ? 'rgba(255, 255, 255, 0.02)'
              : 'rgba(0, 0, 0, 0.02)',
            borderRadius: '12px',
            padding: '8px 12px',
            marginBottom: '12px'
          }}>
            <div style={{ textAlign: 'left' }}>
              <div style={{
                fontSize: '9px',
                color: isDarkMode ? '#9ca3af' : '#6b7280',
                fontWeight: '600',
                textTransform: 'uppercase',
                marginBottom: '2px'
              }}>Volume 24h</div>
              <div style={{
                fontSize: '11px',
                fontWeight: '700',
                color: isDarkMode ? '#e5e7eb' : '#374151'
              }}>
                ${(data.volume_24h / 1000000).toFixed(1)}M
              </div>
            </div>

            {/* Market cap if available */}
            {data.market_cap && (
              <div style={{ textAlign: 'right' }}>
                <div style={{
                  fontSize: '9px',
                  color: isDarkMode ? '#9ca3af' : '#6b7280',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  marginBottom: '2px'
                }}>Market Cap</div>
                <div style={{
                  fontSize: '11px',
                  fontWeight: '700',
                  color: isDarkMode ? '#e5e7eb' : '#374151'
                }}>
                  ${(data.market_cap / 1000000000).toFixed(1)}B
                </div>
              </div>
            )}
          </div>

          {/* High/Low 24h if available */}
          {(data.high_24h || data.low_24h) && (
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              background: isDarkMode
                ? 'rgba(255, 255, 255, 0.02)'
                : 'rgba(0, 0, 0, 0.02)',
              borderRadius: '12px',
              padding: '6px 12px',
              marginBottom: '8px'
            }}>
              {data.low_24h && (
                <div style={{ textAlign: 'left' }}>
                  <span style={{
                    fontSize: '9px',
                    color: '#ef4444',
                    fontWeight: '600'
                  }}>L: </span>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: '600',
                    color: isDarkMode ? '#e5e7eb' : '#374151'
                  }}>
                    ${data.low_24h.toLocaleString()}
                  </span>
                </div>
              )}
              {data.high_24h && (
                <div style={{ textAlign: 'right' }}>
                  <span style={{
                    fontSize: '9px',
                    color: '#10b981',
                    fontWeight: '600'
                  }}>H: </span>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: '600',
                    color: isDarkMode ? '#e5e7eb' : '#374151'
                  }}>
                    ${data.high_24h.toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Last updated timestamp */}
          {data.timestamp && (
            <div style={{
              fontSize: '9px',
              color: isDarkMode ? '#6b7280' : '#9ca3af',
              fontWeight: '500',
              opacity: 0.7,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px'
            }}>
              <span>=R</span>
              {new Date(data.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default CryptoCard;