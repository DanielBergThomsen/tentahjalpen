"""This module will only test non-convenience functions of the scraper package as these are just comprised of calls
to these more basic functions. Furthermore I have decided to omit scrape_pdfs as mocking chalmerstenta.se is low in the
 list of priorities as of current."""

from tentahjalpen.scraper.scraper import update_excel, update_db, load_dataframe
from pathlib import Path


def test_update_excel(tmpdir):
    """Verify that the function actually downloads the file"""

    file = str(tmpdir / "results.xlsx")
    assert not Path(file).is_file()

    update_excel(
        "https://document.chalmers.se/download?docid=00000000-0000-0000-0000-00001C968DC6",
        file)
    assert Path(file).is_file()


def test_load_dataframe():
    """Verify that the dataframe contains at least one of the courses it should"""

    df = load_dataframe("tests/test.xlsx")
    data = df["läsår_2017_2018"]
    assert len(data.loc[data["Kurs"] == "EDA322"]) > 0


def test_load_dataframe_no_description():
    """Verify that the 'Beskrivning' sheet is removed from the dataframe"""

    df = load_dataframe("tests/test.xlsx")
    assert "Beskrivning" not in df.keys()


def test_update_db(inited_db):
    """Verify that an entry is added for the arbitrary course EDA322.
        Presupposes that load_dataframe() is working properly"""

    db = inited_db
    entries = db.query("SELECT * from results WHERE code=%s", ("EDA322",))
    assert(len(entries) == 0)

    df = load_dataframe("tests/test.xlsx")
    update_db(df, db)
    entries = db.query("SELECT * from results WHERE code=%s", ("EDA322",))
    assert(len(entries) > 0)
