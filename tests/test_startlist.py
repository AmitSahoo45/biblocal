import pytest

from biblocal.startlist import Runner, StartList, load_start_list, normalize_bib


def test_semicolon_bom_leading_zeros(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_bytes("\ufeffBib;Name\n007;Ana Silva\n247;Jo Lee\n\n".encode("utf-8"))
    sl = load_start_list(p)
    assert len(sl) == 2
    assert sl.lookup("7") == Runner("007", "Ana Silva")
    assert sl.lookup("247").name == "Jo Lee"
    assert sl.lookup("999") is None
    assert (sl.min_len, sl.max_len) == (1, 3)
    assert sl.bibs == ["007", "247"] and "7" in sl


def test_number_header_tab_delimiter_extra_columns(tmp_path):
    p = tmp_path / "sl.tsv"
    p.write_text("number\tname\tclub\n12\tAna\tRC\n", encoding="utf-8")
    assert load_start_list(p).lookup("12").name == "Ana"


def test_non_digit_bib_names_row(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_text("bib\n12\nA7\n", encoding="utf-8")
    with pytest.raises(ValueError, match="row 3"):
        load_start_list(p)


def test_duplicate_after_normalization(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_text("bib\n007\n7\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_start_list(p)


def test_missing_bib_column(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_text("name\nAna\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bib"):
        load_start_list(p)


def test_header_trim_category_blank_rows_and_zero(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_text(" BIB , NAME , Category \n000, Zero , Masters \n,,\n", encoding="utf-8")
    sl = load_start_list(p)
    assert sl.lookup("0") == Runner("000", "Zero", "Masters")
    assert normalize_bib("000") == "0"


def test_empty_list_and_invalid_direct_bib(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_text("bib\n", encoding="utf-8")
    sl = load_start_list(p)
    assert len(sl) == 0 and "7" not in sl
    assert (sl.min_len, sl.max_len) == (1, 5)
    with pytest.raises(ValueError, match="bib"):
        StartList([Runner("12A")])
