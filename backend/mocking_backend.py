from datetime import date

from tentahjalpen.__init__ import create_app
from tentahjalpen.db_interface import DBInterface, init_db
import testing.postgresql

with testing.postgresql.Postgresql() as test_server:
    test_db = DBInterface(test_connection_url=test_server.url())
    init_db("schema.sql", test_db)
    test_db.query("INSERT INTO results (taken, code, name, failures, threes, fours, fives)"
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                  (date(1998, 12, 26), "EDA322", "Digital Konstruktion", 300, 200, 100, 10))

    app = create_app(test_db=test_db)
    app.run()
