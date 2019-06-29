"""Functional tests for all operations of the API"""

from base64 import b64encode
from flask import json


def test_get_courses(client):
    """Verify that all courses are present"""

    resp = client.get("/courses")
    data = json.loads(resp.data)
    assert data[0]["code"] == "EDA321"
    assert data[1]["code"] == "EDA322"


def test_get_course(client):
    """Verify that all fields of course EDA322 are accessible"""

    resp = client.get("/courses/EDA322")
    data = json.loads(resp.data)[0]

    assert data["code"] == "EDA322"
    assert data["name"] == "Digital Konstruktion"
    assert data["taken"] == "1998-12-26"
    assert data["failures"] == 300
    assert data["threes"] == 200
    assert data["fours"] == 100
    assert data["fives"] == 10
    assert data["exam"] == "http://localhost/courses/EDA322/1998-12-26/exam"


def test_get_course_non_existent(client):
    """Verify that the server responds with 404 when accessing non-existent course"""

    resp = client.get("/courses/MEM123")
    data = json.loads(resp.data)

    assert data["error"] == "Not found"


def test_get_exam(client):
    """Verify that exam of course EDA322 are accessible,
        this is done by first requesting the course manually, and then using the given URI"""

    resp = client.get("/courses/EDA322")
    data = json.loads(resp.data)[0]

    assert data["exam"] is not None

    resp = client.get(data["exam"])
    assert resp.data == open("tests/test.pdf", "rb").read()


def test_get_exam_non_existent(client):
    """Verify that we are given a 404 when accessing non-existent exam"""

    resp = client.get("/courses/EDA322/2022-12-12/exam")
    data = json.loads(resp.data)

    assert data["error"] == "Not found"


def test_get_solution(client):
    """Verify that solution for exam of course EDA322 are accessible,
        this is done by first requesting the course manually, and then using the given URI"""

    resp = client.get("/courses/EDA321")
    data = json.loads(resp.data)[0]

    assert data["solution"] is not None

    resp = client.get(data["solution"])
    assert resp.data == open("tests/test.pdf", "rb").read()


def test_get_solution_non_existent(client):
    """Verify that we are given a 404 when accessing non-existent solution"""

    resp = client.get("/courses/EDA321/2022-12-12/solution")
    data = json.loads(resp.data)

    assert data["error"] == "Not found"


def test_put_suggestion(client, filled_db):
    """Verify that we can post an exam suggestion that gets added to the suggestion database"""

    test_db = filled_db

    entry = test_db.query("SELECT * FROM results WHERE code=%s", ("EDA321",))[0]
    assert entry["exam"] is None

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    # base64 encode exam
    encoded = b64encode(file_bytes).decode("utf-8")

    client.put("/courses/EDA321/2012-12-26/exam", json={
        "exam": encoded
    })

    entry = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA321",))[0]

    assert bytes(entry["exam"]) == file_bytes


def test_put_suggestion_non_existent(client):
    """Verify that we get a 404 when trying to upload an exam to a non-existent course"""

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    # base64 encode exam
    encoded = b64encode(file_bytes).decode("utf-8")

    resp = client.put("/courses/MEM123/2012-12-26/exam", json={
        "exam": encoded
    })
    data = json.loads(resp.data)

    assert data["error"] == "Not found"


def test_put_suggestion_conflict(client):
    """Verify that we get a 409 when trying to upload an exam that already exists"""

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    # base64 encode exam
    encoded = b64encode(file_bytes).decode("utf-8")

    resp = client.put("/courses/EDA322/1998-12-26/exam", json={
        "exam": encoded
    })
    data = json.loads(resp.data)

    assert data["error"] == "Resource already present"


def test_put_solution_suggestion(client, filled_db):
    """Verify that we can post a solution suggestion that gets added to the suggestion database"""

    test_db = filled_db

    entry = test_db.query("SELECT * FROM results WHERE code=%s", ("EDA322",))[0]
    assert entry["solution"] is None

    # get test.pdf file to use for mocking exam solution
    file_bytes = open("tests/test.pdf", "rb").read()

    # base64 encode exam
    encoded = b64encode(file_bytes).decode("utf-8")

    client.put("/courses/EDA322/1998-12-26/solution", json={
        "solution": encoded
    })

    entry = test_db.query(
        "SELECT * FROM exam_suggestions WHERE code=%s", ("EDA322",))[0]

    assert bytes(entry["solution"]) == file_bytes


def test_put_solution_suggestion_non_existent(client):
    """Verify that we get a 404 when trying to upload a solution to a non-existent course"""

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    # base64 encode exam
    encoded = b64encode(file_bytes).decode("utf-8")

    resp = client.put("/courses/MEM123/2012-12-26/solution", json={
        "solution": encoded
    })
    data = json.loads(resp.data)

    assert data["error"] == "Not found"


def test_put_solution_suggestion_conflict(client):
    """Verify that we get a 409 when trying to upload a solution that already exists"""

    # get test.pdf file to use for mocking exam suggestions
    file_bytes = open("tests/test.pdf", "rb").read()

    # base64 encode exam
    encoded = b64encode(file_bytes).decode("utf-8")

    resp = client.put("/courses/EDA321/2012-12-26/solution", json={
        "solution": encoded
    })
    data = json.loads(resp.data)

    assert data["error"] == "Resource already present"
