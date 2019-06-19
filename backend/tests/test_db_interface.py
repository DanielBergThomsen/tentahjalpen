from tentahjalpen.db_interface import list, remove, remove_all, approve, approve_all, init_db


def test_list(suggestion_db, capfd):
    """Verify that the function actually lists all entries in exam_suggestions table"""

    db = suggestion_db

    list(db)
    out, err = capfd.readouterr()

    assert "EDA322" in out
    assert "1998-12-26" in out
    assert "exam" in out
    assert "EDA321" in out
    assert "2012-12-26" in out
    assert "solution" in out

def test_list_empty(inited_db, capfd):
    """Verify that the function doesn't list anything any courses"""

    db = inited_db

    list(db)
    out, err = capfd.readouterr()

    assert "exam" not in out
    assert "solution" not in out


def test_remove(suggestion_db):
    """Verify that the function actually removes the entry in exam_suggestions table"""

    db = suggestion_db

    entry = db.query("SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]
    remove(entry["id"], db)

    matching = db.query("SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))
    assert len(matching) == 0

def test_remove_invalid(suggestion_db):
    """Verify that the function doesn't remove anything when attempting to remove something
    that doesn't exist"""

    db = suggestion_db

    entry = db.query("SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]
    remove("MEM420", db)

    matching = db.query("SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))
    assert len(matching) == 1


def test_remove_all(suggestion_db):
    """Verify that the function actually removes all entries in exam_suggestions table"""

    db = suggestion_db

    num_entries = len(db.query("SELECT * FROM exam_suggestions"))
    assert num_entries > 0

    remove_all(db)
    num_entries = len(db.query("SELECT * FROM exam_suggestions"))
    assert num_entries == 0

def test_remove_all_empty(inited_db):
    """Verify that the function doesn't crash when running on empty table"""

    db = inited_db
    remove_all(db)


def test_approve(suggestion_db):
    """Verify that the function actually inserts the entry in exam_suggestions table into the results table,
        and that the suggestion is then removed from exam_suggestions"""

    db = suggestion_db

    r_entry = db.query("SELECT * FROM results WHERE code=%s", ("EDA322",))[0]
    assert r_entry["exam"] is None

    es_entry = db.query("SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]
    pdf = es_entry["exam"]
    approve(es_entry["id"], db)

    es_entry = db.query("SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))
    assert len(es_entry) == 0

    r_entry = db.query("SELECT * FROM results WHERE code=%s", ("EDA322",))[0]
    assert r_entry["exam"] == pdf


def test_approve_invalid(basic_db):
    """Verify that the function actually inserts the entry in exam_suggestions table into the results table,
        and that the suggestion is then removed from exam_suggestions"""

    db = basic_db

    approve(1, db)

    entries = db.query("SELECT * FROM results WHERE exam IS NOT NULL")
    assert len(entries) == 0


def test_approve_all(suggestion_db):
    """Verify that the function actually approves all entries in exam_suggestions table"""

    db = suggestion_db

    r_entries = db.query("SELECT * FROM results")
    assert len(r_entries) > 0
    for entry in r_entries:
        assert entry["exam"] is None

    es_entries = db.query("SELECT * FROM exam_suggestions")
    pdfs = [entry["exam"] for entry in es_entries]
    approve_all(db)

    es_entries = db.query("SELECT * FROM exam_suggestions")
    assert len(es_entries) == 0

    r_entries = db.query("SELECT * FROM results")
    for i in range(len(r_entries)):
        assert r_entries[i]["exam"] == pdfs[i]

def test_approve_all_empty(basic_db):
    """Verify that the function doesn't crash when running on empty table"""

    db = basic_db
    approve_all(db)


def test_init_db(empty_db):
    """Verify that the tables for the results and exam_suggestions are generated succesfully"""

    db = empty_db

    init_db("schema.sql", db)
    results = db.query("SELECT * FROM information_schema.tables WHERE table_schema=%s", ("public",))

    assert results[0]["table_name"] == "results"
    assert results[1]["table_name"] == "exam_suggestions"

def test_init_db_filled(suggestion_db):
    """Verify that initializing already filled database resets it"""

    db = suggestion_db

    num_entries = len(db.query("SELECT * FROM exam_suggestions"))
    assert num_entries > 0

    init_db("schema.sql", db)
    results = db.query("SELECT * FROM information_schema.tables WHERE table_schema=%s", ("public",))

    num_entries = len(db.query("SELECT * FROM exam_suggestions"))
    assert num_entries == 0
