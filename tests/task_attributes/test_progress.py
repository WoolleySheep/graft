from graft.progress import Progress


def test_progress_same():
    assert Progress.IN_PROGRESS is Progress.IN_PROGRESS


def test_progress_less_than():
    assert Progress.NOT_STARTED < Progress.IN_PROGRESS


def test_progress_greater_than():
    assert Progress.IN_PROGRESS > Progress.NOT_STARTED
