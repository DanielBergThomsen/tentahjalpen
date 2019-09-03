"""
The application factory for the Tentahjälpen backend. Here the initial configuration for
the application is sourced, and any eventual testing or production specific logic is found
here.
"""

import os
import io
import base64

from flask import Flask, make_response, Response, jsonify, abort, send_file, url_for
from flask import request, session
from flask.logging import create_logger
from flask_cors import CORS
from .db_interface import DBInterface, init_db
from .scraper import scraper


# pylint is disabled temporarily as functions will be moved to blueprint class at a later point
# pylint: disable-all
def create_app(production=False, test_db=None):
    """Create Flask application object from given configuration.

    :param production: boolean that changes the connection parameter to use environment variable
    DATABASE_URL to connect to the database
    :param test_db: testing database passed to DBInterface class and used when querying everything
    """

    # make it possible to create config.py in root of backend to override
    # environment-specific settings
    app = Flask(__name__, instance_relative_config=True)
    logger = create_logger(app)

    # DBInterface instance used for all database operations
    connected_db = None

    def init():
        """Check if database is initialized and initialize if necessary."""

        logger.info("Checking if database is initialized...")
        entries = connected_db.query("SELECT * FROM results")

        if not entries:
            logger.info("Initializing database...")
            init_db("schema.sql", connected_db)

    # provide default configs for app
    # some of these should be overridden in config.py
    app.config.from_mapping(

        # allow utf-8 encoding
        JSON_AS_ASCII=False,

        # database defaults
        DB_NAME="courseData",
        DB_USER="postgres",
        DB_PASSWD="toor",
        DB_HOST="localhost",
        DB_PORT=5432,
        SSL="disable",
    )

    if production:

        # connect to postgres using environment variables
        connected_db = DBInterface(url=os.environ["DATABASE_URL"])

    elif test_db is None:

        # connect to postgres
        connected_db = DBInterface(dbname=app.config["DB_NAME"],
                                   user=app.config["DB_USER"],
                                   password=app.config["DB_PASSWD"],
                                   host=app.config["DB_HOST"],
                                   port=app.config["DB_PORT"],
                                   sslmode=app.config["SSL"])

        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)

    else:

        # load the test database
        connected_db = test_db

    # allow CORS headers
    CORS(app)

    # only run init if not running tests
    if test_db is None:

        # perform manual check of database on startup
        init()

    @app.route("/courses", methods=["GET"])
    def get_courses():
        """ Return list of courses with different course codes

        >>> get_courses() # doctest: +ELLIPSIS
        '[...]'

        :return: string of JSONed course list
        """

        entries = connected_db.query(
            "SELECT DISTINCT ON (code) code, name FROM results")

        logger.info("Sending course list")
        return jsonify(entries)

    # return list of results by date from given course code
    @app.route("/courses/<string:code>", methods=["GET"])
    def get_course(code):
        """ Return all exam results associated with the given course code

        >>> get_course("EDA322") # doctest: +SKIP
        [
            {
                "code": "EDA322",
                "exam": "http://localhost:5000/exams/1989",
                "solution": "http://localhost:5000/exams/1337",
                "failures": 33,
                "fives": 5,
                "fours": 15,
                "name": "Digital konstruktion",
                "taken": "2014-03-12",
                "threes": 39
            },
        ...
        ]

        :param code: the course code used to query results
        :return: JSONed dictionary of exam results
        """

        # perform query using given course code
        # safe since using %s protects from SQL injections
        entries = connected_db.query(
            "SELECT exam, solution, failures, threes, fours, fives, taken, name, code FROM results "
            "WHERE code=%s ORDER BY taken",
            (code,))

        # there were no matches on the course code
        if not entries:
            abort(404)

        # format the entries nicely
        for entry in entries:

            # necessary since jsoned version of datetime has timestamp
            entry["taken"] = str(entry["taken"])

            # give easy access to exam pdf
            if entry["exam"] is not None:
                entry["exam"] = url_for(
                    "get_exam", code=code, date=entry["taken"], _external=True)

            # give easy access to solution pdf
            if entry["solution"] is not None:
                entry["solution"] = url_for(
                    "get_solution", code=code, date=entry["taken"], _external=True)

        logger.info("Responding to request for %s", code)
        return jsonify(entries)

    @app.route("/courses/<string:code>/<string:date>/exam", methods=["GET"])
    def get_exam(code, date):
        """ Get exam PDF using code and date taken

        >>> get_exam("EDA322", "1989-12-26") # doctest: +SKIP
        <Response streamed [200 OK]>


        :param code: course code of course
        :param date: date when exam was taken
        :return: response containing exam pdf
        """
        entries = connected_db.query(
            "SELECT exam FROM results WHERE code=%s AND taken=%s", (code, date))
        if not entries or entries[0]["exam"] is None:
            abort(404)

        logger.info(
            "Responding to request for exam in course %s taken on %s", code, date)
        return send_file(io.BytesIO(entries[0]["exam"]), mimetype="application/pdf")

    @app.route("/courses/<string:code>/<string:date>/solution", methods=["GET"])
    def get_solution(code, date):
        """ Get solution PDF using code and date taken

        >>> get_solution("EDA322", "1989-12-26") # doctest: +SKIP
        <Response streamed [200 OK]>


        :param code: course code of course
        :param date: date when exam was taken
        :return: response containing exam pdf
        """
        entries = connected_db.query(
            "SELECT solution FROM results WHERE code=%s AND taken=%s", (code, date))
        if not entries or entries[0]["solution"] is None:
            abort(404)

        logger.info(
            "Responding to request for solution in course %s taken on %s", code, date)
        return send_file(io.BytesIO(entries[0]["solution"]), mimetype="application/pdf")

    # submit exam pdf suggestion in base64 encoding
    @app.route("/courses/<string:code>/<string:date>/exam", methods=["PUT"])
    def put_suggestion(code, date):
        """ Submit exam PDF suggestion in base64 encoding to exam suggestions table

        >>> put_suggestion(code, date) # doctest: +SKIP
        <Response 0 bytes [200 OK]>


        :param code: course code for the exam
        :return: empty response with response code indicating success of operation
        """
        content = request.json

        # make sure data is non-empty
        if not content:
            abort(400)

        # we need the actual exam, and it should also be a string
        if "exam" in content and not isinstance(content["exam"], str):
            abort(400)

        # check that the exam exists
        exam = connected_db.query(
            "SELECT exam FROM results WHERE code=%s AND taken=%s", (code, date))
        if not exam:
            abort(404)

        # check if exam file is already present
        if exam[0]["exam"] is not None:
            abort(409)  # conflict

        # convert base64 into bytes object
        decoded = base64.b64decode(content["exam"])

        # insert binary data as an exam suggestion
        connected_db.query(
            "INSERT INTO exam_suggestions (taken, code, exam) VALUES (%s, %s, %s)",
            (date, code, decoded))

        logger.info("Inserting exam suggestion for code %s", code)
        return Response(status=200)

    # submit solution pdf suggestion in base64 encoding
    @app.route("/courses/<string:code>/<string:date>/solution", methods=["PUT"])
    def put_solution_suggestion(code, date):
        """ Submit exam solution PDF suggestion in base64 encoding to exam suggestions table

        >>> put_solution_suggestion(code, date) # doctest: +SKIP
        <Response 0 bytes [200 OK]>


        :param code: course code for the exam
        :return: empty response with response code indicating success of operation
        """
        content = request.json

        # make sure data is non-empty
        if not content:
            abort(400)

        # we need the actual pdf, and it should also be a string
        if "solution" in content and not isinstance(content["solution"], str):
            abort(400)

        # check that the exam exists
        exam = connected_db.query(
            "SELECT solution FROM results WHERE code=%s AND taken=%s", (code, date))
        if not exam:
            abort(404)

        # check if exam file is already present
        if exam[0]["solution"] is not None:
            abort(409)  # conflict

        # convert base64 into bytes object
        decoded = base64.b64decode(content["solution"])

        # insert binary data as an exam suggestion
        connected_db.query(
            "INSERT INTO exam_suggestions (taken, code, solution) VALUES (%s, %s, %s)",
            (date, code, decoded))

        logger.info("Inserting solution suggestion for code %s", code)
        return Response(status=200)

    @app.errorhandler(400)
    def bad_request(_):
        """Return JSON response indicating that a bad request was performed (400)"""

        logger.error("BAD REQUEST: %s", request.url)
        return make_response(jsonify({"error": "Bad request"}), 400)

    @app.errorhandler(404)
    def not_found(_):
        """Return JSON response indicating that the resource wasn't found (404)"""

        logger.error("RESOURCE NOT FOUND: %s", request.url)
        return make_response(jsonify({"error": "Not found"}), 404)

    @app.errorhandler(409)
    def conflict(_):
        """Return JSON response indicating that the resource already exists (409)"""

        logger.error("RESOURCE ALREADY EXISTS: %s", request.url)
        return make_response(jsonify({"error": "Resource already present"}), 409)

    return app
