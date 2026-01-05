#!/usr/bin/env python3
"""
Crypto P/E Tracker with Historical Data
Daily updates with SQLite database for tracking P/E over time
100% FREE - No API costs
"""

import requests
import sqlite3
import time
from datetime import datetime
import json
import os

class CryptoPETrackerDaily:
    def __init__(self, db_path="crypto_pe_history.db"):
        self.defillama_base = "https://api.llama.fi"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for historical tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for daily snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                protocol TEXT NOT NULL,
                price REAL,
                market_cap REAL,
                fdv REAL,
                daily_revenue REAL,
                revenue_7d REAL,
                revenue_30d REAL,
                annual_revenue REAL,
                ps_circulating REAL,
                ps_fdv REAL,
                valuation TEXT,
                timestamp TEXT,
                UNIQUE(date, protocol)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {self.db_path}")
    
    def get_protocol_revenue(self, protocol_slug):
        """Fetch revenue data from DefiLlama (updates hourly)"""
        if protocol_slug is None:
            return None
            
        url = f"{self.defillama_base}/summary/fees/{protocol_slug}"
        params = {"dataType": "dailyRevenue"}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Calculate annualized revenue from 30-day average
            revenue_30d = data.get("total30d", 0)
            annual_revenue = (revenue_30d / 30) * 365
            
            return {
                "daily_revenue": data.get("total24h", 0),
                "revenue_7d": data.get("total7d", 0),
                "revenue_30d": revenue_30d,
                "annual_revenue": annual_revenue,
                "change_1d": data.get("change_1d", 0)
            }
        except Exception as e:
            print(f"  ✗ Error fetching {protocol_slug} revenue: {e}")
            return None
    
    def get_market_cap(self, coin_id):
        """Fetch market cap data from CoinGecko (updates every 1-5 minutes)"""
        url = f"{self.coingecko_base}/coins/{coin_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get("market_data", {})
            
            return {
                "price": market_data.get("current_price", {}).get("usd", 0),
                "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                "fdv": market_data.get("fully_diluted_valuation", {}).get("usd", 0),
                "circulating_supply": market_data.get("circulating_supply", 0),
                "total_supply": market_data.get("total_supply", 0),
                "max_supply": market_data.get("max_supply", 0)
            }
        except Exception as e:
            print(f"  ✗ Error fetching {coin_id} market cap: {e}")
            return None
    
    def calculate_pe_ratios(self, market_cap, fdv, annual_revenue):
        """Calculate P/S ratios"""
        if annual_revenue == 0 or annual_revenue is None:
            return {
                "ps_circulating": None,
                "ps_fdv": None,
                "interpretation": "No revenue"
            }
        
        ps_circ = market_cap / annual_revenue
        ps_fdv = fdv / annual_revenue if fdv else None
        
        # Interpretation
        if ps_circ < 10:
            interpretation = "Undervalued"
        elif ps_circ < 30:
            interpretation = "Fair value"
        elif ps_circ < 100:
            interpretation = "Expensive"
        else:
            interpretation = "Extremely overvalued"
        
        return {
            "ps_circulating": round(ps_circ, 2),
            "ps_fdv": round(ps_fdv, 2) if ps_fdv else None,
            "interpretation": interpretation
        }
    
    def save_daily_snapshot(self, protocol_key, data):
        """Save daily snapshot to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_snapshots 
                (date, protocol, price, market_cap, fdv, daily_revenue, 
                 revenue_7d, revenue_30d, annual_revenue, ps_circulating, 
                 ps_fdv, valuation, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                today,
                data['name'],
                data['price'],
                data['market_cap'],
                data['fdv'],
                data['daily_revenue'],
                data.get('revenue_7d', 0),
                data.get('revenue_30d', 0),
                data['annual_revenue'],
                data['ps_circulating'],
                data['ps_fdv'],
                data['valuation'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            print(f"  ✓ Saved to database")
        except Exception as e:
            print(f"  ✗ Database error: {e}")
        finally:
            conn.close()
    
    def get_historical_data(self, protocol_name, days=30):
        """Get historical data for a protocol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, price, ps_circulating, annual_revenue, valuation
            FROM daily_snapshots
            WHERE protocol = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (protocol_name, days))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'date': row[0],
            'price': row[1],
            'ps_circulating': row[2],
            'annual_revenue': row[3],
            'valuation': row[4]
        } for row in reversed(rows)]
    
    def fetch_protocol_data(self, protocol_key, manual_revenue=None):
        """Fetch complete data for a protocol"""
        protocol = PROTOCOL_MAPPING[protocol_key]
        
        print(f"\n📊 Fetching {protocol['name']}...")
        
        # Get market cap data
        market_data = self.get_market_cap(protocol["coingecko_id"])
        if not market_data:
            return None
        print(f"  ✓ Price: ${market_data['price']:.4f}")
        
        # Get revenue data
        if manual_revenue:
            revenue_data = {
                "annual_revenue": manual_revenue,
                "daily_revenue": manual_revenue / 365,
                "revenue_30d": (manual_revenue / 365) * 30,
                "revenue_7d": (manual_revenue / 365) * 7
            }
            print(f"  ✓ Revenue: ${revenue_data['annual_revenue']/1e6:.2f}M (manual)")
        else:
            revenue_data = self.get_protocol_revenue(protocol["defillama_slug"])
            if not revenue_data:
                return None
            print(f"  ✓ Revenue: ${revenue_data['annual_revenue']/1e6:.2f}M")
        
        # Calculate P/S ratios
        pe_ratios = self.calculate_pe_ratios(
            market_data["market_cap"],
            market_data["fdv"],
            revenue_data["annual_revenue"]
        )
        print(f"  ✓ P/S Ratio: {pe_ratios['ps_circulating']}x ({pe_ratios['interpretation']})")
        
        data = {
            "name": protocol["name"],
            "chain": protocol["chain"],
            "category": protocol["category"],
            "price": market_data["price"],
            "market_cap": market_data["market_cap"],
            "fdv": market_data["fdv"],
            "circulating_supply": market_data["circulating_supply"],
            "annual_revenue": revenue_data["annual_revenue"],
            "daily_revenue": revenue_data.get("daily_revenue", 0),
            "revenue_30d": revenue_data.get("revenue_30d", 0),
            "revenue_7d": revenue_data.get("revenue_7d", 0),
            "ps_circulating": pe_ratios["ps_circulating"],
            "ps_fdv": pe_ratios["ps_fdv"],
            "valuation": pe_ratios["interpretation"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to database
        self.save_daily_snapshot(protocol_key, data)
        
        # Add historical data
        data['historical'] = self.get_historical_data(protocol['name'], days=90)
        
        return data
    
    def fetch_all_protocols(self):
        """Fetch data for all 5 protocols"""
        results = []
        
        print("\n" + "="*60)
        print("DAILY CRYPTO P/E UPDATE")
        print("="*60)
        
        for key in PROTOCOL_MAPPING.keys():
            manual_rev = PROTOCOL_MAPPING[key].get("manual_revenue")
            data = self.fetch_protocol_data(key, manual_rev)
            
            if data:
                results.append(data)
            
            # Rate limiting
            time.sleep(1.5)
        
        return results
    
    def export_to_json(self, data, filename="protocol_data.json"):
        """Export current data to JSON for dashboard"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Data exported to {filename}")
    
    def print_summary(self, data):
        """Print formatted summary"""
        print("\n" + "="*80)
        print("📈 DAILY SUMMARY")
        print("="*80)
        
        # Sort by P/S ratio
        sorted_data = sorted(
            data, 
            key=lambda x: x["ps_circulating"] if x["ps_circulating"] else float('inf')
        )
        
        for protocol in sorted_data:
            print(f"\n{protocol['name']} ({protocol['chain']})")
            print(f"  💰 Price: ${protocol['price']:,.4f}")
            print(f"  📊 Market Cap: ${protocol['market_cap']/1e9:.2f}B")
            print(f"  💵 Annual Revenue: ${protocol['annual_revenue']/1e6:.2f}M")
            print(f"  📈 P/S Ratio: {protocol['ps_circulating']}x" if protocol['ps_circulating'] else "  📈 P/S Ratio: N/A")
            print(f"  🎯 Valuation: {protocol['valuation']}")
            
            # Historical comparison
            if protocol.get('historical') and len(protocol['historical']) > 0:
                first = protocol['historical'][0]
                if first['ps_circulating']:
                    change = protocol['ps_circulating'] - first['ps_circulating']
                    print(f"  📉 P/S Change (vs {first['date']}): {change:+.2f}x")
        
        print("\n" + "="*80)


# Protocol mapping
PROTOCOL_MAPPING = {
    "hyperliquid": {
        "defillama_slug": "hyperliquid",
        "coingecko_id": "hyperliquid",
        "name": "Hyperliquid",
        "chain": "Hyperliquid L1",
        "category": "Derivatives"
    },
    "pump": {
        "defillama_slug": None,
        "coingecko_id": "pump-fun",
        "name": "Pump.fun",
        "chain": "Solana",
        "category": "Launchpad",
        "manual_revenue": 492000000  # $492M annual
    },
    "ethena": {
        "defillama_slug": "ethena",
        "coingecko_id": "ethena",
        "name": "Ethena",
        "chain": "Ethereum",
        "category": "Stablecoin"
    },
    "aave": {
        "defillama_slug": "aave",
        "coingecko_id": "aave",
        "name": "Aave",
        "chain": "Multi-chain",
        "category": "Lending"
    },
    "metadao": {
        "defillama_slug": "metadao",
        "coingecko_id": "meta-2",
        "name": "MetaDAO",
        "chain": "Solana",
        "category": "DAO"
    }
}


if __name__ == "__main__":
    tracker = CryptoPETrackerDaily()
    
    # Fetch all protocol data
    results = tracker.fetch_all_protocols()
    
    # Print summary
    tracker.print_summary(results)
    
    # Export for dashboard
    tracker.export_to_json(results)
    
    print("\n✅ Done! Open dashboard.html to view charts.")
    print(f"📁 Historical data stored in: {tracker.db_path}")
