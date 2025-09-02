import React from 'react';
import { Layout, Typography, Switch, Button } from 'antd';
import { SunOutlined, MoonOutlined, WifiOutlined, DisconnectOutlined, SyncOutlined, ReloadOutlined } from '@ant-design/icons';
import './Header.css';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = ({ 
  isDarkMode, 
  toggleTheme, 
  wsConnected, 
  networkError, 
  isUpdating, 
  lastUpdate, 
  manualRefresh 
}) => {
  return (
    <AntHeader style={{
      background: isDarkMode ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      padding: '0 50px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <Title level={2} className="header-title" style={{ margin: '14px 0' }}>
          📊 Crypto Investment Tracker
        </Title>

        {/* Enhanced Connection Status Indicator */}
        <div className={`network-status-indicator ${wsConnected ? 'connected' : networkError ? 'disconnected' : 'connecting'
          }`}>
          {wsConnected ? (
            <>
              <WifiOutlined />
              <span>已連線</span>
            </>
          ) : networkError ? (
            <>
              <DisconnectOutlined />
              <span>離線</span>
            </>
          ) : (
            <>
              <SyncOutlined spin />
              <span>連線中</span>
            </>
          )}
        </div>

        {/* Data Update Indicator */}
        {isUpdating && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <SyncOutlined spin style={{ color: '#1890ff', fontSize: '14px' }} />
            <span style={{
              fontSize: '11px',
              color: '#1890ff',
              fontWeight: '600',
              textTransform: 'uppercase'
            }}>
              更新中...
            </span>
          </div>
        )}

        {/* Last Update Time */}
        {lastUpdate && (
          <span style={{
            fontSize: '11px',
            color: isDarkMode ? '#999999' : '#666666',
            fontWeight: '500'
          }}>
            更新: {lastUpdate.toLocaleTimeString()}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Manual Refresh Button */}
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={manualRefresh}
          disabled={isUpdating}
          style={{
            color: isDarkMode ? '#ffffff' : '#666666',
            border: 'none'
          }}
          title="手動刷新"
        />

        {/* Network Status Icon */}
        {wsConnected ? (
          <WifiOutlined style={{
            color: '#52c41a',
            fontSize: '16px'
          }} title="已連接" />
        ) : (
          <DisconnectOutlined style={{
            color: '#ff4d4f',
            fontSize: '16px'
          }} title="未連接" />
        )}

        {/* Theme Toggle */}
        <SunOutlined style={{
          color: !isDarkMode ? '#1890ff' : '#8c8c8c',
          fontSize: '16px'
        }} />
        <Switch
          checked={isDarkMode}
          onChange={toggleTheme}
          checkedChildren={<MoonOutlined />}
          unCheckedChildren={<SunOutlined />}
          style={{
            background: isDarkMode ? '#1890ff' : '#f0f0f0'
          }}
        />
        <MoonOutlined style={{
          color: isDarkMode ? '#1890ff' : '#8c8c8c',
          fontSize: '16px'
        }} />
      </div>
    </AntHeader>
  );
};

export default Header;