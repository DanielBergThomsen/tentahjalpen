"""File containing all the fixtures used for mocking databases with different configurations."""

# pylint: disable=redefined-outer-name
from datetime import date
import pytest

import tentahjalpen
from tentahjalpen.db_interface import DBInterface
from db_manager import init_db


@pytest.fixture()
def empty_db(postgresql):
    """Database which hasn't even been initialized"""
    return DBInterface(test_connection=postgresql)


@pytest.fixture()
def inited_db(empty_db):
    """Database which has been initialized"""

    init_db("schema.sql", empty_db)
    return empty_db


@pytest.fixture()
def basic_db(inited_db):
    """Database which has been initialized, and filled with the following:
       EDA322, 1998-12-26, Digital Konstruktion, U=300, 3=200, 4=100, 5=10
       EDA321, 2012-12-26, Digital Design, U=200, 3=100, 4=10, 5=1"""

    test_db = inited_db
    test_db.query("INSERT INTO results (taken, code, name, failures, threes, fours, fives)"
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                  (date(1998, 12, 26), "EDA322", "Digital Konstruktion", 300, 200, 100, 10))

    test_db.query("INSERT INTO results (taken, code, name, failures, threes, fours, fives)"
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                  (date(2012, 12, 26), "EDA321", "Digital Design", 200, 100, 10, 1))

    return test_db


@pytest.fixture()
def suggestion_db(basic_db):
    """Database which has been initialized, and filled with the following:
       EDA322, 1998-12-26, Digital Konstruktion, U=300, 3=200, 4=100, 5=10
       EDA321, 2012-12-26, Digital Design, U=200, 3=100, 4=10, 5=1

       and in the exam_suggestions table:
       EDA322, 1998-12-26, exam=test.pdf
       EDA321, 2012-12-26, solution=test.pdf"""

    test_db = basic_db

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    test_db.query("INSERT INTO exam_suggestions (taken, code, exam) VALUES (%s, %s, %s)",
                  (date(1998, 12, 26), "EDA322", file_bytes))

    test_db.query("INSERT INTO exam_suggestions (taken, code, solution) VALUES (%s, %s, %s)",
                  (date(2012, 12, 26), "EDA321", file_bytes))

    return test_db


@pytest.fixture()
def filled_db(inited_db):
    """Database which has been initialized, and filled with the following:
       EDA322, 1998-12-26, Digital Konstruktion, U=300, 3=200, 4=100, 5=10, exam=test.pdf
       EDA321, 2012-12-26, Digital Design, U=200, 3=100, 4=10, 5=1, solution=test.pdf"""
    test_db = inited_db

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    test_db.query("INSERT INTO results (taken, code, name, exam, failures, threes, fours, fives)"
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                  (date(1998, 12, 26), "EDA322", "Digital Konstruktion", file_bytes,
                   300, 200, 100, 10))

    test_db.query("""INSERT INTO results
                  (taken, code, name, solution, failures, threes, fours, fives)"""
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                  (date(2012, 12, 26), "EDA321", "Digital Design", file_bytes,
                   200, 100, 10, 1))

    return test_db


@pytest.fixture
def client(filled_db):
    """Set up testing client to use when issuing requests"""

    client = tentahjalpen.create_app(test_db=filled_db).test_client()
    yield client
