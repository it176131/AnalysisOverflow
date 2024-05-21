# 3rd party
from stackapi.stackapi import StackAPIError
import pandas as pd
import pytest

# application specific
from analysis_overflow.stackoverflow import StackOverflow


@pytest.fixture
def so():
    return StackOverflow(user_id=1, max_pages=1, page_size=5)


@pytest.mark.parametrize(argnames="key", argvalues=[None, "test"])
def test__get_key(key: str | None):
    if key is None:
        so = StackOverflow(user_id=1, key=key)
        actual = so._get_key()
        assert actual == so.key
        assert isinstance(actual, str) or actual is None

    else:
        with pytest.raises(StackAPIError):
            StackOverflow(user_id=1, key=key)


def test_user_id(user_id1: int = 1, user_id2: int = 2):
    so = StackOverflow(user_id=user_id1)
    assert user_id1 == so.user_id
    so.user_id = user_id2
    assert user_id2 == so.user_id


@pytest.mark.parametrize(
    argnames="endpoint", argvalues=[None, "test", "users"]
)
def test_fetch(so: StackOverflow, endpoint: str | None):
    if endpoint is None:
        with pytest.raises(ValueError):
            so.fetch(endpoint=endpoint)

    elif endpoint == "test":
        with pytest.raises(StackAPIError):
            so.fetch(endpoint=endpoint)

    else:
        results = so.fetch(endpoint=endpoint)
        assert isinstance(results, dict)
        items: list = results["items"]
        assert len(items) <= so.max_pages * so.page_size


@pytest.mark.parametrize(argnames="user_ids", argvalues=[None, [1], [2, 3]])
def test_fetch_user_answers(so: StackOverflow, user_ids: list[int] | None):
    user_answers = so.fetch_user_answers(user_ids=user_ids)
    assert isinstance(user_answers, dict)
    items = user_answers.get("items")
    df = pd.DataFrame(items)
    owner_series = df["owner"].to_list()
    owner_df = pd.DataFrame(owner_series)

    if user_ids is None:
        user_id: int = getattr(so, "user_id")
        assert owner_df["user_id"].eq(user_id).all()

    else:
        assert owner_df["user_id"].isin(user_ids).all()


@pytest.mark.parametrize(
    argnames="question_ids", argvalues=[None, [1], [60325792]]
)
def test_fetch_questions(so: StackOverflow, question_ids: list[int]):
    if question_ids is None:
        with pytest.raises(StackAPIError):
            so.fetch_questions(question_ids=question_ids)

    else:
        results = so.fetch_questions(question_ids=question_ids)
        assert isinstance(results, dict)
        items = results.get("items")
        df = pd.DataFrame(items)

        # valid question_id
        if not df.empty:
            assert df["question_id"].isin(question_ids).all()


@pytest.mark.parametrize(argnames="user_ids", argvalues=[None, [1], [2, 3]])
def test_fetch_user_reputation_history(
    so: StackOverflow, user_ids: list[int] | None
):
    user_rep_history = so.fetch_user_reputation_history(user_ids=user_ids)
    assert isinstance(user_rep_history, dict)
    items = user_rep_history.get("items")
    df = pd.DataFrame(items)
    user_id_series = df["user_id"]

    if user_ids is None:
        user_id = getattr(so, "user_id")
        assert user_id_series.eq(user_id).all()

    else:
        assert user_id_series.isin(user_ids).all()


@pytest.mark.parametrize(
    argnames="badge_ids", argvalues=[None, [267], [50, 51]]
)
def test_fetch_badge_recipients(so: StackOverflow, badge_ids: list[int]):
    if badge_ids is None:
        with pytest.raises(StackAPIError):
            so.fetch_badge_recipients(badge_ids=badge_ids)

    else:
        recipients = so.fetch_badge_recipients(badge_ids=badge_ids)
        assert isinstance(recipients, dict)
        items = recipients.get("items")
        df = pd.DataFrame(items)

        # valid badge_ids
        if not df.empty:
            badge_id_series = df["badge_id"]
            assert badge_id_series.isin(badge_ids).all()
