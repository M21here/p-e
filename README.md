# 📊 Crypto P/E Tracker

> Real-time Price-to-Sales ratios for top DeFi protocols with historical charts

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Update Daily](https://img.shields.io/badge/Updates-Daily-green.svg)](https://github.com/yourusername/crypto-pe-tracker/actions)
[![Data: Free](https://img.shields.io/badge/API_Cost-$0/month-success.svg)](https://github.com/yourusername/crypto-pe-tracker)

## 🎯 Features

- 📈 **Daily Updates** - Automatic data refresh every day at 9 AM UTC
- 📊 **Historical Charts** - Track price vs P/S ratio trends over 90 days
- 💰 **100% Free** - No API costs using DefiLlama & CoinGecko free tiers
- 🎨 **Minimalistic UI** - Clean, professional design
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- ⚡ **Fast** - Static site with CDN delivery

## 🔍 Protocols Tracked

| Protocol | Chain | Category | Current P/S |
|----------|-------|----------|------------|
| **Hyperliquid** | Hyperliquid L1 | Derivatives | ~19x |
| **Pump.fun** | Solana | Launchpad | ~1.7x |
| **Ethena** | Ethereum | Stablecoin | ~3,509x |
| **Aave** | Multi-chain | Lending | ~28x |
| **MetaDAO** | Solana | DAO | ~37x |

## 🚀 Live Demo

👉 **[View Live Dashboard](https://yourusername.github.io/crypto-pe-tracker/)**

## 📸 Screenshots

### Dashboard Overview
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

### Historical Charts
![Charts](https://via.placeholder.com/800x400?text=Chart+Screenshot)

## 🛠️ Tech Stack

- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Charts:** Chart.js
- **Data Sources:** DefiLlama API, CoinGecko API
- **Database:** SQLite (local)
- **Backend:** Python 3.10+
- **Automation:** GitHub Actions / Cron

## ⚙️ Installation

### Prerequisites
- Python 3.7 or higher
- `requests` library

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-pe-tracker.git
cd crypto-pe-tracker

# Install dependencies
pip install requests

# Run the tracker
python3 crypto_pe_tracker_daily.py

# Open the dashboard
open index.html
```

## 🔄 Automated Updates

### Option 1: GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow that automatically:
- Runs daily at 9 AM UTC
- Fetches latest protocol data
- Updates `protocol_data.json`
- Commits changes back to the repo

**Setup:**
1. Fork/clone this repo
2. Enable GitHub Actions in Settings
3. GitHub Pages will auto-deploy on each commit

### Option 2: Local Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/crypto-pe-tracker && python3 crypto_pe_tracker_daily.py
```

## 📊 Data Sources

| Source | Data Provided | Update Frequency | Cost |
|--------|---------------|------------------|------|
| [DefiLlama](https://defillama.com) | Protocol revenue | Hourly | Free |
| [CoinGecko](https://coingecko.com) | Token prices & market cap | 1-5 minutes | Free (10K calls/mo) |
| SQLite | Historical snapshots | Daily | Free (local) |

**Monthly API Usage:** ~300 calls (3% of free tier)

## 📈 Understanding P/S Ratios

**Price-to-Sales (P/S) Ratio** = Market Cap ÷ Annual Revenue

### Valuation Benchmarks

- **< 10x** 🟢 Undervalued - Generating strong revenue vs market cap
- **10-30x** 🟡 Fair Value - Healthy valuation
- **30-100x** 🟠 Expensive - High expectations priced in
- **> 100x** 🔴 Overvalued - Revenue not supporting valuation

### Sector Averages

- **Launchpads:** 2-10x
- **DEXs:** 5-20x
- **Lending:** 10-50x
- **Derivatives:** 15-100x

## 🗂️ Project Structure

```
crypto-pe-tracker/
├── index.html                      # Main dashboard
├── crypto_pe_tracker_daily.py     # Data fetcher script
├── protocol_data.json             # Current data (auto-generated)
├── crypto_pe_history.db           # SQLite historical database
├── DEPLOYMENT_GUIDE.md            # Deployment instructions
├── DAILY_SETUP_GUIDE.md           # Setup documentation
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
└── .github/
    └── workflows/
        └── update-data.yml        # GitHub Actions workflow
```

## 🚀 Deployment Options

### 1. GitHub Pages (Easiest)
- Free hosting
- Automatic deployments
- Custom domain support
- [Full guide](DEPLOYMENT_GUIDE.md#option-1-github-pages)

### 2. Netlify
- One-click deploy
- Serverless functions
- Free SSL
- [Full guide](DEPLOYMENT_GUIDE.md#option-2-netlify)

### 3. Vercel
- Fast CDN
- Edge functions
- Git integration
- [Full guide](DEPLOYMENT_GUIDE.md#option-3-vercel)

### 4. Cloudflare Pages
- Unlimited bandwidth
- Global CDN
- Free tier
- [Full guide](DEPLOYMENT_GUIDE.md#option-4-cloudflare-pages)

## 🔧 Configuration

### Add More Protocols

Edit `crypto_pe_tracker_daily.py`:

```python
PROTOCOL_MAPPING = {
    "your-protocol": {
        "defillama_slug": "protocol-slug",
        "coingecko_id": "token-id",
        "name": "Protocol Name",
        "chain": "Blockchain",
        "category": "Category"
    }
}
```

Find slugs:
- DefiLlama: https://defillama.com/protocols
- CoinGecko: https://coingecko.com/en/coins/[search]

### Customize Update Frequency

GitHub Actions `.github/workflows/update-data.yml`:
```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
```

## 📊 Database Schema

```sql
CREATE TABLE daily_snapshots (
    date TEXT,              -- YYYY-MM-DD
    protocol TEXT,          -- Protocol name
    price REAL,            -- Token price USD
    market_cap REAL,       -- Market cap USD
    annual_revenue REAL,   -- Annualized revenue
    ps_circulating REAL,   -- P/S ratio
    valuation TEXT         -- Undervalued/Fair/Expensive
);
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution:
- [ ] Add more protocols
- [ ] Improve chart visualization
- [ ] Add export to CSV feature
- [ ] Create mobile app
- [ ] Add email alerts
- [ ] Improve documentation

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/crypto-pe-tracker.git

# Create branch
git checkout -b feature/your-feature

# Make changes and test
python3 crypto_pe_tracker_daily.py

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DefiLlama](https://defillama.com) - Protocol revenue data
- [CoinGecko](https://coingecko.com) - Token market data
- [Chart.js](https://chartjs.org) - Beautiful charts
- DeFi community for inspiration

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/crypto-pe-tracker/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/crypto-pe-tracker/discussions)
- **Documentation:** See [DAILY_SETUP_GUIDE.md](DAILY_SETUP_GUIDE.md)

## ⚠️ Disclaimer

This tool is for informational purposes only. It does not constitute financial advice. Always do your own research before making investment decisions.

## 📈 Roadmap

- [x] Basic P/S tracking for 5 protocols
- [x] Historical charts
- [x] Automated daily updates
- [x] Responsive design
- [ ] Add 10+ more protocols
- [ ] Email alerts for threshold breaches
- [ ] Export to CSV/PDF
- [ ] Compare multiple protocols
- [ ] Add revenue growth metrics
- [ ] Mobile app (React Native)
- [ ] API endpoint for public access
- [ ] Community protocol suggestions

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/crypto-pe-tracker&type=Date)](https://star-history.com/#yourusername/crypto-pe-tracker&Date)

---

Made with ❤️ by [Your Name](https://github.com/yourusername)

**If you find this useful, consider giving it a ⭐!**
