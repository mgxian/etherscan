import scrapy
import requests
import json
from pprint import pprint
from etherscan.items import EtherscanItem, ContractItem


class EtherscanSpider(scrapy.Spider):
    name = "etherscan"
    allowed_domains = ["etherscan.io"]
    start_urls = [
        "https://etherscan.io/contractsVerified",
    ]

    def parse(self, response):
        page = response.xpath('/html/body/div[1]/div[5]/div[2]/div[2]/p/span')
        max_page_number = int(page.xpath('//*/b[2]/text()').extract()[0])
        # print(max_page_number)
        # max_page_number = 1
        for i in range(max_page_number):
            url = response.url + '/' + str(i+1)
            # print(url)
            yield scrapy.Request(url, callback=self.parse_verified_contracts)

    def parse_verified_contracts(self, response):
        for contract in response.xpath('/html/body/div[1]/div[5]/div[3]/div/div/div/table/tbody/tr/td[1]/a'):
            link = contract.xpath('@href').extract()[0]
            url = response.urljoin(link)
            # print(url)
            yield scrapy.Request(url, callback=self.parse_contract)

    def parse_contract(self, response):
        # item = ContractItem()
        item = {}
        try:
            address = response.xpath(
                '//*[@id="mainaddress"]/text()')[0].extract()
        except:
            print('crawl error ----> ', response.url)
            return
        contract_code_dom = response.xpath(
            '//*[@id="ContentPlaceHolder1_contractCodeDiv"]')
        name = contract_code_dom.xpath(
            'div[2]/table/tr/td[2]/text()')[0].extract().strip('\n ')
        summary_dom = response.xpath(
            '//*[@id="ContentPlaceHolder1_divSummary"]/div[1]/table')
        balance = summary_dom.xpath(
            '//tr[1]/td[2]/text()')[0].extract().strip('\n ')
        ether_value = summary_dom.xpath(
            '//tr[2]/td[2]/text()')[0].extract().strip('\n ')
        transaction_count = summary_dom.xpath(
            '//tr[3]/td[2]/span/text()')[0].extract().strip('\n ')
        creator_address = summary_dom.xpath(
            '//*[@id="ContentPlaceHolder1_trContract"]/td[2]/a/text()')[0].extract().strip('\n ')
        creator_transaction_hash = summary_dom.xpath(
            '//*[@id="ContentPlaceHolder1_trContract"]/td[2]/span/a/text()')[0].extract().strip('\n ')
        code = response.xpath('//*[@id="editor"]/text()')[0].extract()
        compiler_version = contract_code_dom.xpath(
            'div[2]/table/tr[2]/td[2]/text()')[0].extract().strip('\n ')
        optimization_enabled = 'yes' in contract_code_dom.xpath(
            'div[3]/table/tr/td[2]/text()')[0].extract().strip('\n ').lower()
        runs = contract_code_dom.xpath(
            'div[3]/table/tr[2]/td[2]/text()')[0].extract().strip('\n ')

        item['address'] = address
        item['name'] = name
        item['balance'] = balance
        item['ether_value'] = ether_value
        item['transaction_count'] = transaction_count
        item['creator_address'] = creator_address
        item['creator_transaction_hash'] = creator_transaction_hash
        item['compiler_version'] = compiler_version
        item['optimization_enabled'] = optimization_enabled
        item['runs'] = runs
        item['code'] = code

        item['chain'] = 'eth'
        item['binary_code'] = ''

        # print(json.dumps(item))

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        url = "https://api.wutui.pro/api/s/contract/upload?__WT__=wutui"
        data = {
            "json": json.dumps(item)
        }
        resp = requests.put(url, data, headers=headers)
        print(resp.text)

        # yield item
