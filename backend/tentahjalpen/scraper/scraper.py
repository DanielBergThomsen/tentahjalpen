from pathlib import Path

import pandas as pd
import requests
from dateutil.parser import parse
from .pdf_spider import PdfSpider
from scrapy.crawler import CrawlerProcess


def print_or_log(string, end="\n", app=None):
    """ Prints using stdout if no app argument is supplied, otherwise app.logger.info is used 

    :param string: string to use when printing or logging
    :param app: flask app object to use when logging
    """
    if app is None:
        print(string, end=end)
    else:
        app.logger.info(string)

def scrape_pdfs(db):
    """ Starts a scrapy CrawlerProcess with PdfSpider to extract exam pdfs from chalmerstenta.se

    :param db: DBInterface object to use when sending exam suggestions
    """
    process = CrawlerProcess()
    process.crawl(PdfSpider, db=db)
    process.start()


def update_all(db, app=None):
    """ Check if there are any updates to the exam statistics document at:
    https://document.chalmers.se/download?docid=00000000-0000-0000-0000-00001C968DC6.
    If there are, the data is extracted from the excel document and then filtered based on
    already existing entries in the database before being added.

    >>> update_all(db) # doctest: +SKIP
    ****UPDATING****
    Checking excel file...
    Updating file contents...
    Extracting from excel...
    Updating database...
    Formatting data...
    9/9
    Inserting data...
    20000/20000
    Inserted 200 entries in database

    >>> update_all(db) # doctest: +SKIP
    ****UPDATING****
    Checking excel file...
    No update necessary

    :param db: DBInterface object to use when sending exam suggestions
    """

    print_or_log("****UPDATING****", app=app)
    print_or_log("Checking excel file...", app=app)

    new_data_present = update_excel(
        "https://document.chalmers.se/download?docid=00000000-0000-0000-0000-00001C968DC6",
        "results.xlsx", app)
    if new_data_present:
        print_or_log("Extracting from excel...", app=app)
        mem = load_dataframe("results.xlsx")
        print_or_log("Updating database...", app=app)
        update_db(mem, db, app)
    else:
        print_or_log("No update necessary", app=app)


def update_excel(url, filename, app=None):
    """ Updates excel file if new data is present, if there is no local copy
    of the excel file it is also downloaded.


    >>> update_excel(url, old_filename) # doctest: +SKIP
    Updating file contents...
    True


    >>> update_excel(url, nonexistent_filename) # doctest: +SKIP
    Writing new file...
    True


    >>> update_excel(url, up_to_date_filename) # doctest: +SKIP
    Data up-to-date
    False


    :param url: URL to download the excel document from
    :param filename: filename to use for document
    :return: boolean indicating whether excel file was written or not
    """

    # fetch excel document
    results = requests.get(url, allow_redirects=True)

    # check if we have a local copy
    if Path(filename).is_file():

        # check if it's up-to-date
        with open(filename, "rb") as f:
            file_contents = f.read()
            if file_contents != results.content:
                print_or_log("Updating file contents...", app=app)
                open(filename, "wb").write(results.content)
            else:
                print_or_log("Data up-to-date", app=app)
                return False

    # write new file
    else:
        print_or_log("Writing new file...", app=app)
        open(filename, "wb").write(results.content)

    return True


def update_db(df, db, app=None):
    """ Updates database using given pandas DataFrame if the given entry
    is not already present in database

    >>> update_db(df, db) # doctest: +SKIP
    Formatting data...
    9/9
    Inserting data...
    20000/20000
    Inserted 200 entries in database


    :param df: Pandas DataFrame object containing sheets from excel document
    :param db: DBInterface object to use when sending exam suggestions
    """
    db = db

    print_or_log("Formatting data...", app=app)

    # list to keep track of filtered data
    # keys are the date with the code concatenated
    entries = {}
    i = 1
    for key, sheet in df.items():

        # print progress
        print_or_log("{}/{}".format(i, len(df.items())), end="\r", app=app)
        i += 1

        # prepare exam results from sheet period
        for index, row in sheet.iterrows():

            # skip if not exam
            if row["Provnamn"] != "Tentamen":
                continue

            # retrieve course code
            code = row["Kurs"]

            # retrieve course name
            name = row["Kursnamn"]

            # retrieve grade
            grade = row["Betyg"]

            # retrieve amount of results
            amount = row["Antal"]

            # retrieve exam date
            date = row["Provdatum"]
            if type(date) is pd.Timestamp:
                date = str(date.date())

            # necessary because of different date formats in sheets
            elif type(date) is str:
                date = str(parse(date).date())

            # if exam occasion hasn't been encountered yet, add it
            key = code + date
            if key not in entries:
                entries[key] = {
                    "taken": date,
                    "code": code,
                    "name": name,
                    "failures": 0,
                    "threes": 0,
                    "fours": 0,
                    "fives": 0,
                }

            # now modify grade that this iteration concerns in occasion
            if grade == "U":
                entries[key]["failures"] = amount
            elif grade == "3":
                entries[key]["threes"] = amount
            elif grade == "4":
                entries[key]["fours"] = amount
            elif grade == "5":
                entries[key]["fives"] = amount

    print_or_log("\nInserting data...", app=app)
    insertions = 0
    i = 1

    # go through entries and add them if they're not already present in the database
    for key, entry in entries.items():

        # print progress
        print_or_log("{}/{}".format(i, len(entries.items())), end="\r", app=app)
        i += 1

        # see if there is an entry matching the course code and exam date
        db_entry = db.query(
            "SELECT * FROM results WHERE code=%s AND taken=%s", (entry["code"], entry["taken"]))

        # if there isn't, we can insert the new result in the database
        if len(db_entry) == 0:
            insertions += 1

            db.query("INSERT INTO results (taken, code, name, failures, threes, fours, fives) "
                     "VALUES (%s,%s,%s,%s,%s,%s,%s)", (entry["taken"], entry["code"], entry["name"], entry["failures"],
                                                       entry["threes"], entry["fours"], entry["fives"]))

    print_or_log("\nInserted " + str(insertions) + " entries in database", app=app)


def load_dataframe(filename):
    """ Reads excel document and returns pandas DataFrame containing all sheets except 'Beskrivning'

    >>> load_dataframe("../results.xlsx") # doctest: +SKIP
    OrderedDict([('läsår 2010_2011', Kurs  Kursnamn                         Kursägare (program) ...
    0                               TDA341 Advanced functional programming  MPALG               ...

    :param filename: filename to use for document
    :return: Pandas DataFrame containing all sheets except one named 'Beskrivning'
    """

    # read all sheets of excel file
    sheets = pd.read_excel(filename, sheet_name=None)

    # filter description sheet
    sheets.pop("Beskrivning")
    return sheets
