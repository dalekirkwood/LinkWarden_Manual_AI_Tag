# 🏷️ LinkWarden Intelligent Tagger

## 📌 Overview

**🚨 Temporary Solution 🚨**

This script was created in response to [LinkWarden GitHub Issue #971](https://github.com/linkwarden/linkwarden/issues/971) as a temporary fix to manually run AI tagging on existing links. It is intended to be a community-driven solution until an official feature is implemented by the LinkWarden team.

Automatically tag your LinkWarden bookmarks using AI-powered tag suggestions! This Python script leverages Ollama's language model to intelligently categorize your saved links based on their content.

## ⚠️ Important Notes

- This is a community-created temporary solution
- Not an official LinkWarden feature
- May be deprecated once an official solution is implemented
- Use at your own discretion

## ✨ Features

- 🤖 AI-driven tag suggestions using Ollama
- 📚 Customizable tag list
- 🔍 Smart content analysis
- 🏗️ Flexible configuration options

## 🛠️ Prerequisites

- Python 3.8+
- LinkWarden instance
- Ollama with Phi3 mini model
- API access to LinkWarden

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/linkwarden-tagger.git
   cd linkwarden-tagger
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file:
   ```
   LINKWARDEN_API_KEY=your_api_key_here
   LINKWARDEN_BASE_URL=http://localhost:3002/api/v1  # Optional
   OLLAMA_BASE_URL=http://localhost:11434  # Optional
   SKIP_LINKS_WITH_TAGS=true  # Optional
   ```

## 🚀 Usage

1. Customize `tags.txt` with your preferred tags
2. Run the script:
   ```bash
   python linkwarden_tagger.py
   ```

## 🔧 Configuration

### Environment Variables
- `LINKWARDEN_API_KEY`: Your LinkWarden API key (required)
- `LINKWARDEN_BASE_URL`: Custom LinkWarden API URL (optional)
- `OLLAMA_BASE_URL`: Custom Ollama server URL (optional)
- `SKIP_LINKS_WITH_TAGS`: Skip links that already have tags (optional)

### Tag File
Manage your tags in `tags.txt`. Organize them by categories, one tag per line. Comments start with `#`.

## 📋 Requirements

- `requests`
- `python-dotenv`
- Ollama with Phi3 mini model installed (see [Linkwarden AI Worker Documentation](https://docs.linkwarden.app/self-hosting/ai-worker))

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙌 Acknowledgments

- [LinkWarden](https://github.com/linkwarden/linkwarden)
- [Ollama](https://ollama.ai)
- [Phi3 Model](https://ollama.ai/library/phi3)
- Inspiration: [LinkWarden Issue #971](https://github.com/linkwarden/linkwarden/issues/971)

---

🌟 **Happy Tagging!** 🏷️🚀

**Disclaimer:** This is a community-created tool and is not an official part of the LinkWarden project. Use with caution and always backup your data.
