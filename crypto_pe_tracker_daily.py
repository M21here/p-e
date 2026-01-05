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
import logging
from typing import Optional, Dict, Any

class CryptoPETrackerDaily:
    def __init__(self, db_path="crypto_pe_history.db"):
        self.defillama_base = "https://api.llama.fi"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.db_path = db_path
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.setup_logging()
        self.init_database()

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crypto_pe_tracker.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """Initialize SQLite database for historical tracking"""
        try:
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
            self.logger.info(f"✓ Database initialized: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def make_request_with_retry(self, url: str, params: Optional[Dict] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries} for {url}")
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limit
                    self.logger.warning(f"Rate limited, waiting {self.retry_delay * (attempt + 1)}s...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"HTTP error {response.status_code}: {e}")
                    break
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error on attempt {attempt + 1}: {e}")

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))

        return None
    
    def get_protocol_revenue(self, protocol_slug: Optional[str]) -> Optional[Dict[str, float]]:
        """Fetch revenue data from DefiLlama (updates hourly)"""
        if protocol_slug is None:
            return None

        url = f"{self.defillama_base}/summary/fees/{protocol_slug}"
        params = {"dataType": "dailyRevenue"}

        data = self.make_request_with_retry(url, params)
        if not data:
            self.logger.error(f"Failed to fetch revenue for {protocol_slug}")
            return None

        try:
            # Validate data structure
            if not isinstance(data, dict):
                self.logger.error(f"Invalid data format for {protocol_slug}")
                return None

            # Calculate annualized revenue from 30-day average
            revenue_30d = float(data.get("total30d", 0))
            annual_revenue = (revenue_30d / 30) * 365 if revenue_30d > 0 else 0

            return {
                "daily_revenue": float(data.get("total24h", 0)),
                "revenue_7d": float(data.get("total7d", 0)),
                "revenue_30d": revenue_30d,
                "annual_revenue": annual_revenue,
                "change_1d": float(data.get("change_1d", 0))
            }
        except (ValueError, TypeError) as e:
            self.logger.error(f"Data validation error for {protocol_slug}: {e}")
            return None
    
    def get_market_cap(self, coin_id: str) -> Optional[Dict[str, float]]:
        """Fetch market cap data from CoinGecko (updates every 1-5 minutes)"""
        url = f"{self.coingecko_base}/coins/{coin_id}"

        data = self.make_request_with_retry(url)
        if not data:
            self.logger.error(f"Failed to fetch market data for {coin_id}")
            return None

        try:
            # Validate data structure
            if not isinstance(data, dict):
                self.logger.error(f"Invalid data format for {coin_id}")
                return None

            market_data = data.get("market_data", {})
            if not market_data:
                self.logger.error(f"No market data for {coin_id}")
                return None

            # Get values with proper fallbacks
            price = float(market_data.get("current_price", {}).get("usd", 0))
            market_cap = float(market_data.get("market_cap", {}).get("usd", 0))
            fdv = float(market_data.get("fully_diluted_valuation", {}).get("usd", 0))
            circulating_supply = float(market_data.get("circulating_supply") or 0)

            # Fix for tokens with zero circulating supply - use FDV as market cap
            if market_cap == 0 and fdv > 0:
                self.logger.warning(f"{coin_id} has zero market cap, using FDV instead")
                market_cap = fdv

            return {
                "price": price,
                "market_cap": market_cap,
                "fdv": fdv,
                "circulating_supply": circulating_supply,
                "total_supply": float(market_data.get("total_supply") or 0),
                "max_supply": float(market_data.get("max_supply") or 0)
            }
        except (ValueError, TypeError, AttributeError) as e:
            self.logger.error(f"Data validation error for {coin_id}: {e}")
            return None
    
    def calculate_pe_ratios(self, market_cap: float, fdv: float, annual_revenue: float) -> Dict[str, Any]:
        """Calculate P/S ratios"""
        if annual_revenue == 0 or annual_revenue is None:
            self.logger.warning("Cannot calculate P/S ratio: no revenue data")
            return {
                "ps_circulating": None,
                "ps_fdv": None,
                "interpretation": "No revenue"
            }

        if market_cap == 0 or market_cap is None:
            self.logger.warning("Cannot calculate P/S ratio: no market cap data")
            return {
                "ps_circulating": None,
                "ps_fdv": round(fdv / annual_revenue, 2) if fdv and fdv > 0 else None,
                "interpretation": "No market cap"
            }

        ps_circ = market_cap / annual_revenue
        ps_fdv = fdv / annual_revenue if fdv and fdv > 0 else None

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
    
    def save_daily_snapshot(self, protocol_key: str, data: Dict[str, Any]) -> bool:
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
            self.logger.info(f"  ✓ Saved {data['name']} to database")
            return True
        except Exception as e:
            self.logger.error(f"  ✗ Database error for {data['name']}: {e}")
            return False
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
    
    def fetch_protocol_data(self, protocol_key: str, manual_revenue: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Fetch complete data for a protocol"""
        protocol = PROTOCOL_MAPPING[protocol_key]

        self.logger.info(f"\n📊 Fetching {protocol['name']}...")

        # Get market cap data
        market_data = self.get_market_cap(protocol["coingecko_id"])
        if not market_data:
            self.logger.error(f"Failed to get market data for {protocol['name']}")
            return None
        self.logger.info(f"  ✓ Price: ${market_data['price']:.4f}")

        # Get revenue data
        if manual_revenue:
            revenue_data = {
                "annual_revenue": manual_revenue,
                "daily_revenue": manual_revenue / 365,
                "revenue_30d": (manual_revenue / 365) * 30,
                "revenue_7d": (manual_revenue / 365) * 7
            }
            self.logger.info(f"  ✓ Revenue: ${revenue_data['annual_revenue']/1e6:.2f}M (manual)")
        else:
            revenue_data = self.get_protocol_revenue(protocol["defillama_slug"])
            if not revenue_data:
                self.logger.error(f"Failed to get revenue data for {protocol['name']}")
                return None
            self.logger.info(f"  ✓ Revenue: ${revenue_data['annual_revenue']/1e6:.2f}M")

        # Calculate P/S ratios
        pe_ratios = self.calculate_pe_ratios(
            market_data["market_cap"],
            market_data["fdv"],
            revenue_data["annual_revenue"]
        )

        ps_display = f"{pe_ratios['ps_circulating']}x" if pe_ratios['ps_circulating'] else "N/A"
        self.logger.info(f"  ✓ P/S Ratio: {ps_display} ({pe_ratios['interpretation']})")

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
    
    def fetch_all_protocols(self) -> list:
        """Fetch data for all protocols"""
        results = []

        self.logger.info("\n" + "="*60)
        self.logger.info("DAILY CRYPTO P/E UPDATE")
        self.logger.info("="*60)

        successful = 0
        failed = 0

        for key in PROTOCOL_MAPPING.keys():
            manual_rev = PROTOCOL_MAPPING[key].get("manual_revenue")
            data = self.fetch_protocol_data(key, manual_rev)

            if data:
                results.append(data)
                successful += 1
            else:
                failed += 1
                self.logger.warning(f"Skipping {PROTOCOL_MAPPING[key]['name']} due to errors")

            # Rate limiting - avoid hitting API limits
            time.sleep(1.5)

        self.logger.info(f"\n✓ Successfully fetched {successful} protocols")
        if failed > 0:
            self.logger.warning(f"✗ Failed to fetch {failed} protocols")

        return results
    
    def export_to_json(self, data: list, filename: str = "protocol_data.json") -> bool:
        """Export current data to JSON for dashboard"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"\n✓ Data exported to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export data to {filename}: {e}")
            return False
    
    def print_summary(self, data: list):
        """Print formatted summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("📈 DAILY SUMMARY")
        self.logger.info("="*80)

        # Sort by P/S ratio
        sorted_data = sorted(
            data,
            key=lambda x: x["ps_circulating"] if x["ps_circulating"] else float('inf')
        )

        for protocol in sorted_data:
            self.logger.info(f"\n{protocol['name']} ({protocol['chain']})")
            self.logger.info(f"  💰 Price: ${protocol['price']:,.4f}")

            # Handle market cap display
            if protocol['market_cap'] > 0:
                self.logger.info(f"  📊 Market Cap: ${protocol['market_cap']/1e9:.2f}B")
            else:
                self.logger.info(f"  📊 Market Cap: N/A (FDV: ${protocol['fdv']/1e9:.2f}B)")

            self.logger.info(f"  💵 Annual Revenue: ${protocol['annual_revenue']/1e6:.2f}M")

            if protocol['ps_circulating']:
                self.logger.info(f"  📈 P/S Ratio: {protocol['ps_circulating']}x")
            else:
                self.logger.info(f"  📈 P/S Ratio: N/A")

            self.logger.info(f"  🎯 Valuation: {protocol['valuation']}")

            # Historical comparison
            if protocol.get('historical') and len(protocol['historical']) > 1:
                first = protocol['historical'][0]
                if first.get('ps_circulating') and protocol['ps_circulating']:
                    change = protocol['ps_circulating'] - first['ps_circulating']
                    self.logger.info(f"  📉 P/S Change (vs {first['date']}): {change:+.2f}x")

        self.logger.info("\n" + "="*80)


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
    try:
        tracker = CryptoPETrackerDaily()

        # Fetch all protocol data
        results = tracker.fetch_all_protocols()

        if not results:
            tracker.logger.error("No protocols fetched successfully. Exiting.")
            exit(1)

        # Print summary
        tracker.print_summary(results)

        # Export for dashboard
        if tracker.export_to_json(results):
            tracker.logger.info("\n✅ Done! Open index.html to view charts.")
            tracker.logger.info(f"📁 Historical data stored in: {tracker.db_path}")
            tracker.logger.info(f"📊 Logs saved to: crypto_pe_tracker.log")
        else:
            tracker.logger.error("Failed to export data. Check logs.")
            exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
