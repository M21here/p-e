#!/bin/bash

# 🚀 One-Click Deploy Script for Crypto P/E Tracker
# This script helps you deploy to various platforms

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🚀 Crypto P/E Tracker - Deployment Helper         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.7+${NC}"
    exit 1
fi

echo -e "${BLUE}Select deployment platform:${NC}"
echo ""
echo "  1) GitHub Pages (Recommended - Free)"
echo "  2) Netlify (Easy - Free)"
echo "  3) Vercel (Fast - Free)"
echo "  4) Cloudflare Pages (Unlimited Bandwidth - Free)"
echo "  5) Generate initial data only (no deploy)"
echo "  6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}📦 Preparing for GitHub Pages...${NC}"
        
        # Run tracker to generate initial data
        echo -e "${YELLOW}⏳ Generating initial data...${NC}"
        python3 crypto_pe_tracker_daily.py
        
        # Initialize git if not already
        if [ ! -d .git ]; then
            echo -e "${YELLOW}📝 Initializing git repository...${NC}"
            git init
            git add .
            git commit -m "Initial commit: Crypto P/E Tracker"
        fi
        
        echo ""
        echo -e "${GREEN}✅ Repository prepared!${NC}"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Create a new repository on GitHub"
        echo "2. Run these commands:"
        echo ""
        echo -e "${YELLOW}   git remote add origin https://github.com/YOUR_USERNAME/crypto-pe-tracker.git${NC}"
        echo -e "${YELLOW}   git branch -M main${NC}"
        echo -e "${YELLOW}   git push -u origin main${NC}"
        echo ""
        echo "3. Go to GitHub repository → Settings → Pages"
        echo "4. Source: 'Deploy from branch' → Branch: 'main' → '/ (root)' → Save"
        echo ""
        echo -e "${GREEN}🎉 Your site will be live at:${NC}"
        echo "   https://YOUR_USERNAME.github.io/crypto-pe-tracker/"
        ;;
        
    2)
        echo ""
        echo -e "${GREEN}📦 Preparing for Netlify...${NC}"
        
        # Check if Netlify CLI is installed
        if ! command -v netlify &> /dev/null; then
            echo -e "${YELLOW}⚠️  Netlify CLI not found.${NC}"
            echo -e "${BLUE}Installing Netlify CLI...${NC}"
            npm install -g netlify-cli || {
                echo -e "${RED}❌ Failed to install Netlify CLI. Install Node.js first.${NC}"
                exit 1
            }
        fi
        
        # Run tracker
        echo -e "${YELLOW}⏳ Generating initial data...${NC}"
        python3 crypto_pe_tracker_daily.py
        
        # Login and deploy
        echo -e "${BLUE}🔐 Logging in to Netlify...${NC}"
        netlify login
        
        echo -e "${BLUE}🚀 Deploying to Netlify...${NC}"
        netlify deploy --prod
        
        echo ""
        echo -e "${GREEN}✅ Deployed successfully!${NC}"
        ;;
        
    3)
        echo ""
        echo -e "${GREEN}📦 Preparing for Vercel...${NC}"
        
        # Check if Vercel CLI is installed
        if ! command -v vercel &> /dev/null; then
            echo -e "${YELLOW}⚠️  Vercel CLI not found.${NC}"
            echo -e "${BLUE}Installing Vercel CLI...${NC}"
            npm install -g vercel || {
                echo -e "${RED}❌ Failed to install Vercel CLI. Install Node.js first.${NC}"
                exit 1
            }
        fi
        
        # Run tracker
        echo -e "${YELLOW}⏳ Generating initial data...${NC}"
        python3 crypto_pe_tracker_daily.py
        
        # Deploy
        echo -e "${BLUE}🚀 Deploying to Vercel...${NC}"
        vercel --prod
        
        echo ""
        echo -e "${GREEN}✅ Deployed successfully!${NC}"
        ;;
        
    4)
        echo ""
        echo -e "${GREEN}📦 Preparing for Cloudflare Pages...${NC}"
        
        # Check if Wrangler is installed
        if ! command -v wrangler &> /dev/null; then
            echo -e "${YELLOW}⚠️  Wrangler CLI not found.${NC}"
            echo -e "${BLUE}Installing Wrangler...${NC}"
            npm install -g wrangler || {
                echo -e "${RED}❌ Failed to install Wrangler. Install Node.js first.${NC}"
                exit 1
            }
        fi
        
        # Run tracker
        echo -e "${YELLOW}⏳ Generating initial data...${NC}"
        python3 crypto_pe_tracker_daily.py
        
        # Login and deploy
        echo -e "${BLUE}🔐 Logging in to Cloudflare...${NC}"
        wrangler login
        
        echo -e "${BLUE}🚀 Deploying to Cloudflare Pages...${NC}"
        wrangler pages publish . --project-name=crypto-pe-tracker
        
        echo ""
        echo -e "${GREEN}✅ Deployed successfully!${NC}"
        ;;
        
    5)
        echo ""
        echo -e "${GREEN}📊 Generating initial data...${NC}"
        python3 crypto_pe_tracker_daily.py
        echo ""
        echo -e "${GREEN}✅ Data generated successfully!${NC}"
        echo -e "${BLUE}Files created:${NC}"
        echo "  - protocol_data.json (today's data)"
        echo "  - crypto_pe_history.db (database)"
        echo ""
        echo -e "${YELLOW}💡 Tip: Open index.html in your browser to view the dashboard${NC}"
        ;;
        
    6)
        echo ""
        echo -e "${BLUE}👋 Goodbye!${NC}"
        exit 0
        ;;
        
    *)
        echo ""
        echo -e "${RED}❌ Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    ✨ Deployment Helper Complete! ✨${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📚 For detailed deployment docs, see: DEPLOYMENT_GUIDE.md${NC}"
echo -e "${BLUE}❓ Need help? Check out: README.md${NC}"
echo ""
