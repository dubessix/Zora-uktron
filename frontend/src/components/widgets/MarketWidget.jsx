import React, { useState, useEffect } from 'react';

/**
 * MarketWidget — real crypto prices (Set B: no fake BTC).
 * Fetches live prices from the free CoinGecko API.
 */
export default function MarketWidget() {
  const [coins, setCoins] = useState([]);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(
          "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,solana&vs_currencies=usd&include_24hr_change=true"
        );
        if (!res.ok) throw new Error();
        const data = await res.json();
        const map = {
          bitcoin: "BTC", ethereum: "ETH", binancecoin: "BNB", solana: "SOL"
        };
        const list = Object.entries(data).map(([id, v]) => ({
          symbol: `${map[id] || id.toUpperCase()}/USD`,
          price: `$${v.usd.toLocaleString(undefined, { maximumFractionDigits: 2 })}`,
          change: v.usd_24h_change == null
            ? "Unavailable"
            : `${v.usd_24h_change > 0 ? "+" : ""}${v.usd_24h_change.toFixed(2)}%`,
          up: v.usd_24h_change == null ? null : v.usd_24h_change >= 0
        }));
        setCoins(list);
        setStatus("ok");
      } catch (err) { setStatus("offline"); } 
    };
    load();
  }, []);

  return (
    <div className="space-y-2 font-mono text-[10px]">
      <div className="flex justify-between text-[7px] uppercase tracking-widest text-white/40 font-bold">
        <span>Live Market</span>
        <span className={status === "offline" ? "text-rose-400" : "text-emerald-400"}>
          {status === "loading" ? "loading…" : status === "offline" ? "offline" : "LIVE"}
        </span>
      </div>
      {status !== "ok" && coins.length === 0 && (
        <p className="text-[9px] text-white/30">{status === "offline" ? "Could not fetch live prices." : "Loading…"}</p>
      )}
      <div className="space-y-1.5">
        {coins.map((c, i) => (
          <div key={i} className="flex items-center justify-between border border-white/5 bg-white/[0.01] p-2 rounded-sm">
            <span className="text-[#F5F5F7]">{c.symbol}</span>
            <span className="flex items-center gap-2">
              <span className="text-white/70">{c.price}</span>
              <span className={c.up == null ? "text-white/40" : c.up ? "text-emerald-400" : "text-rose-400"}>{c.change}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
