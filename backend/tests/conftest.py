import pytest

from db_manager import init_db
from tentahjalpen.db_interface import DBInterface
from datetime import date


@pytest.fixture()
def empty_db(postgresql):
    return DBInterface(test_connection=postgresql)


@pytest.fixture()
def inited_db(empty_db):

    init_db("schema.sql", empty_db)
    return empty_db


@pytest.fixture()
def basic_db(inited_db):

    db = inited_db
    db.query("INSERT INTO results (taken, code, name, failures, threes, fours, fives)"
             "VALUES (%s,%s,%s,%s,%s,%s,%s)",
             (date(1998, 12, 26), "EDA322", "Digital Konstruktion", 300, 200, 100, 10))

    db.query("INSERT INTO results (taken, code, name, failures, threes, fours, fives)"
             "VALUES (%s,%s,%s,%s,%s,%s,%s)",
             (date(2012, 12, 26), "EDA321", "Digital Design", 200, 100, 10, 1))

    return db


@pytest.fixture()
def suggestion_db(basic_db):

    db = basic_db

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    db.query("INSERT INTO exam_suggestions (taken, code, exam) VALUES (%s, %s, %s)",
             (date(1998, 12, 26), "EDA322", file_bytes))

    db.query("INSERT INTO exam_suggestions (taken, code, solution) VALUES (%s, %s, %s)",
             (date(2012, 12, 26), "EDA321", file_bytes))

    return db


@pytest.fixture()
def filled_db(inited_db):

    db = inited_db

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    db.query("INSERT INTO results (taken, code, name, exam, failures, threes, fours, fives)"
             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
             (date(1998, 12, 26), "EDA322", "Digital Konstruktion", file_bytes, 300, 200, 100, 10))

    db.query("INSERT INTO results (taken, code, name, solution, failures, threes, fours, fives)"
             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
             (date(2012, 12, 26), "EDA321", "Digital Design", file_bytes, 200, 100, 10, 1))

    return db
