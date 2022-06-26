from graft.priority import Priority


def test_priority_same():
    assert Priority.MEDIUM is Priority.MEDIUM


def test_priority_less_than():
    assert Priority.LOW < Priority.HIGH


def test_priority_greater_than():
    assert Priority.CRITICAL > Priority.OPTIONAL
