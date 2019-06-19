import psycopg2
import psycopg2.extras

import os
import webbrowser
from tabulate import tabulate


class DBInterface:

    def __init__(self, **kwargs):
        """ Establish persistent connection to Postgres database using connection parameters """

        if kwargs.get("url", None) is not None:
            self.connection = psycopg2.connect(kwargs["url"])

        elif kwargs.get("test_connection", None) is not None:
            self.connection = kwargs["test_connection"]

        else:
            self.connection = psycopg2.connect(dbname=kwargs["dbname"], user=kwargs["user"],
                                               password=kwargs["password"], host=kwargs["host"],
                                               port=kwargs["port"], sslmode=kwargs["sslmode"])

        # avoid having to commit manually
        self.connection.autocommit = True

    def query(self, query, args=None):
        """ Executes query string with optional arguments

        >>> query(db, args) # doctest: +SKIP
        [RealDictRow(["entry1", "value1"]), RealDictRow(["entry2", "value2"])]


        >>> query(db, None) # doctest: +SKIP
        [RealDictRow(["entry1", "value1"]), RealDictRow(["entry2", "value2"])]


        >>> query(db, args) # doctest: +SKIP


        :param query: string query to execute
        :param args: tuple of strings to insert on '%s' in query
        :return: dictionary of entries
        """

        # gather connection
        db = self.connection

        # create cursor reference
        c = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            if args is None:
                c.execute(query)

            # execute query safely provided string uses %s token
            else:
                c.execute(query, args)

            if c.description is not None:
                return c.fetchall()

        except:
            db.rollback()
            return []


def list(db):
    """Print list of current course suggestions

    >>> list(db) # doctest: +SKIP
    Code    Taken         ID
    ------  ----------  ----
    ...

    """
    exams = db.query("SELECT * FROM exam_suggestions")
    for i in range(len(exams)):
        suggestion_type = None
        if exams[i].get("exam", None) is not None:
            suggestion_type = "exam"
        elif exams[i].get("solution", None) is not None:
            suggestion_type = "solution"

        exams[i] = [suggestion_type, exams[i]["code"],
                    exams[i]["taken"], exams[i]["id"]]

    print(tabulate(exams, headers=["Type", "Code", "Taken", "ID"]))


def remove(id, db):
    """Remove exam suggestion from database

    >>> remove(1, db) # doctest: +SKIP
    Removed ... from database


    :param id: id of exam suggestion to remove from database

    """
    try:
        entry = db.query(
            "SELECT code, taken FROM exam_suggestions WHERE id=%s", (id,))[0]
        db.query(
            "DELETE FROM exam_suggestions WHERE id=%s", (id,))
        print("Removed " + entry["code"] + " " +
              str(entry["taken"]) + " id=" + str(id) + " from database")
    except IndexError:
        print("Entry not in database")


def remove_all(db):
    """ Remove all exam suggestions from database

    >>> remove_all(db) # doctest: +SKIP
    Removed ... exam suggestions from database

    """
    amount = len(db.query("SELECT * FROM exam_suggestions"))
    db.query(
        "DELETE FROM exam_suggestions", None)

    print("Removed " + str(amount) + " exam suggestions from database")


def approve(id, db):
    """ Approve exam suggestion and add to database

    >>> approve(1, db) # doctest: +SKIP
    Added ... taken on ... to database

    :param id: id of exam suggestion to add to results in database

    """
    try:
        entry = db.query(
            "SELECT * FROM exam_suggestions WHERE id=%s", (id,))[0]
        remove(id, db)

        if entry.get("exam", None) is not None:
            db.query("UPDATE results SET exam=%s WHERE code=%s AND taken=%s",
                     (entry["exam"], entry["code"], entry["taken"]))
        elif entry.get("solution", None) is not None:
            db.query("UPDATE results SET solution=%s WHERE code=%s AND taken=%s",
                     (entry["solution"], entry["code"], entry["taken"]))

        print("Added " + entry["code"] + " taken on " +
              str(entry["taken"]) + " to database")
    except IndexError:
        print("Entry not in database")


def approve_all(db):
    """ Approve all exam suggestions and add to database

    >>> approve_all(db) # doctest: +SKIP
    Added ... exams to database

    """
    entries = db.query("SELECT * FROM exam_suggestions", None)
    remove_all(db)

    for entry in entries:
        if entry.get("exam", None) is not None:
            db.query("UPDATE results SET exam=%s WHERE code=%s AND taken=%s",
                     (entry["exam"], entry["code"], entry["taken"]))
        elif entry.get("solution", None) is not None:
            db.query("UPDATE results SET solution=%s WHERE code=%s AND taken=%s",
                     (entry["solution"], entry["code"], entry["taken"]))

    print("Added " + str(len(entries)) + " exams to database")


def show(id, db):
    """ Open file from id in webbrowser

    opens file in browser
    >>> show(1, db) # doctest: +SKIP

    :param id: id of suggestion

    """
    exam = db.query(
        "SELECT exam FROM exam_suggestions WHERE id=%s", (id,))
    with open("temp.pdf", "wb") as f:
        f.write(exam[0]["exam"])
        f.close()

    webbrowser.open_new_tab("file://" + os.path.realpath("temp.pdf"))


def init_db(filename, db):
    """ Initiailze database using given file containing SQL statements

    >>> init_db("mock.sql", db) # doctest: +SKIP

    :param filename: name of file containing SQL to execute
    """
    with open(filename, "r") as f:
        db.query(f.read())
