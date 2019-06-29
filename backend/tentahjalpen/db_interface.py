"""
File contains both the main interface to postgres as a class, as well as a set of
convenience functions for maintaining the exam_suggestions table, initializing the
database and scraping chalmerstenta.se for new exam_suggestions automatically.
"""

import os
import webbrowser
from tabulate import tabulate
import psycopg2
import psycopg2.extras


class DBInterface: # pylint: disable=too-few-public-methods
    """Class to increase convenience in interfacing with a postgres database using the
    psycopg2 module. Connections can be established either using keyword arguments, or
    a connection URL. The class allows for effortless passing of testing databases for
    mocking purposes."""

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

        >>> query("SELECT * FROM EXAMPLE", args) # doctest: +SKIP
        [RealDictRow(["entry1", "value1"]), RealDictRow(["entry2", "value2"])]


        >>> query("SELECT * FROM EXAMPLE", None) # doctest: +SKIP
        [RealDictRow(["entry1", "value1"]), RealDictRow(["entry2", "value2"])]

        :param query: string query to execute
        :param args: tuple of strings to insert on '%s' in query
        :return: dictionary of entries
        """

        # gather connection
        connected_db = self.connection

        # create cursor reference
        cursor = connected_db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            if args is None:
                cursor.execute(query)

            # execute query safely provided string uses %s token
            else:
                cursor.execute(query, args)

            if cursor.description is not None:
                return cursor.fetchall()

            return None

        except psycopg2.DataError:
            connected_db.rollback()
            return []


def list_suggestions(connected_db):
    """Print list of current course suggestions

    >>> list_suggestions(connected_db) # doctest: +SKIP
    Code    Taken         ID
    ------  ----------  ----
    ...

    """
    exams = connected_db.query("SELECT * FROM exam_suggestions")
    for i, _ in enumerate(exams):
        suggestion_type = None
        if exams[i].get("exam", None) is not None:
            suggestion_type = "exam"
        elif exams[i].get("solution", None) is not None:
            suggestion_type = "solution"

        exams[i] = [suggestion_type, exams[i]["code"],
                    exams[i]["taken"], exams[i]["id"]]

    print(tabulate(exams, headers=["Type", "Code", "Taken", "ID"]))


def remove(suggestion_id, connected_db):
    """Remove exam suggestion from database

    >>> remove(1, connected_db) # doctest: +SKIP
    Removed ... from database


    :param id: id of exam suggestion to remove from database

    """
    try:
        entry = connected_db.query(
            "SELECT code, taken FROM exam_suggestions WHERE id=%s", (suggestion_id,))[0]
        connected_db.query(
            "DELETE FROM exam_suggestions WHERE id=%s", (suggestion_id,))
        print("Removed " + entry["code"] + " " +
              str(entry["taken"]) + " id=" + str(suggestion_id) + " from database")
    except IndexError:
        print("Entry not in database")


def remove_all(connected_db):
    """ Remove all exam suggestions from database

    >>> remove_all(connected_db) # doctest: +SKIP
    Removed ... exam suggestions from database

    """
    amount = len(connected_db.query("SELECT * FROM exam_suggestions"))
    connected_db.query(
        "DELETE FROM exam_suggestions", None)

    print("Removed " + str(amount) + " exam suggestions from database")


def approve(suggestion_id, connected_db):
    """ Approve exam suggestion and add to database

    >>> approve(1, connected_db) # doctest: +SKIP
    Added ... taken on ... to database

    :param id: id of exam suggestion to add to results in database

    """
    try:
        entry = connected_db.query(
            "SELECT * FROM exam_suggestions WHERE id=%s", (suggestion_id,))[0]
        remove(suggestion_id, connected_db)

        if entry.get("exam", None) is not None:
            connected_db.query("UPDATE results SET exam=%s WHERE code=%s AND taken=%s",
                               (entry["exam"], entry["code"], entry["taken"]))
        elif entry.get("solution", None) is not None:
            connected_db.query("UPDATE results SET solution=%s WHERE code=%s AND taken=%s",
                               (entry["solution"], entry["code"], entry["taken"]))

        print("Added " + entry["code"] + " taken on " +
              str(entry["taken"]) + " to database")
    except IndexError:
        print("Entry not in database")


def approve_all(connected_db):
    """ Approve all exam suggestions and add to database

    >>> approve_all(connected_db) # doctest: +SKIP
    Added ... exams to database

    """
    entries = connected_db.query("SELECT * FROM exam_suggestions", None)
    remove_all(connected_db)

    for entry in entries:
        if entry.get("exam", None) is not None:
            connected_db.query("UPDATE results SET exam=%s WHERE code=%s AND taken=%s",
                               (entry["exam"], entry["code"], entry["taken"]))
        elif entry.get("solution", None) is not None:
            connected_db.query("UPDATE results SET solution=%s WHERE code=%s AND taken=%s",
                               (entry["solution"], entry["code"], entry["taken"]))

    print("Added " + str(len(entries)) + " exams to database")


def show(suggestion_id, connected_db):
    """ Open file from id in webbrowser

    opens file in browser
    >>> show(1, connected_db) # doctest: +SKIP

    :param id: id of suggestion

    """
    exam = connected_db.query(
        "SELECT exam FROM exam_suggestions WHERE id=%s", (suggestion_id,))
    with open("temp.pdf", "wb") as file:
        file.write(exam[0]["exam"])
        file.close()

    webbrowser.open_new_tab("file://" + os.path.realpath("temp.pdf"))


def init_db(filename, connected_db):
    """ Initiailze database using given file containing SQL statements

    >>> init_db("mock.sql", connected_db) # doctest: +SKIP

    :param filename: name of file containing SQL to execute
    """
    with open(filename, "r") as file:
        connected_db.query(file.read())
