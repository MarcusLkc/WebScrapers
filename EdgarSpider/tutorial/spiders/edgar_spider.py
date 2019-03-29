import scrapy


class QuotesSpider(scrapy.Spider):
    name = "edgar"

    def start_requests(self):
        urls = [
            'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=blk&type=13F-HR&dateb=20181023&owner=include&count=500'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        class_file_table = response.xpath(
            '//table[@class="tableFile2"]//a[contains(@href,"Archive")]/@href').extract()
        for report_link in class_file_table[:1]:
            yield response.follow(report_link, callback=self.class_file_parser)

    def class_file_parser(self, response):
        yield response.follow(response.xpath('//table[@class="tableFile"]//a')[-1], callback=self.parse_holdings)

    def parse_holdings(self, response):
        for info_table in response.xpath('//informationtable/infotable'):
            yield {
                'nameofissuer': info_table.xpath('nameofissuer/text()').extract_first(),
                'titleofclass': info_table.xpath('titleofclass/text()').extract_first(),
                'cusip': info_table.xpath('cusip/text()').extract_first(),
                'value': info_table.xpath('value/text()').extract_first(),
                'sshprnamt': info_table.xpath('shrsorprnamt/sshprnamt/text()').extract_first(),
                'sshorprntype': info_table.xpath('shrsorprnamt/sshprnamttype/text()').extract_first(),
                'InvestmentDiscretion': info_table.xpath('investmentdiscretion/text()').extract_first(),
                'va-Sole': info_table.xpath('votingauthority/sole/text()').extract_first(),
                'va-Shared': info_table.xpath('votingauthority/shared/text()').extract_first(),
                'va-None': info_table.xpath('votingauthority/none/text()').extract_first(),
            }
