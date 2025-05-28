# Web Scraper Agent

A Python-based web scraping automation tool built to extract useful content from websites, process data, and support AI integrations (like OpenAI) through environment-managed API keys.


## Demo - https://drive.google.com/file/d/1r6hCK8o1CTKh-2xVKs7PtyIWlAyCjjFG/view?usp=drivesdk

## Features

* 🌐 URL input and dynamic scraping
* 🔍 Keyword-based content extraction
* 🧠 Integrates with OpenAI for content analysis (summarization, classification, etc.)
* 📁 Local storage of results (JSON/CSV)
* 🔐 Secure API access via `.env` (excluded from version control)

## Tech Stack

* **Python 3.10+**
* **BeautifulSoup4** and **requests** for web scraping
* **OpenAI API** (via `openai` Python package)
* **dotenv** for environment variable management

## Installation

```bash
git clone https://github.com/karthikzzzzzzz/Web-Scraper-Agent.git
cd Web-Scraper-Agent
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Do NOT commit `.env` to Git.** It should be included in `.gitignore`.

## To Run Backend

```bash
uvicorn scrapping_agent.main:agent --reload
```

## To Run Frontend
```bash
cd frontend
npm install
npm run dev
```

You can configure flags to:

* Specify output file name and format
* Select scraping depth or timeout
* Enable/disable OpenAI integration

## Output

Scraped data will be saved under an `output/` directory, as `.json` or `.csv` based on your preference.

## TODO

* [ ] Add unit tests
* [ ] Add support for concurrent scraping

## Contributing

1. Fork the repo
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature-name`)
5. Create a pull request

## License

MIT License. See `LICENSE` file for details.

---

Maintained with ❤️ by [karthikzzzzzzz](https://github.com/karthikzzzzzzz)
