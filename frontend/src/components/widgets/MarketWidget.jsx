import React from 'react';

/**
 * MarketWidget Content Component
 * Renders live stock prices, cryptocurrency indexes, and personal watchlists.
 */
export default function MarketWidget() {
  const assets = [
    { symbol: "BTC/USD", price: "$64,250.00", change: "+4.12%", up: true },
    { symbol: "TSLA", price: "$182.42", change: "-2.35%", up: false },
    { symbol: "AAPL", price: "$174.12", change: "+0.85%", up: true }
  ];

  return (
    <div className="space-y-3 font-mono text-[10px]">
      
      {/* Header index */}
      <div className="flex justify-between items-center bg-white/5 p-2 rounded-sm text-[8px] text-[#8B8B96] uppercase tracking-wider font-bold">
        <span>Active Watchlist</span>
        <span>Market Index</span>
      </div>

      {/* Assets loop */}
      <div className="space-y-1.5">
        {assets.map((asset, idx) => (
          <div 
            key={idx}
            className="flex justify-between items-center bg-white/[0.01] border border-white/5 p-2 rounded-sm"
          >
            <div>
              <span className="font-bold text-[#F5F5F7]">{asset.symbol}</span>
              <span className="block text-[8px] text-white/30 mt-0.5">{asset.price}</span>
            </div>
            <span className={`text-[8px] px-2 py-0.5 rounded-sm font-bold tracking-widest ${
              asset.up ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
            }`}>
              {asset.change}
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}
