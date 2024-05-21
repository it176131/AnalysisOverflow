# 3rd party
import pytest

# application specific
from analysis_overflow import utils
from analysis_overflow.stackoverflow import StackOverflow


@pytest.fixture
def ref():
    return StackOverflow(user_id=1)


@pytest.mark.parametrize(
    "user_ids,expected",
    [(None, [1]), ([1], [1]), ([2], [2]), ([2, 3], [2, 3])],
)
def test_check_user_ids(
    ref: StackOverflow, user_ids: list[int] | None, expected: list[int]
):
    @utils.check_user_ids
    def to_be_decorated(ref, user_ids):
        assert user_ids == expected

    to_be_decorated(ref, user_ids)
