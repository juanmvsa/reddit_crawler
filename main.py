#!/usr/bin/env python3
"""
Reddit User Information Crawler

This script demonstrates how to retrieve available public information about Reddit users
and your own subscription data. note: you cannot access other users' private subscription lists.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import praw


class RedditCrawler:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        initialize reddit api client.

        args:
            client_id: reddit app client id.
            client_secret: reddit app client secret.
            user_agent: descriptive user agent string.
            username: reddit username (for authenticated requests).
            password: reddit password (for authenticated requests).
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password,
        )

    def get_user_public_info(self, username: str) -> Dict[str, Any]:
        """
        get publicly available information about a reddit user.

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
            }

            return user_info

        except Exception as e:
            print(f"error fetching user info for {username}: {e}")
            return {}

    def get_user_recent_activity(
        self, username: str, limit: int = 25
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        get recent public activity (posts and comments) from a user.
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
        this is not the same as subscriptions, just where they post/comment.

        args:
            username: reddit username.
            limit: number of recent activities to analyze.

        returns:
            list of subreddit names where user is active.
        """
        activity = self.get_user_recent_activity(username, limit)
        subreddits: set[str] = set()

        # collect subreddits from posts.
        for post in activity["recent_posts"]:
            subreddits.add(post["subreddit"])

        # collect subreddits from comments.
        for comment in activity["recent_comments"]:
            subreddits.add(comment["subreddit"])

        return sorted(list(subreddits))

    def get_my_subscriptions(self) -> List[str]:
        """
        get your own subscribed subreddits (requires authentication).
        this only works for your own account, not other users.

        returns:
            list of subreddit names you're subscribed to.
        """
        try:
            subreddits: List[str] = []
            for subreddit in self.reddit.user.subreddits(limit=None):
                subreddits.append(subreddit.display_name)
                time.sleep(0.1)  # rate limiting.

            return sorted(subreddits)

        except Exception as e:
            print(f"error fetching subscriptions: {e}")
            print("make sure you're authenticated with username/password")
            return []

    def get_my_friends(self) -> List[str]:
        """
        get list of reddit users you're following (friends).
        only works for your own account.

        returns:
            list of usernames you're following.
        """
        try:
            friends: List[str] = []
            for friend in self.reddit.user.friends():
                friends.append(friend.name)
                time.sleep(0.1)  # rate limiting.

            return friends

        except Exception as e:
            print(f"error fetching friends list: {e}")
            return []


def main() -> None:
    """
    example usage of the redditcrawler.
    """

    # you need to create a reddit app at https://www.reddit.com/prefs/apps/
    # and get your client_id and client_secret.
    CLIENT_ID = "3ovc_g7TML5FWFNxSbRgcQ"
    CLIENT_SECRET = "8ZbP1DAvpSKiSsI2Rnm-IwPU-4ZU0Q"
    USER_AGENT = "RedditCrawler/1.0 by femmebxt"

    # optional: for accessing your own subscriptions.
    USERNAME = "femmebxt"  # optional.
    PASSWORD = "*bkT9g9NGFcx7!gH5MYZ"  # optional.

    # initialize crawler.
    crawler = RedditCrawler(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        username=USERNAME,  # remove if you don't want to authenticate.
        password=PASSWORD,  # remove if you don't want to authenticate.
    )

    # example: get public info about a user.
    target_username = "femmebxt"  # reddit ceo's username as example.
    print(f"getting public info for u/{target_username}...")
    user_info = crawler.get_user_public_info(target_username)
    print(f"user info: {user_info}")

    # example: get subreddits where user is active.
    print(f"\ngetting active subreddits for u/{target_username}...")
    active_subs = crawler.get_active_subreddits(target_username, limit=50)
    print(f"active in subreddits: {active_subs}")

    # example: get your own subscriptions (requires authentication).
    if USERNAME and PASSWORD:
        print("\ngetting your subscriptions...")
        my_subs = crawler.get_my_subscriptions()
        print(
            f"you're subscribed to {len(my_subs)} subreddits: {my_subs[:10]}..."
        )  # show first 10.

        print("\ngetting your friends list...")
        my_friends = crawler.get_my_friends()
        print(f"you're following {len(my_friends)} users: {my_friends}")


if __name__ == "__main__":
    main()
