import React from 'react';
import { Card } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PriceTrendChart = () => {
  const data = [
    { name: '1d', BTC: 48000, ETH: 3000, BNB: 220 },
    { name: '2d', BTC: 49000, ETH: 3100, BNB: 225 },
    { name: '3d', BTC: 50000, ETH: 3200, BNB: 230 },
    { name: '4d', BTC: 49500, ETH: 3150, BNB: 235 },
    { name: '5d', BTC: 50500, ETH: 3250, BNB: 240 },
  ];

  return (
    <Card title="Price Trend (Demo)">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="BTC" stroke="#f7931a" strokeWidth={2} />
          <Line type="monotone" dataKey="ETH" stroke="#627eea" strokeWidth={2} />
          <Line type="monotone" dataKey="BNB" stroke="#f3ba2f" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default PriceTrendChart;