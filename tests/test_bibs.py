import pytest
from dataclasses import replace

from biblocal.bibs import decide, demote_frequent, extract_candidates, near_matches
from biblocal.models import Settings, TextHit
from biblocal.startlist import Runner, StartList

# Token/decision unit tests isolate height; the geometric tests enable it below.
S = Settings(accept=.80, min_bib_height_share=0)
BOX = ((0, 0), (10, 0), (10, 10), (0, 10))


def hit(text, score=.95):
    return TextHit(text, score, BOX)


def test_digit_runs_within_length():
    assert [c.number for c in extract_candidates([hit("BIB 247"), hit("123456")], S)] == ["247"]


def test_clock_and_distance_tokens_skipped():
    hits = [hit("1:23:45"), hit("10K"), hit("5km"), hit("42.195"), hit("247")]
    assert [c.number for c in extract_candidates(hits, S)] == ["247"]


def test_mapping_only_in_mostly_digit_tokens():
    c = extract_candidates([hit("2O7"), hit("STOP")], S)
    assert [(x.number, x.mapped) for x in c] == [("207", True)]
    assert c[0].score == pytest.approx(.855)
    assert decide("a.jpg", c, None, S).reasons == ["mapped_chars"]


def test_duplicate_number_keeps_best_score():
    c = extract_candidates([hit("88", .6), hit("88", .9)], S)
    assert [(x.number, x.score) for x in c] == [("88", .9)]


def test_tagged_uses_start_list_spelling_and_name():
    sl = StartList([Runner("007", "Ana")])
    r = decide("a.jpg", extract_candidates([hit("7", .9)], S, sl), sl, S)
    assert (r.status, r.bibs, r.names) == ("tagged", ["007"], ["Ana"])
    assert len(extract_candidates([hit("007"), hit("7", .99)], S, sl)) == 1


def test_not_in_list_goes_to_review_with_suggestion():
    sl = StartList([Runner("247")])
    r = decide("a.jpg", extract_candidates([hit("217", .92)], S, sl), sl, S)
    assert (r.status, r.suggestions) == ("review", ["247"])
    assert "not_in_start_list" in r.reasons and r.bibs == []


def test_review_band_and_none():
    r = decide("a.jpg", extract_candidates([hit("247", .6)], S), None, S)
    assert (r.status, r.reasons) == ("review", ["low_confidence"])
    assert decide("a.jpg", extract_candidates([hit("247", .3)], S), None, S).status == "none"


def test_near_matches_order_and_limit():
    sl = StartList([Runner(b) for b in ["247", "2170", "17", "999", "218"]])
    assert near_matches("217", sl) == ["218", "247", "17"]
    assert near_matches("0217", sl) == ["218", "247", "17"]


def test_frequent_number_demoted():
    rs = [decide(f"{i}.jpg", extract_candidates([hit("2026")], S), None, S) for i in range(20)]
    rs.append(decide("x.jpg", extract_candidates([hit("88")], S), None, S))
    out = demote_frequent(rs, None, S)
    assert all(r.status == "review" and "frequent_number" in r.reasons for r in out[:20])
    assert out[20].bibs == ["88"] and rs[0].status == "tagged"


def test_frequent_filter_skips_start_list_members():
    sl = StartList([Runner("2026")])
    rs = [decide(f"{i}.jpg", extract_candidates([hit("2026")], S, sl), sl, S) for i in range(20)]
    assert all(r.status == "tagged" for r in demote_frequent(rs, sl, S))


def test_frequent_filter_boundaries_and_remaining_bib_alignment():
    rs = [decide(f"{i}.jpg", extract_candidates([hit("2026")], S), None, S) for i in range(5)]
    rs += [decide(f"{i}.jpg", [], None, S) for i in range(5, 20)]
    assert demote_frequent(rs, None, S)[0].status == "tagged"  # exactly 25%
    rs[5] = decide("5.jpg", extract_candidates([hit("2026", .99), hit("88", .9)], S), None, S)
    out = demote_frequent(rs, None, S)
    assert (out[5].status, out[5].bibs, out[5].scores) == ("tagged", ["88"], [.9])
    assert rs[5].bibs == ["2026", "88"]


def test_empty_start_list_never_accepts_and_thresholds_are_inclusive():
    cs = extract_candidates([hit("7", .8)], S)
    assert decide("a.jpg", cs, StartList([]), S).bibs == []
    assert decide("a.jpg", cs, None, S).bibs == ["7"]
    assert decide("a.jpg", extract_candidates([hit("7", .5)], S), None, S).status == "review"


def test_remaining_letters_reject_entire_token_after_mapping():
    hits = [hit("A247"), hit("247th"), hit("2O7A"), hit("247é"), hit("2O7")]
    assert [c.number for c in extract_candidates(hits, S)] == ["207"]


def test_box_height_share_inclusive_and_filtered_before_deduplication():
    settings = replace(S, min_bib_height_share=.02)
    small = TextHit("247", .99, ((0, 0), (40, 0), (40, 9), (0, 9)))
    boundary = TextHit("247", .90, BOX)
    candidates = extract_candidates([small, boundary], settings, image_height=500)
    assert [(c.number, c.score) for c in candidates] == [("247", .90)]
    assert extract_candidates([boundary], settings, image_height=1000) == []


def test_height_filter_requires_valid_image_height():
    settings = replace(S, min_bib_height_share=.02)
    for height in (None, 0, -1):
        with pytest.raises(ValueError, match="image_height"):
            extract_candidates([hit("247")], settings, image_height=height)


@pytest.mark.parametrize("score,height,status", [(.89, 30, "review"), (.90, 20, "tagged"), (.99, 19, "none")])
def test_selected_defaults_accept_confident_bibs_at_two_percent(score, height, status):
    settings = Settings()
    text = TextHit("247", score, ((0, 0), (100, 0), (100, height), (0, height)))
    candidates = extract_candidates([text], settings, image_height=1000)
    result = decide("a.jpg", candidates, None, settings)
    assert result.status == status
    assert result.bibs == (["247"] if status == "tagged" else [])
