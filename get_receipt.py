from bs4 import BeautifulSoup
import urllib.request
import ssl

class get_receipt():
    def __init__(self):
        #bypass verificate
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen("https://www.etax.nat.gov.tw/etw-main/front/ETW183W1/") as response:
            doc = response.read()

        soup = BeautifulSoup(doc, "lxml")
        self.site_list = {}
        
        #get every site addr to receipt number
        for site in soup.tbody.find_all("a"):
            if "ETW183W2" in site["href"]:
                time = site["href"].split("_")[1]
                self.site_list[time] = site["href"]

    #get number with date input
    def get_num(self, date):
        self.date = date
        self.prize_list = {}

        with urllib.request.urlopen("https://www.etax.nat.gov.tw" + self.site_list[self.date]) as response:
            doc = response.read()
        soup = BeautifulSoup(doc, 'lxml')

        content_table = soup.find('div', 'content').table
        table_td = content_table.find_all('td')

        self.prize_list['special'] = (table_td[1].span.string, table_td[2].string)
        self.prize_list['grand'] = (table_td[3].span.string, table_td[4].string)
        self.prize_list['regular'] = ((table_td[5].span.string.split("、")), table_td[11].string[:-1])
        self.prize_list['additional_sixth'] = (table_td[12].string, table_td[13].string)

        return self.prize_list

