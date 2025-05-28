#!/usr/bin/env python3
"""
Reddit User Information Crawler

This script demonstrates how to retrieve available public information about Reddit users
and your own subscription data. note: you cannot access other users' private subscription lists.
all data is saved to json files for persistence.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import praw


class RedditCrawler:
    def __init__(
        self,
        output_dir: str = "reddit_data",
    ) -> None:
        """
        initialize reddit api client with credentials from environment or secrets file.

        args:
            output_dir: directory to save json files.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # load credentials from environment variables or secrets file.
        credentials = self._load_credentials()

        self.reddit = praw.Reddit(
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            user_agent=credentials["user_agent"],
            username=credentials.get("username"),
            password=credentials.get("password"),
        )

        print(f"initialized reddit crawler. data will be saved to: {self.output_dir}")

    def _load_credentials(self) -> Dict[str, str]:
        """
        load reddit api credentials from environment variables or secrets file.

        returns:
            dictionary containing credentials.
        """
        # try environment variables first.
        credentials = {
            "client_id": os.getenv("REDDIT_CLIENT_ID"),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
            "user_agent": os.getenv("REDDIT_USER_AGENT", "RedditCrawler/1.0"),
            "username": os.getenv("REDDIT_USERNAME"),
            "password": os.getenv("REDDIT_PASSWORD"),
        }

        # if no environment variables, try secrets file.
        secrets_file = Path("secrets.json")
        if not credentials["client_id"] and secrets_file.exists():
            try:
                with open(secrets_file, "r") as f:
                    file_credentials = json.load(f)
                    credentials.update(file_credentials)
                    print("loaded credentials from secrets.json")
            except Exception as e:
                print(f"error loading secrets.json: {e}")

        # validate required credentials.
        if not credentials["client_id"] or not credentials["client_secret"]:
            self._create_secrets_template()
            raise ValueError(
                "reddit credentials not found. please set environment variables or create secrets.json file."
            )

        return credentials

    def _create_secrets_template(self) -> None:
        """
        create a template secrets.json file if it doesn't exist.
        """
        secrets_template = {
            "client_id": "your_reddit_client_id_here",
            "client_secret": "your_reddit_client_secret_here",
            "user_agent": "RedditCrawler/1.0 by YourUsername",
            "username": "your_reddit_username_optional",
            "password": "your_reddit_password_optional",
        }

        secrets_file = Path("secrets.json")
        if not secrets_file.exists():
            with open(secrets_file, "w") as f:
                json.dump(secrets_template, f, indent=2)
            print(
                f"created template secrets.json file. please update it with your credentials."
            )

    def _save_to_json(self, data: Any, filename: str) -> None:
        """
        save data to a json file with timestamp.

        args:
            data: data to save.
            filename: name of the json file (without extension).
        """
        filepath = self.output_dir / f"{filename}.json"

        # add metadata.
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "data_type": filename,
            "data": data,
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"saved {filename} data to: {filepath}")
        except Exception as e:
            print(f"error saving {filename}: {e}")

    def get_user_public_info(self, username: str) -> Dict[str, Any]:
        """
        get publicly available information about a reddit user.
        saves data to user_public_info.json.

        args:
            username: reddit username to look up.

        returns:
            dictionary containing public user information.
        """
        try:
            user = self.reddit.redditor(username)

            # get basic user info.
            user_info = {
                "username": user.name,
                "created_utc": user.created_utc,
                "comment_karma": user.comment_karma,
                "link_karma": user.link_karma,
                "is_verified": user.verified if hasattr(user, "verified") else None,
                "has_premium": user.is_gold if hasattr(user, "is_gold") else None,
                "account_age_days": (datetime.now().timestamp() - user.created_utc)
                / 86400,
            }

            # save to json file.
            self._save_to_json(user_info, f"user_public_info_{username}")

            return user_info

        except Exception as e:
            print(f"error fetching user info for {username}: {e}")
            return {}

    def get_user_recent_activity(
        self, username: str, limit: int = 25
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        get recent public activity (posts and comments) from a user.
        saves data to user_recent_activity.json.
        this can give hints about which subreddits they're active in.

        args:
            username: reddit username.
            limit: number of recent items to fetch.

        returns:
            dictionary with recent posts and comments.
        """
        try:
            user = self.reddit.redditor(username)

            # get recent submissions (posts).
            recent_posts: List[Dict[str, Any]] = []
            for submission in user.submissions.new(limit=limit):
                recent_posts.append(
                    {
                        "title": submission.title,
                        "subreddit": submission.subreddit.display_name,
                        "created_utc": submission.created_utc,
                        "score": submission.score,
                        "url": f"https://reddit.com{submission.permalink}",
                        "num_comments": submission.num_comments,
                    }
                )
                time.sleep(0.1)  # rate limiting.

            # get recent comments.
            recent_comments: List[Dict[str, Any]] = []
            for comment in user.comments.new(limit=limit):
                recent_comments.append(
                    {
                        "body": (
                            comment.body[:200] + "..."
                            if len(comment.body) > 200
                            else comment.body
                        ),
                        "subreddit": comment.subreddit.display_name,
                        "created_utc": comment.created_utc,
                        "score": comment.score,
                        "submission_title": comment.submission.title,
                    }
                )
                time.sleep(0.1)  # rate limiting.

            activity_data = {
                "username": username,
                "posts_count": len(recent_posts),
                "comments_count": len(recent_comments),
                "recent_posts": recent_posts,
                "recent_comments": recent_comments,
            }

            # save to json file.
            self._save_to_json(activity_data, f"user_recent_activity_{username}")

            return {
                "recent_posts": recent_posts,
                "recent_comments": recent_comments,
            }

        except Exception as e:
            print(f"error fetching activity for {username}: {e}")
            return {"recent_posts": [], "recent_comments": []}

    def get_active_subreddits(self, username: str, limit: int = 100) -> List[str]:
        """
        analyze user's recent activity to find subreddits they're active in.
        saves data to active_subreddits.json.
        this is not the same as subscriptions, just where they post/comment.

        args:
            username: reddit username.
            limit: number of recent activities to analyze.

        returns:
            list of subreddit names where user is active.
        """
        activity = self.get_user_recent_activity(username, limit)
        subreddits: set[str] = set()
        subreddit_activity: Dict[str, Dict[str, int]] = {}

        # collect subreddits from posts.
        for post in activity["recent_posts"]:
            subreddit = post["subreddit"]
            subreddits.add(subreddit)
            if subreddit not in subreddit_activity:
                subreddit_activity[subreddit] = {"posts": 0, "comments": 0}
            subreddit_activity[subreddit]["posts"] += 1

        # collect subreddits from comments.
        for comment in activity["recent_comments"]:
            subreddit = comment["subreddit"]
            subreddits.add(subreddit)
            if subreddit not in subreddit_activity:
                subreddit_activity[subreddit] = {"posts": 0, "comments": 0}
            subreddit_activity[subreddit]["comments"] += 1

        # create detailed activity data.
        active_subreddits_data = {
            "username": username,
            "total_active_subreddits": len(subreddits),
            "subreddits_list": sorted(list(subreddits)),
            "detailed_activity": subreddit_activity,
        }

        # save to json file.
        self._save_to_json(active_subreddits_data, f"active_subreddits_{username}")

        return sorted(list(subreddits))

    def get_my_subscriptions(self) -> List[str]:
        """
        get your own subscribed subreddits (requires authentication).
        saves data to my_subscriptions.json.
        this only works for your own account, not other users.

        returns:
            list of subreddit names you're subscribed to.
        """
        try:
            subreddits: List[str] = []
            subreddit_details: List[Dict[str, Any]] = []

            for subreddit in self.reddit.user.subreddits(limit=None):
                subreddits.append(subreddit.display_name)
                subreddit_details.append(
                    {
                        "name": subreddit.display_name,
                        "title": subreddit.title,
                        "subscribers": subreddit.subscribers,
                        "created_utc": subreddit.created_utc,
                        "description": subreddit.public_description[:200] + "..."
                        if len(subreddit.public_description or "") > 200
                        else subreddit.public_description,
                    }
                )
                time.sleep(0.1)  # rate limiting.

            subscriptions_data = {
                "total_subscriptions": len(subreddits),
                "subscriptions_list": sorted(subreddits),
                "detailed_subscriptions": subreddit_details,
            }

            # save to json file.
            self._save_to_json(subscriptions_data, "my_subscriptions")

            return sorted(subreddits)

        except Exception as e:
            print(f"error fetching subscriptions: {e}")
            print("make sure you're authenticated with username/password")
            return []

    def get_my_friends(self) -> List[str]:
        """
        get list of reddit users you're following (friends).
        saves data to my_friends.json.
        only works for your own account.

        returns:
            list of usernames you're following.
        """
        try:
            friends: List[str] = []
            friends_details: List[Dict[str, Any]] = []

            for friend in self.reddit.user.friends():
                friends.append(friend.name)
                friends_details.append(
                    {
                        "username": friend.name,
                        "date_added": friend.date,
                    }
                )
                time.sleep(0.1)  # rate limiting.

            friends_data = {
                "total_friends": len(friends),
                "friends_list": friends,
                "detailed_friends": friends_details,
            }

            # save to json file.
            self._save_to_json(friends_data, "my_friends")

            return friends

        except Exception as e:
            print(f"error fetching friends list: {e}")
            return []

    def crawl_user_complete(self, username: str) -> Dict[str, Any]:
        """
        perform complete crawling of a user's public information.
        saves all data to separate json files.

        args:
            username: reddit username to crawl.

        returns:
            summary of crawled data.
        """
        print(f"starting complete crawl for user: {username}")

        # get all public information.
        user_info = self.get_user_public_info(username)
        active_subs = self.get_active_subreddits(username)

        summary = {
            "username": username,
            "crawl_timestamp": datetime.now().isoformat(),
            "user_info": user_info,
            "active_subreddits_count": len(active_subs),
            "active_subreddits": active_subs,
        }

        # save summary.
        self._save_to_json(summary, f"crawl_summary_{username}")

        print(
            f"completed crawl for {username}. found activity in {len(active_subs)} subreddits."
        )
        return summary


def main() -> None:
    """
    example usage of the redditcrawler with json storage.
    """

    try:
        # initialize crawler (credentials loaded automatically).
        crawler = RedditCrawler(output_dir="reddit_data")

        # example: perform complete crawl of a user.
        target_username = "femmebxt"  # reddit ceo's username as example.
        print(f"performing complete crawl for u/{target_username}...")
        summary = crawler.crawl_user_complete(target_username)

        # example: get your own data (requires authentication).
        try:
            print("\nattempting to get your personal data...")
            my_subs = crawler.get_my_subscriptions()
            if my_subs:
                print(f"successfully retrieved {len(my_subs)} subscriptions")

            my_friends = crawler.get_my_friends()
            if my_friends:
                print(f"successfully retrieved {len(my_friends)} friends")
            elif not my_subs:
                print(
                    "no authenticated data retrieved. check your username/password in secrets."
                )

        except Exception as e:
            print(f"could not retrieve personal data: {e}")
            print(
                "this is normal if you haven't provided username/password credentials."
            )

        print(
            f"\nall data has been saved to json files in the 'reddit_data' directory."
        )

    except ValueError as e:
        print(f"credential error: {e}")
        print("\nto fix this:")
        print("1. set environment variables:")
        print("   export REDDIT_CLIENT_ID='your_client_id'")
        print("   export REDDIT_CLIENT_SECRET='your_client_secret'")
        print("2. or update the generated secrets.json file with your credentials")


if __name__ == "__main__":
    main()
