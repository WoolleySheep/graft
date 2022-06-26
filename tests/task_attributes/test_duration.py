from graft.duration import Duration


def test_duration_same():
    assert Duration.LESS_THAN_1_DAY is Duration.LESS_THAN_1_DAY


def test_duration_less_than():
    assert Duration.LESS_THAN_1_HOUR < Duration.LESS_THAN_1_WEEK


def test_duration_greater_than():
    assert Duration.ONGOING > Duration.LESS_THAN_1_MONTH
