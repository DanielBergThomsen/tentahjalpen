"""Unit tests for the db_interface class."""

from tentahjalpen.db_interface import list_suggestions, remove, remove_all
from tentahjalpen.db_interface import approve, approve_all, init_db


def test_list(suggestion_db, capfd):
    """Verify that the function actually lists all entries in exam_suggestions table"""

    test_db = suggestion_db

    list_suggestions(test_db)
    out, _ = capfd.readouterr()

    assert "EDA322" in out
    assert "1998-12-26" in out
    assert "exam" in out
    assert "EDA321" in out
    assert "2012-12-26" in out
    assert "solution" in out


def test_list_empty(inited_db, capfd):
    """Verify that the function doesn't list anything any courses"""

    test_db = inited_db

    list_suggestions(test_db)
    out, _ = capfd.readouterr()

    assert "exam" not in out
    assert "solution" not in out


def test_remove(suggestion_db):
    """Verify that the function actually removes the entry in exam_suggestions table"""

    test_db = suggestion_db

    entry = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]
    remove(entry["id"], test_db)

    matching = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))
    assert not matching


def test_remove_invalid(suggestion_db):
    """Verify that the function doesn't remove anything when attempting to remove something
    that doesn't exist"""

    test_db = suggestion_db

    _ = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]
    remove("MEM420", test_db)

    matching = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))
    assert len(matching) == 1


def test_remove_all(suggestion_db):
    """Verify that the function actually removes all entries in exam_suggestions table"""

    test_db = suggestion_db

    num_entries = len(test_db.query("SELECT * FROM exam_suggestions"))
    assert num_entries > 0

    remove_all(test_db)
    num_entries = len(test_db.query("SELECT * FROM exam_suggestions"))
    assert num_entries == 0


def test_remove_all_empty(inited_db):
    """Verify that the function doesn't crash when running on empty table"""

    test_db = inited_db
    remove_all(test_db)


def test_approve(suggestion_db):
    """Verify that the function actually inserts the entry in exam_suggestions table into the
    results table and that the suggestion is then removed from exam_suggestions"""

    test_db = suggestion_db

    r_entry = test_db.query(
        "SELECT * FROM results WHERE code=%s", ("EDA322",))[0]
    assert r_entry["exam"] is None

    es_entry = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]
    pdf = es_entry["exam"]
    approve(es_entry["id"], test_db)

    es_entry = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))
    assert not es_entry

    r_entry = test_db.query(
        "SELECT * FROM results WHERE code=%s", ("EDA322",))[0]
    assert r_entry["exam"] == pdf


def test_approve_invalid(basic_db):
    """Verify that the function actually inserts the entry in exam_suggestions table into the
    results table and that the suggestion is then removed from exam_suggestions"""

    test_db = basic_db

    approve(1, test_db)

    entries = test_db.query("SELECT * FROM results WHERE exam IS NOT NULL")
    assert not entries


def test_approve_all(suggestion_db):
    """Verify that the function actually approves all entries in exam_suggestions table"""

    test_db = suggestion_db

    r_entries = test_db.query("SELECT * FROM results")
    assert r_entries
    for entry in r_entries:
        assert entry["exam"] is None

    es_entries = test_db.query("SELECT * FROM exam_suggestions")
    pdfs = [entry["exam"] for entry in es_entries]
    approve_all(test_db)

    es_entries = test_db.query("SELECT * FROM exam_suggestions")
    assert not es_entries

    r_entries = test_db.query("SELECT * FROM results")
    for i, _ in enumerate(r_entries):
        assert r_entries[i]["exam"] == pdfs[i]


def test_approve_all_empty(basic_db):
    """Verify that the function doesn't crash when running on empty table"""

    test_db = basic_db
    approve_all(test_db)


def test_init_db(empty_db):
    """Verify that the tables for the results and exam_suggestions are generated succesfully"""

    test_db = empty_db

    init_db("schema.sql", test_db)
    results = test_db.query("SELECT * FROM information_schema.tables WHERE table_schema=%s",
                            ("public",))

    assert results[0]["table_name"] == "results"
    assert results[1]["table_name"] == "exam_suggestions"


def test_init_db_filled(suggestion_db):
    """Verify that initializing already filled database resets it"""

    test_db = suggestion_db

    num_entries = len(test_db.query("SELECT * FROM exam_suggestions"))
    assert num_entries > 0

    init_db("schema.sql", test_db)
    _ = test_db.query(
        "SELECT * FROM information_schema.tables WHERE table_schema=%s", ("public",))

    num_entries = len(test_db.query("SELECT * FROM exam_suggestions"))
    assert num_entries == 0
