import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Layout, Row, Col, Typography, Spin, Alert, Tabs, Button, Card } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import './App.css';

// Import components
import Header from './components/Header/Header';
import UpdateIndicator from './components/UpdateIndicator/UpdateIndicator';

import MarketOverview from './components/MarketOverview/MarketOverview';
import NewsCard from './components/NewsCard/NewsCard';
import RecommendationCard from './components/RecommendationCard/RecommendationCard';
import FeatureBanner from './components/FeatureBanner/FeatureBanner';
import LastUpdated from './components/LastUpdated/LastUpdated';
import CryptoSection from './components/CryptoSection/CryptoSection';
import CryptoGrid from './components/CryptoGrid/CryptoGrid';
import PriceTrendChart from './components/PriceTrendChart/PriceTrendChart';

const { Content } = Layout;
const { Title, Text } = Typography;

const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

function App() {
  const [marketData, setMarketData] = useState(null);
  const [previousMarketData, setPreviousMarketData] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [news, setNews] = useState(null);
  const [newsLoading, setNewsLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('1');
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('crypto-tracker-theme');
    return saved ? JSON.parse(saved) : false;
  });

  // WebSocket and real-time states
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [networkError, setNetworkError] = useState(false);
  const [connectionQuality, setConnectionQuality] = useState('good'); // good, poor, offline

  const ws = useRef(null);
  const reconnectTimer = useRef(null);
  const heartbeatTimer = useRef(null);
  const maxReconnectAttempts = 5;

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        setNetworkError(false);
        setReconnectAttempts(0);

        // Start heartbeat
        startHeartbeat();
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          switch (message.type) {
            case 'connection_established':
              console.log('WebSocket connection established:', message.client_id);
              setWsConnected(true);
              break;

            case 'initial_data':
            case 'market_update':
              setIsUpdating(true);
              setConnectionQuality('good');

              // Update market data with animation
              setTimeout(() => {
                if (message.data && (message.data.prices || message.data.overview)) {
                  // Store previous data for comparison
                  if (marketData) {
                    setPreviousMarketData(marketData);
                  }

                  setMarketData(message.data);
                  setLastUpdate(new Date(message.timestamp));
                  setLoading(false);
                  setError(null);
                  setNetworkError(false);
                } else {
                  console.warn('Received empty market data');
                  // Even with empty data, stop loading to show something
                  setLoading(false);
                }
                setIsUpdating(false);
              }, 300);
              break;

            case 'pong':
              // Heartbeat response received
              console.log('Heartbeat response received');
              break;

            case 'keepalive':
              // Server keepalive ping
              console.log('Server keepalive received');
              break;

            case 'error':
              console.error('WebSocket server error:', message.message);
              setError(`Server error: ${message.message}`);
              setNetworkError(true);
              break;

            case 'subscription_confirmed':
              console.log('Subscription confirmed for:', message.symbols);
              break;

            default:
              console.log('Unknown WebSocket message type:', message.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          setError('Failed to parse server message');
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setWsConnected(false);
        setConnectionQuality('poor');
        stopHeartbeat();

        // Attempt to reconnect if not a manual close
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          console.log(`Scheduling reconnect attempt ${reconnectAttempts + 1}/${maxReconnectAttempts}`);
          scheduleReconnect();
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          console.error('Max reconnect attempts reached');
          setNetworkError(true);
          setConnectionQuality('offline');
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setNetworkError(true);
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setNetworkError(true);
    }
  }, [reconnectAttempts]);

  const scheduleReconnect = useCallback(() => {
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);

    reconnectTimer.current = setTimeout(() => {
      setReconnectAttempts(prev => prev + 1);
      connectWebSocket();
    }, delay);
  }, [reconnectAttempts, connectWebSocket]);

  const startHeartbeat = useCallback(() => {
    heartbeatTimer.current = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Send ping every 30 seconds
  }, []);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimer.current) {
      clearInterval(heartbeatTimer.current);
      heartbeatTimer.current = null;
    }
  }, []);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }

    stopHeartbeat();

    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect');
      ws.current = null;
    }

    setWsConnected(false);
  }, [stopHeartbeat]);

  const manualRefresh = useCallback(() => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      setIsUpdating(true);
      ws.current.send(JSON.stringify({ type: 'request_data' }));
    } else {
      // Fallback to HTTP if WebSocket is not available
      setIsUpdating(true);
      fetchMarketDataHttp();
      fetchRecommendationsHttp();
    }
  }, []);

  useEffect(() => {
    // Initialize connection
    connectWebSocket();

    // Fetch recommendations separately (not available via WebSocket)
    fetchRecommendationsHttp();

    // Fetch news on component mount and set up auto-refresh
    fetchNewsHttp();
    
    // Set loading timeout - if still loading after 5 seconds, stop loading and show data
    const loadingTimeout = setTimeout(() => {
      if (loading) {
        console.log('Loading timeout reached - showing available data');
        setLoading(false);
        // Try to fetch data via HTTP as fallback
        fetchMarketDataHttp();
      }
    }, 5000);
    
    // Auto-refresh market data every 60 seconds to reduce API calls
    const marketRefreshInterval = setInterval(() => {
      if (wsConnected) {
        manualRefresh();
      } else {
        fetchMarketDataHttp();
        fetchRecommendationsHttp();
      }
    }, 60 * 1000); // 60 seconds interval

    // Auto-refresh news every 5 minutes
    const newsRefreshInterval = setInterval(() => {
      fetchNewsHttp();
    }, 5 * 60 * 1000);

    // Cleanup on unmount
    return () => {
      disconnectWebSocket();
      clearTimeout(loadingTimeout);
      clearInterval(marketRefreshInterval);
      clearInterval(newsRefreshInterval);
    };
  }, [connectWebSocket, disconnectWebSocket]);

  useEffect(() => {
    localStorage.setItem('crypto-tracker-theme', JSON.stringify(isDarkMode));

    if (isDarkMode) {
      document.body.classList.add('dark-theme');
      document.body.classList.remove('light-theme');
    } else {
      document.body.classList.add('light-theme');
      document.body.classList.remove('dark-theme');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  // HTTP fallback functions (non-memoized to avoid dependency issues)
  const fetchMarketDataHttp = async () => {
    try {
      setNetworkError(false);
      const cryptoRequest = axios.get(`${API_BASE_URL}/api/crypto/real-prices`);
      const overviewRequest = axios.get(`${API_BASE_URL}/api/market/overview`);

      const responses = await Promise.all([
        cryptoRequest,
        overviewRequest
      ]);

      const cryptoResponse = responses[0];
      const overviewResponse = responses[1];

      setMarketData({
        prices: cryptoResponse.data,
        overview: overviewResponse.data
      });
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError('Failed to fetch market data');
      setNetworkError(true);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
      setIsUpdating(false);
    }
  };

  const fetchRecommendationsHttp = async () => {
    try {
      const portfolioResponse = await axios.get(`${API_BASE_URL}/api/portfolio/analyze`);
      setRecommendations(portfolioResponse.data);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    }
  };

  const fetchNewsHttp = async () => {
    try {
      setNewsLoading(true);
      const newsResponse = await axios.get(`${API_BASE_URL}/api/crypto/news`);
      setNews(newsResponse.data);
    } catch (err) {
      console.error('Error fetching news:', err);
    } finally {
      setNewsLoading(false);
    }
  };





  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh' }} className={isDarkMode ? 'dark-theme' : 'light-theme'}>
        <Content style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '50px'
        }}>
          <Spin size="large" />
        </Content>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout style={{ minHeight: '100vh' }} className={isDarkMode ? 'dark-theme' : 'light-theme'}>
        <Content style={{ padding: '50px' }}>
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
          />
        </Content>
      </Layout>
    );
  }

  const tabItems = [
    {
      label: '市場總覽',
      children: (
        <div>
          {/* Market Overview */}
          <MarketOverview marketData={marketData} isDarkMode={isDarkMode} />

          {/* Last Updated Info */}
          <LastUpdated marketData={marketData} isDarkMode={isDarkMode} />

          {/* Feature Enhancement Banner */}
          <FeatureBanner isDarkMode={isDarkMode} />

          {/* Crypto Prices Section Header */}
          <CryptoSection marketData={marketData} isDarkMode={isDarkMode} />

          {/* Modern Crypto Grid */}
          <CryptoGrid 
            marketData={marketData}
            previousMarketData={previousMarketData}
            isUpdating={isUpdating}
            isDarkMode={isDarkMode}
            networkError={networkError}
            manualRefresh={manualRefresh}
          />
        </div>
      ),
      key: '1',
    },
    {
      label: '投資建議',
      children: (
        <div>
          <Title level={3}>AI 投資分析</Title>
          {recommendations ? (
            <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
              {recommendations.assets && recommendations.assets.length > 0 ? (
                recommendations.assets.map((rec, index) => (
                  <Col xs={24} sm={12} md={8} key={index}>
                    <RecommendationCard rec={rec} isDarkMode={isDarkMode} />
                  </Col>
                ))
              ) : (
                <Col span={24}>
                  <Alert message="No recommendations available" type="info" showIcon />
                </Col>
              )}
            </Row>
          ) : (
            <Spin size="large" />
          )}
        </div>
      ),
      key: '2',
    },
    {
      label: '價格趨勢',
      children: (
        <div>
          <PriceTrendChart />
        </div>
      ),
      key: '3',
    },
    {
      label: '🗞️ 加密貨幣新聞',
      children: (
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px'
          }}>
            <Title level={3} style={{ margin: 0 }}>前十大加密貨幣新聞</Title>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {news?.last_updated && (
                <Text style={{
                  fontSize: '12px',
                  color: isDarkMode ? '#999999' : '#666666',
                  fontWeight: '500'
                }}>
                  最後更新: {new Date(news.last_updated).toLocaleTimeString()}
                </Text>
              )}
              <Button
                type="text"
                icon={<ReloadOutlined />}
                onClick={fetchNewsHttp}
                disabled={newsLoading}
                style={{
                  color: isDarkMode ? '#ffffff' : '#666666',
                  border: 'none'
                }}
                title="手動刷新新聞"
              />
            </div>
          </div>

          {newsLoading ? (
            <div style={{ textAlign: 'center', padding: '50px 0' }}>
              <Spin size="large" />
              <div style={{ marginTop: '16px' }}>
                <Text style={{ color: isDarkMode ? '#cccccc' : '#666666' }}>
                  正在載入最新加密貨幣新聞...
                </Text>
              </div>
            </div>
          ) : news && news.news && news.news.length > 0 ? (
            <>
              <Row gutter={[16, 24]} style={{ marginBottom: '24px' }}>
                {news.news.map((newsItem, index) => (
                  <Col xs={24} sm={12} lg={8} key={index}>
                    <NewsCard newsItem={newsItem} isDarkMode={isDarkMode} />
                  </Col>
                ))}
              </Row>

              {/* News summary footer */}
              <Card style={{
                marginTop: '24px',
                background: isDarkMode ? 'rgba(0, 0, 0, 0.6)' : 'rgba(255, 255, 255, 0.6)',
                textAlign: 'center'
              }}>
                <Text style={{
                  fontSize: '14px',
                  color: isDarkMode ? '#cccccc' : '#666666',
                  fontWeight: '500'
                }}>
                  📰 已顯示 {news.count} 條最新加密貨幣新聞 • 每5分鐘自動更新
                </Text>
                <br />
                <Text style={{
                  fontSize: '12px',
                  color: isDarkMode ? '#999999' : '#999999',
                  fontStyle: 'italic'
                }}>
                  新聞來源包括 CryptoCompare 及其他加密貨幣媒體平台
                </Text>
              </Card>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '50px 0' }}>
              <Alert
                message="暫無新聞數據"
                description="新聞服務暫時不可用，請稍後再試或點擊刷新按鈕重新載入"
                type="info"
                showIcon
                action={
                  <Button size="small" onClick={fetchNewsHttp}>
                    重新載入
                  </Button>
                }
              />
            </div>
          )}
        </div>
      ),
      key: '4',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }} className={isDarkMode ? 'dark-theme' : 'light-theme'}>
      {/* Real-time update indicator */}
      <UpdateIndicator isVisible={isUpdating} isDarkMode={isDarkMode} />

      <Header 
        isDarkMode={isDarkMode}
        toggleTheme={toggleTheme}
        wsConnected={wsConnected}
        networkError={networkError}
        isUpdating={isUpdating}
        lastUpdate={lastUpdate}
        manualRefresh={manualRefresh}
      />

      <Content style={{ padding: '50px' }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          style={{ padding: '24px' }}
        />
      </Content>
    </Layout>
  );
}

export default App;