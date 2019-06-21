import os
import io
import base64

from flask import Flask, make_response, Response, jsonify, abort, send_file, url_for, request, session
from flask_cors import CORS
from flask_apscheduler import APScheduler
from .db_interface import DBInterface, init_db
from .scraper import scraper


def create_app(production=False, test_db=None):

    # make it possible to create config.py in root of backend to override environment-specific settings
    app = Flask(__name__, instance_relative_config=True)

    # DBInterface instance used for all database operations
    db = None

    def update():
        """ Update database using scraper.update_all and update jsoned_course_list to include any new entries """

        # update database
        with app.app_context():
            scraper.update_all(db)

    def init():
        """ Check if database is initialized, initialize if necessary and update afterwards """

        app.logger.info("Checking if database is initialized...")
        entries = db.query("SELECT * FROM results")

        if len(entries) == 0:
            app.logger.info("Initializing database...")
            init_db("schema.sql", db)

        update()

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

        # configuration used to setup Flask-APScheduler to call update() every night at 02:01 (GMT+2)
        JOBS=[
            {
                "id": "update db data",
                "func": update,
                "trigger": "cron",
                "year": "*",
                "month": "*",
                "day": "*",
                "hour": 2,
                "minute": 1,
                "second": 0,
            }
        ],
        SCHEDULER_API_ENABLED=True,
        SCHEDULER_TIMEZONE="Europe/Stockholm"
    )

    if production:

        # connect to postgres using environment variables
        db = DBInterface(url=os.environ["DATABASE_URL"])

    elif test_db is None:

        # connect to postgres
        db = DBInterface(dbname=app.config["DB_NAME"], user=app.config["DB_USER"], password=app.config["DB_PASSWD"],
                         host=app.config["DB_HOST"], port=app.config["DB_PORT"], sslmode=app.config["SSL"])

        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)

    else:

        # load the test database
        db = test_db

    # allow CORS headers
    CORS(app)

    # only run update and init if not running tests
    if test_db is None:
        # start scheduler for updates
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()

        # perform manual check of database on startup
        init()

    @app.route("/courses", methods=["GET"])
    def get_courses():
        """ Return list of courses with different course codes

        >>> get_courses() # doctest: +ELLIPSIS
        '[...]'

        :return: string of JSONed course list
        """

        entries = db.query("SELECT DISTINCT ON (code) code, name FROM results")

        app.logger.info("Sending course list")
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
        entries = db.query(
            "SELECT exam, solution, failures, threes, fours, fives, taken, name, code FROM results "
            "WHERE code=%s ORDER BY taken",
            (code,))

        # there were no matches on the course code
        if len(entries) == 0:
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

        app.logger.info("Responding to request for %s", code)
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
        entries = db.query(
            "SELECT exam FROM results WHERE code=%s AND taken=%s", (code, date))
        if not entries or entries[0]["exam"] == None:
            abort(404)

        app.logger.info(
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
        entries = db.query(
            "SELECT solution FROM results WHERE code=%s AND taken=%s", (code, date))
        if not entries or entries[0]["solution"] == None:
            abort(404)

        app.logger.info(
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
        if "exam" in content and type(content["exam"]) is not str:
            abort(400)

        # check that the exam exists
        exam = db.query(
            "SELECT exam FROM results WHERE code=%s AND taken=%s", (code, date))
        if len(exam) <= 0:
            abort(404)

        # check if exam file is already present
        if exam[0]["exam"] is not None:
            abort(409)  # conflict

        # convert base64 into bytes object
        decoded = base64.b64decode(content["exam"])

        # insert binary data as an exam suggestion
        db.query(
            "INSERT INTO exam_suggestions (taken, code, exam) VALUES (%s, %s, %s)",
            (date, code, decoded))

        app.logger.info("Inserting exam suggestion for code %s", code)
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
        if "solution" in content and type(content["solution"]) is not str:
            abort(400)

        # check that the exam exists
        exam = db.query(
            "SELECT solution FROM results WHERE code=%s AND taken=%s", (code, date))
        if len(exam) <= 0:
            abort(404)

        # check if exam file is already present
        if exam[0]["solution"] is not None:
            abort(409)  # conflict

        # convert base64 into bytes object
        decoded = base64.b64decode(content["solution"])

        # insert binary data as an exam suggestion
        db.query(
            "INSERT INTO exam_suggestions (taken, code, solution) VALUES (%s, %s, %s)",
            (date, code, decoded))

        app.logger.info("Inserting solution suggestion for code %s", code)
        return Response(status=200)

    @app.errorhandler(400)
    def conflict(error):
        """ Return JSON response indicating that a bad request was performed (400) """

        app.logger.error("BAD REQUEST: %s", request.url)
        return make_response(jsonify({"error": "Bad request"}), 400)

    @app.errorhandler(404)
    def not_found(error):
        """ Return JSON response indicating that the resource wasn't found (404)"""

        app.logger.error("RESOURCE NOT FOUND: %s", request.url)
        return make_response(jsonify({"error": "Not found"}), 404)

    @app.errorhandler(409)
    def conflict(error):
        """ Return JSON response indicating that the resource already exists (409)"""

        app.logger.error("RESOURCE ALREADY EXISTS: %s", request.url)
        return make_response(jsonify({"error": "Resource already present"}), 409)

    return app
