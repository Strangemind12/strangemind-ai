# Strangemind AI 🤖⚡

**Strangemind AI** is a cutting-edge WhatsApp Business AI bot designed for advanced user engagement, entertainment, and passive earning. Powered by Gupshup’s WhatsApp API, OpenAI’s language models, and integrated with a unique game economy and movie streaming features, this bot brings an interactive digital experience to WhatsApp users worldwide.

---

## Features 🚀

- **Intelligent Chat & Content Generation**: Powered by OpenAI GPT models for text and story generation.
- **Movie Search & Streaming**: Search for movies, watch trailers, and get streaming/download links scraped from multiple sources.
- **Spam & Abuse Detection**: Keep the community clean and safe.
- **Admin Controls**: Manage premium features, user access, and bot settings remotely.

---

## Getting Started 🏁

### Prerequisites

- Node.js (v16+ recommended)
- MongoDB (Atlas or local)
- Gupshup WhatsApp Business API account and API key
- OpenAI API key (optional, for advanced AI features)
- Koyeb or another scraping service for movie search (optional)
- YouTube API key (optional, for trailers)

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/Strangemind12/strangemind-ai.git
   cd strangemind-ai

2. Install dependencies:

npm install


3. Configure environment variables:



Create a .env file in the root directory and add:

GUPSHUP_API_KEY=your_gupshup_api_key
BOT_NAME=Strangemind AI
OPENAI_API_KEY=your_openai_key
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/strangemindDB
ADMIN_PHONE=+234youradminnumber

# Feature toggles
ENABLE_PREMIUM=true
ENABLE_GAMIFIED_MODE=true
ENABLE_MOVIE_ENGINE=true
ENABLE_SPAM_FILTER=true
WELCOME_ON_MENTION=true
ENABLE_REFERRAL_SYSTEM=true

# Movie engine specific
MOVIE_SCRAPER_API=https://your-koyeb-api.com/search
YOUTUBE_API_KEY=your_youtube_api_key

# Game settings
GAME_XP_PER_MESSAGE=5
GAME_COIN_PER_MESSAGE=2
GAME_DAILY_COIN_LIMIT=500
GAME_BOX_NAME=Strangemind Vault
GAME_MIN_WITHDRAWAL=1000
GAME_WITHDRAWAL_ENABLED=true
GAME_WITHDRAWAL_METHOD=airtime
GAME_WITHDRAWAL_WEBHOOK=https://your-server.com/api/withdraw

# Referral bonuses
REFERRAL_BONUS_REFERRER=100
REFERRAL_BONUS_NEW_USER=50


---

Running the Bot

npm start

The bot will connect to WhatsApp via Gupshup API, initialize the database, and start listening for messages.


---

Usage 📱

Chat with the bot to earn XP and coins.

Use /movie <movie name> to search and stream movies.

Use /vault or /mybox to check your coin balance and XP.

Use /withdraw to cash out your coins (if enabled).

Use /refer to get your referral code and invite friends.

Use /top to see the leaderboard.



---

Contributing 🤝

Feel free to fork, improve, and submit pull requests. For major changes, open an issue first to discuss your ideas.


---

License

MIT License


---

Contact

For support and inquiries, reach out via WhatsApp at the admin number set in .env.


---

Built with 💡 and ☕ by Strangemind
