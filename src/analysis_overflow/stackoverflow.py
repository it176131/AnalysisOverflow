from os import getenv
from typing import Any

from pydantic.config import ConfigDict
from pydantic.main import BaseModel
from stackapi import StackAPI

from analysis_overflow.utils import check_user_ids


class Item(BaseModel):
    """An item in :attribute:``Result.items``."""

    model_config = ConfigDict(extra="allow")


class Result(BaseModel):
    """Result of an API call."""

    model_config = ConfigDict(extra="forbid")

    backoff: int
    has_more: bool
    page: int
    quota_max: int
    quota_remaining: int
    total: int
    items: list[Item]


class StackOverflow(StackAPI):
    """
    ***Subclass of `StackAPI` limiting queries to StackOverflow.***

    The object used to interact with the Stack Exchange API

    :param user_id: The user's Stack Overflow ID
    :param version: **(Required)** The version of the API you are
        connecting to.
    :param max_pages: The maximum number of pages to retrieve
    :param page_size: The number of elements per page. The API limits
        this to a maximum of 100 items on all end points
    :param key: An API key
    :param access_token: An access token associated with an application
        and a user, to grant more permissions (such as write access)
    """

    def __init__(self, user_id: int, **kwargs):
        self._user_id = user_id

        if kwargs.get("key") is None:
            kwargs["key"] = self._get_key()

        super().__init__(name="stackoverflow", **kwargs)
        self._quota_remaining: int | None = None

    @staticmethod
    def _get_key() -> str | None:
        """Get the API key from the user's environment variables.

        API key should be stored with the variable name
        "STACK_API_KEY". If no API key, return ``None``.

        :returns: api_key
        """
        api_key = getenv(key="STACK_API_KEY")
        return api_key

    @property
    def quota_remaining(self) -> int | None:
        """Return the remaining quota if available.

        :return: remaining_quota
        """
        remaining_quota = self._quota_remaining
        return remaining_quota

    @property
    def user_id(self) -> int:
        """Return the User's ID.

        :return: user_id
        """
        user_id = self._user_id
        return user_id

    @user_id.setter
    def user_id(self, user_id: int) -> None:
        """Set the User's Stack Overflow ID after instantiation."""
        self._user_id = user_id

    def fetch(
        self,
        endpoint: str | None = None,
        page: int = 1,
        key: str | None = None,
        filter: str = "default",
        **kwargs,
    ) -> dict[str, Any]:
        super().fetch.__doc__
        results = super().fetch(
            endpoint=endpoint, page=page, key=key, filter=filter, **kwargs
        )
        self._quota_remaining = results.get("quota_remaining")
        return results

    @check_user_ids
    def fetch_user_answers(
        self, user_ids: list[int] | None = None
    ) -> dict[str, Any]:
        """Get users' answer posts identified by a set of ids.

        Reference:
        https://api.stackexchange.com/docs/answers-on-users

        :param user_ids: user-ids of interest. If left as `None`, will use
            `self.user_id`
        :return: user_answers
        """
        endpoint = "users/{ids}/answers"
        user_answers = self.fetch(endpoint=endpoint, ids=user_ids)
        return user_answers

    def fetch_questions(self, question_ids: list[int]) -> dict[str, Any]:
        """Get the questions identified by a set of ids.

        Reference:
        https://api.stackexchange.com/docs/questions-by-ids

        :param question_ids: IDs of questions
        :returns: questions
        """
        endpoint = "questions/{ids}"
        questions = self.fetch(endpoint=endpoint, ids=question_ids)
        return questions

    @check_user_ids
    def fetch_user_reputation_history(
        self, user_ids: list[int] | None = None
    ) -> dict[str, Any]:
        """Get history of a user's reputation, excluding private events.

        Reference:
        https://api.stackexchange.com/docs/reputation-history

        :param user_ids: User IDs of interest.
            If left as `None`, will use ``self.user_id``
        :return: user_rep_history
        """
        endpoint = "users/{ids}/reputation-history"
        user_rep_history = self.fetch(endpoint=endpoint, ids=user_ids)
        return user_rep_history

    def fetch_badge_recipients(self, badge_ids: list[int]) -> dict[str, Any]:
        """Get the recent recipients of the given badges.

        Reference:
        https://api.stackexchange.com/docs/badge-recipients-by-ids

        :param badge_ids: Badge IDs of interest.
        :return: badge_recipients
        """
        endpoint = "badges/{ids}/recipients"
        badge_recipients = self.fetch(endpoint=endpoint, ids=badge_ids)
        return badge_recipients
