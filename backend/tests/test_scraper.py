"""This module will only test non-convenience functions of the scraper package as these are just
comprised of calls to these more basic functions. Furthermore I have decided to omit scrape_pdfs
as mocking chalmerstenta.se is low in the list of priorities as of current."""

from tentahjalpen.scraper.scraper import update_db, load_dataframe


def test_load_dataframe():
    """Verify that the dataframe contains at least one of the courses it should"""

    dataframe = load_dataframe("tests/test.xlsx")
    data = dataframe["läsår_2017_2018"]
    assert not data.loc[data["Kurs"] == "EDA322"].empty


def test_load_dataframe_no_description():
    """Verify that the 'Beskrivning' sheet is removed from the dataframe"""

    dataframe = load_dataframe("tests/test.xlsx")
    assert "Beskrivning" not in dataframe.keys()


def test_update_db(inited_db):
    """Verify that an entry is added for the arbitrary course EDA322.
        Presupposes that load_dataframe() is working properly"""

    test_db = inited_db
    entries = test_db.query("SELECT * from results WHERE code=%s", ("EDA322",))
    assert not entries

    dataframe = load_dataframe("tests/test.xlsx")
    update_db(dataframe, test_db)
    entries = test_db.query("SELECT * from results WHERE code=%s", ("EDA322",))
    assert entries
