import sys
from tentahjalpen.db_interface import DBInterface, init_db, list, remove, remove_all, approve, approve_all, show
from tentahjalpen.scraper import scraper


def main(db):
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
            print("scrape: scrape statistics from Chalmers and PDFs from chalmerstenta.se")
            print("show ID: open file in browser")
            print("remove ID: remove entry with the given ID")
            print("remove_all: remove all entries")
            print("approve ID: approve entry with the given ID")
            print("approve_all: approve all entries")
        elif len(command) == 2 and command[0] == "init":
            init_db(command[1], db)
        elif len(command) == 1 and command[0] == "list":
            list(db)
        elif len(command) == 1 and command[0] == "remove_all":
            remove_all(db)
        elif len(command) == 1 and command[0] == "approve_all":
            approve_all(db)
        elif len(command) == 1 and command[0] == "scrape":
            print("Scraping statistics...")
            scraper.update_all(db)
            print("Scraping exam pdfs...")
            scraper.scrape_pdfs(db)
            print("Done")
        elif len(command) == 2 and command[0] == "remove":
            remove(command[1], db)
        elif len(command) == 2 and command[0] == "show":
            show(command[1], db)
        elif len(command) == 2 and command[0] == "approve":
            approve(command[1], db)
        else:
            print("Unknown command")


if __name__ == "__main__":
    db = DBInterface(url=sys.argv[1])

    print("Connection established to: " + sys.argv[1])
    main(db)
