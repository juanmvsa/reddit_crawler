# reddit crawler with `json` storage

a python script to crawl your reddit user information using the reddit api with secure credential management and `json` file storage.


## 0. features

- secure credential management via environment variables or secrets file.
- all data saved to structured `json` files with timestamps.
- complete user crawling with detailed activity analysis.
- support for personal data retrieval (subscriptions, friends).
- rate limiting and error handling.

---

## 1. setup with `uv`

1. install [uv](https://docs.astral.sh/uv/):
   ```bash
   curl -lssf https://astral.sh/uv/install.sh | sh
   ```

2. initialize the project:
   ```bash
   mkdir reddit-crawler && cd reddit-crawler
   ```

3. create `pyproject.toml` and save the script as `reddit_crawler.py`.

4. install dependencies:
   ```bash
   uv sync
   ```

---

## 2. credential setup

### option 1: environment variables (recommended)
```bash
export reddit_client_id="your_client_id"
export reddit_client_secret="your_client_secret"
export reddit_user_agent="redditcrawler/1.0 by yourusername"
export reddit_username="your_username"  # optional
export reddit_password="your_password"  # optional
```

#### notes

 
### option 2: secrets file
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

---

## 3. get reddit api credentials

1. go [here](https://www.reddit.com/prefs/apps).
2. click "create app" or "create another app".
3. choose "script" as the app type.
4. generate your `reddit_client_secret`.
5. the `client_id` is emailed to the account associated to your reddit account, once you have generated your `reddit_client_secret`.


---

## 4. usage

after installing all the dependencies using `uv`:

```bash
uv run python reddit_crawler.py
```

### output files

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

### output `json` file structure

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

---

## development

install development dependencies:
```bash
uv sync --group dev
```

format code:
```bash
uv run black reddit_crawler.py
uv run isort reddit_crawler.py
```

type checking:
```bash
uv run mypy reddit_crawler.py
```

---

## security notes

- **never commit `secrets.json` to version control**
- use environment variables in production
- the script respects reddit's rate limits

---

## limitations

- cannot access other users' private subscription lists
- rate limited to respect reddit's api terms
- requires reddit api credentials
- some data may be unavailable for private/suspended accounts
