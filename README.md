# 🕷️ reddit crawler with `json` storage

a python script to crawl your reddit user information using the reddit api with secure credential management and `json` file storage.

## 📚 table of contents 

✨ [0. features](#-0.-features)

🚀 [1. setup with `uv`](#-1.-setup-with-uv)

   🚀 [1.0 install `uv`](#1.0-install-uv)

   🚀 [1.1 clone this repo](#1.1-clone-this-repo)

   🚀 [1.2 initialize this project](#1.2-initialize-this-project)

   🚀 [1.3 install dependencies](#1.3-install-dependencies)

🔐 [2. credentials setup](#-2.-credentials-setup)

🔑 [3. get reddit api credentials](#-3.-get-reddit-api-credentials)

🪄 [4. usage](#-4.-usage)

🪄 [4.0 running the script](#4.0-running-the-script)

   🪄 [4.1 output files](#4.1-output-files)

   🪄 [4.2 output `json` file structure ](#4.2-output-json-file-structure)

👩🏿‍💻 [5. development](#-5.-development)

   👩🏿‍💻 [5.0 install development dependencies](#5.0-install-development-dependencies)

   👩🏿‍💻 [5.1 format code](#5.1-format-code)

   👩🏿‍💻 [5.2 type checking](#5.2-type-checking)

🔒 [6. security notes](#-6.-security-notes)

⛔️ [7. limitations](#-7.-limitations)

---

## ✨ 0. features
- secure credential management via environment variables or secrets file.
- all data saved to structured `json` files with timestamps.
- complete user crawling with detailed activity analysis.
- support for personal data retrieval (subscriptions, friends).
- rate limiting and error handling.

[*back to table of contents*](#-table-of-contents)

## 🚀 1. setup with `uv`

### 1.0 install [uv](https://docs.astral.sh/uv/)
   ```bash
   curl -lssf https://astral.sh/uv/install.sh | sh
   ```

### 1.1 clone this repo
```bash
git clone https://github.com/juanmvsa/reddit_crawler
```

### 1.2 initialize this project
   ```bash
   cd reddit-crawler
   ```

```bash
uv init
```

### 1.3 install dependencies
   ```bash
   uv sync
   ```

[*back to table of contents*](#-table-of-contents)

## 🔐 2. credentials setup

#### option 1: environment variables (recommended)
```bash
export reddit_client_id="your_client_id"
export reddit_client_secret="your_client_secret"
export reddit_user_agent="redditcrawler/1.0 by yourusername"
export reddit_username="your_username"  # optional
export reddit_password="your_password"  # optional
```
 
#### option 2: secrets file
run the script once to generate `secrets.json` template, then update it:
```json
{
  "client_id": "your_reddit_client_id_here",
  "client_secret": "your_reddit_client_secret_here",
  "user_agent": "redditcrawler/1.0 by yourusername",
  "username": "your_reddit_username_optional",
  "password": "your_reddit_password_optional"
}
```

**important:** add `secrets.json` to `.gitignore` to keep credentials secure.

[*back to table of contents*](#-table-of-contents)

## 🔑 3. get reddit api credentials

**a)** go [here](https://www.reddit.com/prefs/apps).

**b)** click "create app" or "create another app".

**c)** choose "script" as the app type.

**d)** generate your `reddit_client_secret`.

**e)** the `client_id` is emailed to the account associated to your reddit account, once you have generated your `reddit_client_secret`.

[*back to table of contents*](#-table-of-contents)

## 🪄 4. usage

### 4.0 running the script
after installing all the dependencies using `uv`:

```bash
uv run reddit_crawler.py
```

### 4.1 output files
all data is saved to the `reddit_data/` directory:
- `user_public_info_{username}.json` - basic user information
- `user_recent_activity_{username}.json` - recent posts and comments
- `active_subreddits_{username}.json` - subreddits where user is active
- `my_subscriptions.json` - your subscribed subreddits (requires auth)
- `my_friends.json` - users you're following (requires auth)
- `crawl_summary_{username}.json` - complete crawl summary

each file includes:
- timestamp of data collection
- data type identifier
- structured data with metadata

### 4.2 output `json` file structure

```json
{
  "timestamp": "2024-01-15t10:30:45.123456",
  "data_type": "active_subreddits_username",
  "data": {
    "username": "example_user",
    "total_active_subreddits": 15,
    "subreddits_list": ["python", "programming", "webdev"],
    "detailed_activity": {
      "python": {"posts": 5, "comments": 12},
      "programming": {"posts": 2, "comments": 8}
    }
  }
}
```

[*back to table of contents*](#-table-of-contents)

## 👩🏿‍💻 5. development

### 5.0 install development dependencies
```bash
uv sync --group dev
```

### 5.1 format code
```bash
uv run black reddit_crawler.py
```

```bash
uv run isort reddit_crawler.py
```

### 5.2 type checking
```bash
uv run mypy reddit_crawler.py
```

[*back to table of contents*](#-table-of-contents)

## 🔒 6. security notes

- **never commit `secrets.json` to version control.**
- use environment variables in production.
- the script respects reddit's rate limits.

[*back to table of contents*](#-table-of-contents)

## 🚫 7. limitations

- cannot access other users' private subscription lists.
- rate limited to respect reddit's api terms.
- requires reddit api credentials.
- some data may be unavailable for private/suspended accounts.

  [*back to table of contents*](#-table-of-contents)
