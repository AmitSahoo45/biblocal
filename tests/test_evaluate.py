import pytest

from biblocal.evaluate import evaluate
from biblocal.models import PhotoResult


def test_eval_exact_metrics():
    truth = {"a.jpg": ["247"], "b.jpg": ["12"], "c.jpg": []}
    rs = [PhotoResult("a.jpg", "tagged", ["247"]), PhotoResult("b.jpg", "tagged", ["13"]), PhotoResult("c.jpg", "none")]
    rep = evaluate(rs, truth)
    assert (rep.readable, rep.hit_rate, rep.wrong_rate) == (2, .5, .5)
    assert rep.misses == ["b.jpg"] and rep.wrong == [("b.jpg", "13")]


def test_eval_matches_leading_zeros():
    rep = evaluate([PhotoResult("a.jpg", "tagged", ["7"])], {"a.jpg": ["007"]})
    assert (rep.hit_rate, rep.wrong_rate) == (1., 0.)


def test_missing_truth_warns_and_no_tags_is_not_a_hit():
    with pytest.warns(UserWarning, match="1.*truth"):
        rep = evaluate([PhotoResult("a.jpg", "review", suggestions=["7"]), PhotoResult("missing.jpg", "tagged", ["7"])], {"a.jpg": ["7"]})
    assert (rep.photos, rep.readable, rep.hit_rate, rep.wrong_rate, rep.review_rate) == (1, 1, 0., 0., 1.)


def test_wrong_rate_counts_tags_and_blank_truth():
    rep = evaluate([PhotoResult("a.jpg", "tagged", ["7", "8"]), PhotoResult("b.jpg", "tagged", ["9"])],
                   {"a.jpg": ["7"], "b.jpg": []})
    assert rep.hit_rate == 1. and rep.wrong_rate == pytest.approx(2 / 3)
    assert rep.wrong == [("a.jpg", "8"), ("b.jpg", "9")]
