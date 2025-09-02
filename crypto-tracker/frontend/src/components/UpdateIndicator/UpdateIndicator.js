import React from 'react';
import { SyncOutlined } from '@ant-design/icons';
import './UpdateIndicator.css';

const UpdateIndicator = ({ isVisible, isDarkMode }) => (
  isVisible ? (
    <div className={`update-indicator ${isDarkMode ? 'dark' : 'light'}`}>
      <SyncOutlined spin style={{ fontSize: '14px' }} />
      <span>ÊBÙ∞-...</span>
    </div>
  ) : null
);

export default UpdateIndicator;