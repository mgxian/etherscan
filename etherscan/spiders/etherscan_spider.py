import scrapy
import requests
import json
import re
from pprint import pprint
from etherscan.items import EtherscanItem, ContractItem


class EtherscanSpider(scrapy.Spider):
    name = "etherscan"
    allowed_domains = ["etherscan.io"]
    start_urls = [
        "https://etherscan.io/contractsVerified",
    ]

    def parse(self, response):
        # print('start --->')
        page = response.xpath('/html/body/div[1]/div[5]/div[2]/div[2]/p/span')
        max_page_number = int(page.xpath('//*/b[2]/text()').extract()[0])
        # print('max_page_number --> ', max_page_number)
        # max_page_number = 1
        for i in range(max_page_number):
            url = response.url + '/' + str(i+1)
            # print(url)
            yield scrapy.Request(url, callback=self.parse_verified_contracts)

    def parse_verified_contracts(self, response):
        for contract in response.xpath('/html/body/div[1]/div[5]/div[3]/div/div/div/table/tbody/tr/td[1]/a')[:]:
            link = contract.xpath('@href').extract()[0]
            url = response.urljoin(link)
            # print(url)
            # url = 'https://etherscan.io/address/0x293993aC7b6F8502B383ED7a1B784F5A49695E18#code'
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

        creator_address_element = summary_dom.xpath(
            '//*[@id="ContentPlaceHolder1_trContract"]/td[2]/a/text()')
        if len(creator_address_element) > 0:
            creator_address = creator_address_element[0].extract().strip('\n ')
        else:
            creator_address = ''

        creator_transaction_hash_element = summary_dom.xpath(
            '//*[@id="ContentPlaceHolder1_trContract"]/td[2]/span/a/text()')
        if len(creator_transaction_hash_element) > 0:
            creator_transaction_hash = creator_transaction_hash_element[0].extract().strip(
                '\n ')
        else:
            creator_transaction_hash = ''

        code = response.xpath('//*[@id="editor"]/text()')[0].extract()
        compiler_version = contract_code_dom.xpath(
            'div[2]/table/tr[2]/td[2]/text()')[0].extract().strip('\n ')
        optimization_enabled = 'yes' in contract_code_dom.xpath(
            'div[3]/table/tr/td[2]/text()')[0].extract().strip('\n ').lower()
        runs = contract_code_dom.xpath(
            'div[3]/table/tr[2]/td[2]/text()')[0].extract().strip('\n ')

        warnings = []
        warning_elements = response.xpath(
            '//*[@id="ContentPlaceHolder1_contractCodeDiv"]/div[1]/i/a')[1:]
        for we in warning_elements:
            warning = {}
            text = we.xpath('text()')[0].extract()
            link = we.xpath('@href')[0].extract()
            link = response.urljoin(link)
            # print(text)
            warning['name'] = text.split(' ')[0]
            warning['severity'] = text.split(' ')[1].strip('()')
            warning['url'] = link
            warnings.append(warning)

        used_lib_elements = response.xpath(
            '//*[@id="dividcode"]/i[contains(@class, "fa-book")]/following-sibling::pre[1]')
        if len(used_lib_elements) > 0:
            used_lib_names = [name.strip(
                ' :') for name in used_lib_elements.xpath('text()').extract()]
            used_lib_links = []
            root_url = 'https://etherscan.io'
            for used_lib_element in used_lib_elements:
                used_lib_link = used_lib_element.xpath('a/@href')[0].extract()
                used_lib_links.append(root_url + used_lib_link)
            
            used_libs = []
            for name, url in zip(used_lib_names, used_lib_links):
                used_lib = {}
                used_lib['name'] = name
                used_lib['url'] = url
                used_libs.append(used_lib)

            print('woops -------------> ', used_libs)

        return

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

        item['warnings'] = warnings

        # print(json.dumps(item))
        # print(warning)

        # yield item

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
