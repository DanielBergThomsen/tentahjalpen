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
