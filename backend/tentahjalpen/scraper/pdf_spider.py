import re
from dateutil.parser import parse

from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class PdfSpider(CrawlSpider):
    """ Scrapy CrawlSpider used for scraping exam PDFs from chalmerstenta.se """

    name = "exam_pdfs"

    allowed_domains = ["chalmerstenta.se"]
    start_urls = ["https://chalmerstenta.se/?page=listcourse"]

    rules = (
        Rule(LinkExtractor(allow=("\?kurs\=.*")), callback="parse_course"),
    )

    def __init__(self, *args, **kwargs):
        """ Instantiates spider and saves DBInterface instance for use when submitting exams to database
        Arguments are passed into CrawlSpider constructor, and argument db is used for DBInterface instance """

        super(PdfSpider, self).__init__(*args, **kwargs)
        self.db = kwargs["db"]

    def parse_course(self, response):
        """ Checks whether given response is of a page containing a course PDF that corresponds to an entry in the
        database """

        # select rows from DOM
        rows = response.xpath("//table//table/child::*")

        # check that there is data present
        if len(rows) <= 2:
            self.log("No entries")
            return

        # gather and clean title of course using url
        title = response.url.split("kurs=")[-1].split("_")
        title = " ".join(title)

        # check if there is a course code present
        # regex for three uppercase letters followed by three digits
        code = re.search("[A-Z]{3}[0-9]{3}", title)

        # there was a match for the expression
        if code is not None:
            code = code.group(0)

            # search to see if course is in database
            matches = self.db.query(
                "SELECT * FROM results WHERE code=%s", (code,))

            # no match
            if len(matches) <= 0:
                self.log("Course not in database")
                return

        # no code present, search for name as last-ditch effort
        else:
            matches = self.db.query(
                "SELECT DISTINCT ON (code) code FROM results WHERE name=%s", (title,))

            # as long as there is a match and no ambivalence, use result
            if len(matches) != 1:
                self.log("Either course not found in database, or several matches")
                return

            # set course code for when submitting exam suggestion later
            code = matches[0]["code"]

        # iterate over table rows
        # start at the index 2 since the first two entries are just the title of the course and columns
        for row in rows[2:]:

            # now find table cell
            data = row.xpath("td")

            # skip if empty
            if len(data) <= 0:
                continue

            # gather and validate date
            date = data.xpath(".//text()")[0].get()
            try:
                date = str(parse(date).date())
            except ValueError:
                self.log("Invalid date format, skipping iteration")
                continue

            # make sure date is present in database
            matches = self.db.query("SELECT * FROM results WHERE code=%s AND taken=%s",
                                    (code, date,))

            # no entry matched
            if len(matches) <= 0:
                self.log("Date not found in database")
                continue

            # make sure exam doesn't already exist
            if matches[0].get("exam", None) is not None:
                self.log("Exam already present in database")
                continue

            # let scrapy schedule download of actual pdf
            yield Request(url="http://chalmerstenta.se" + data[2].xpath("a/@href").get(),
                          callback=self.save_data,
                          meta={"date": date,
                                "code": code,
                                "type": "exam"})

            # check if solution is in row
            solution_url = data[3].xpath("a/@href").get()
            if solution_url is None:
                self.log("Solution not present, skipping.")
                continue

            # check if solution is not already present
            if matches[0].get("solution", None) is not None:
                self.log("Solution already present in database")
                continue

            # schedule download of solution pdf
            yield Request(url="http://chalmerstenta.se" + solution_url,
                          callback=self.save_data,
                          meta={"date": date,
                                "code": code,
                                "type": "solution"})

    def save_data(self, response):
        """ Download PDF and submit exam suggestion using meta entries: date and code"""

        self.log("Posting exam suggestion to database")
        date = response.meta["date"]
        code = response.meta["code"]

        # insert suggestion
        if response.meta["type"] == "exam":
            self.db.query(
                "INSERT INTO exam_suggestions (taken, code, exam) VALUES (%s, %s, %s)",
                (date, code, response.body))
        elif response.meta["type"] == "solution":
            self.db.query(
                "INSERT INTO exam_suggestions (taken, code, solution) VALUES (%s, %s, %s)",
                (date, code, response.body))
