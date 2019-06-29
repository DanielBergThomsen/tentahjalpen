"""
Executing this class starts a REPL session wherein the user may show, remove or approve
the entries in the exam_suggestions table. The user may also scrape chalmerstenta.se
for new exam suggestions which then get added to the exam_suggestions table for further
investigation. It is also possible to initialize the database from here. When executing
this file a postgresql connection URL is expected as the first argument.

Example usage:

>>> python database_manager.py postgres://user:password@host:5432/database # doctest: +SKIP
"""


import sys
from tentahjalpen.db_interface import DBInterface, init_db, list_suggestions
from tentahjalpen.db_interface import remove, remove_all, approve, approve_all, show
from tentahjalpen.scraper import scraper


def main(connected_db):
    """Enter interactive session where commands can
    be issued and their effects are printed in context

    >>> main(db) # doctest: +SKIP
    Issue command 'help' to print a list of commands
    >help
    Available commands:
    init FILENAME: initialize table using given file and scrape exam data
    list: print table of exam suggestions in database
    scrape: scrape statistics from Chalmers and PDFs from chalmerstenta.se
    show ID: open file in browser
    remove ID: remove entry with the given ID
    remove_all: remove all entries
    approve ID: approve entry with the given ID
    approve_all: approve all entries

    ...

    """
    print("Issue 'help' to print a list of commands")
    while True:
        command = input(">").split()
        if len(command) == 1 and command[0] == "help":
            print("Available commands:")
            print("init FILENAME: initialize table using given file and scrape exam data")
            print("list: print table of exam suggestions in database")
            print(
                "scrape: scrape statistics from Chalmers and PDFs from chalmerstenta.se")
            print("show ID: open file in browser")
            print("remove ID: remove entry with the given ID")
            print("remove_all: remove all entries")
            print("approve ID: approve entry with the given ID")
            print("approve_all: approve all entries")
        elif len(command) == 2 and command[0] == "init":
            init_db(command[1], connected_db)
        elif len(command) == 1 and command[0] == "list":
            list_suggestions(connected_db)
        elif len(command) == 1 and command[0] == "remove_all":
            remove_all(connected_db)
        elif len(command) == 1 and command[0] == "approve_all":
            approve_all(connected_db)
        elif len(command) == 1 and command[0] == "scrape":
            print("Scraping statistics...")
            scraper.update_all(connected_db)
            print("Scraping exam pdfs...")
            scraper.scrape_pdfs(connected_db)
            print("Done")
        elif len(command) == 2 and command[0] == "remove":
            remove(command[1], connected_db)
        elif len(command) == 2 and command[0] == "show":
            show(command[1], connected_db)
        elif len(command) == 2 and command[0] == "approve":
            approve(command[1], connected_db)
        else:
            print("Unknown command")


if __name__ == "__main__":
    CONNECTED_DB = DBInterface(url=sys.argv[1])

    print("Connection established to: " + sys.argv[1])
    main(CONNECTED_DB)
