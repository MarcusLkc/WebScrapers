"""This module holds a spider webcrawler for the edgar holdings websites
The Module outputs to different csv files and additionally it 
runs asyncronously thanks to Scrapy

Raises:
    Exception: [description]
"""


import scrapy
import csv


class EdgarSpider(scrapy.Spider):
    """This is our spider class for navigating through the Edgar website
    which inherits from the Scrapy class
    num and cik variables needs to be passed to this spider when running
    by using the argument flags ex.  -a num=2 -a cik=blk
    full ex:
        scrapy crawl edgar2 -a num=2 -a cik=blk
    Attributes:
        num (int): The number of reports that you would like to be printed out
        cik (str): The cik number of the company you would like to have
    Args:
        scrapy (scrapy): Scrapy class object for utility functions and crawling mechanisms 

    Raises:
        Exception: raises exception if you do not set a cik
    """

    name = "edgar2"

    def start_requests(self):
        """This is our starting function which overrides scrapy's base start_requests function

        Attributes:
            self

        Raises:
            Exception: [description]
        """

        self.num = getattr(self, 'num', 1)
        self.cik = getattr(self, 'cik', None)
        if not self.cik:
            raise Exception("You must set a cik")

        urls = [
            'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=13F&dateb=&owner=exclude&count=100'.format(
                self.cik)
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parses the first html page of the company we selected and scans the table for 13f file url s
        then follows them to the next page

        Args:
            response (:obj): a scrapy request object provided from our start_url
        """

        num = int(self.num)
        class_file_table = response.xpath(
            '//table[@class="tableFile2"]//a[contains(@href,"Archive")]/@href').extract()

        for report_link in class_file_table[:num]:
            yield response.follow(report_link, callback=self.class_file_parser)

    def class_file_parser(self, response):
        """Parses the 2nd webpage of our navigation where we can grab the link of our 
        text or xml files. which is in the last row of the tableFile table

        Args:
            response (:obj): a scrapy request object provided by parse
        """

        yield response.follow(response.xpath('//table[@class="tableFile"]//a')[-1], callback=self.parse_holdings)

    def parse_holdings(self, response):
        """Parses the .txt holdings file of the specified holdings report
        Then saves all of our necessary data and headers to a .csv file based on company name filetype etc.

        Args:
            response ([type]): [description]
        """

        file_type = "13-F"
        report_period = response.xpath(
            '//periodofreport/text()').extract_first()
        comp_name = response.xpath(
            '//name/text()').extract_first().replace(' ', '')
        file_name = comp_name + file_type + report_period
        with open(file_name, 'w', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(['nameofIssuer', 'titleofclass', 'cusip', 'value', 'sshrpnamt', 'sshrorprnamt',
                         'sshrorprntype', 'InvestmentDiscretion', 'va-Sole', 'va-Shared', 'va-None'])

            for info_table in response.xpath('//informationtable/infotable'):
                wr.writerow([
                    info_table.xpath('nameofissuer/text()').extract_first(),
                    info_table.xpath('titleofclass/text()').extract_first(),
                    info_table.xpath('cusip/text()').extract_first(),
                    info_table.xpath('value/text()').extract_first(),
                    info_table.xpath(
                        'shrsorprnamt/sshprnamt/text()').extract_first(),
                    info_table.xpath(
                        'shrsorprnamt/sshprnamttype/text()').extract_first(),
                    info_table.xpath(
                        'investmentdiscretion/text()').extract_first(),
                    info_table.xpath(
                        'votingauthority/sole/text()').extract_first(),
                    info_table.xpath(
                        'votingauthority/shared/text()').extract_first(),
                    info_table.xpath(
                        'votingauthority/none/text()').extract_first()
                ])
