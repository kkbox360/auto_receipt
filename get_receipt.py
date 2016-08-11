from bs4 import BeautifulSoup
import urllib.request
import ssl
import datetime
import smtplib
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from email.header import Header

class get_receipt():
    def __init__(self):
        #bypass verificate
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen('https://www.etax.nat.gov.tw/etw-main/front/ETW183W1/') as response:
            doc = response.read()

        soup = BeautifulSoup(doc, 'lxml')
        self.site_list = {}
        self.date_list = []
        self.prize_list = {}
        
        #get every site addr to receipt number
        for site in soup.tbody.find_all('a'):
            if 'ETW183W2' in site['href']:
                time = int(site['href'].split('_')[1])
                self.site_list[time] = site['href']
                self.date_list.append(time)

    #get number with date input
    def get_num(self, date):
        self.prize_list[date] = {}

        with urllib.request.urlopen("https://www.etax.nat.gov.tw" + self.site_list[date]) as response:
            doc = response.read()
        soup = BeautifulSoup(doc, 'lxml')

        content_table = soup.find('div', 'content').table
        table_td = content_table.find_all('td')

        self.prize_list[date]['special'] = (table_td[1].span.string, table_td[2].string)
        self.prize_list[date]['grand'] = (table_td[3].span.string, table_td[4].string)
        self.prize_list[date]['regular'] = ((table_td[5].span.string.split("、")), table_td[11].string[:-1])
        self.prize_list[date]['additional_sixth'] = (table_td[12].string, table_td[13].string)

        return self.prize_list

    def send_mail(self, recepient):
        #get account & password to login
        try:
            f = open('google_account.txt', 'r')
            me = f.readline()[:-1]
            pw = f.readline()
        except IOError:
            f = open('google_account.txt', 'w')
            me = input('Google Account:')
            pw = getpass.getpass('Password:')
            f.write(me + '\n')
            f.write(pw)
        finally:
            f.close()
        
        #get last two receipt nums
        self.get_num(self.date_list[0])
        self.get_num(self.date_list[1])
        date1 = self.prize_list[self.date_list[0]]
        date2 = self.prize_list[self.date_list[1]]

        html = """<html>
          <head></head>
          <body>
            <h1 style='color: red;'>日期:%s</h1>
            <p>特別獎:%s</p>
            <p>%s</p>
            <p>特獎:%s</p>
            <p>%s</p>
            <p>頭獎:%s</p>
            <p>%s</p>
            <p>增開六獎:%s</p>
            <p>%s</p>
            <br>
            <h1>日期:%s</h1>
            <p>特別獎:%s</p>
            <p>%s</p>
            <p>特獎:%s</p>
            <p>%s</p>
            <p>頭獎:%s</p>
            <p>%s</p>
            <p>增開六獎:%s</p>
            <p>%s</p>
          </body>
        </html>
        """ % (self.date_list[0], date1['special'][0], date1['special'][1], date1['grand'][0], date1['grand'][1], date1['regular'][0], date1['regular'][1], date1['additional_sixth'][0], date1['additional_sixth'][1], self.date_list[1], date2['special'][0], date2['special'][1], date2['grand'][0], date2['grand'][1], date2['regular'][0], date2['regular'][1], date2['additional_sixth'][0], date2['additional_sixth'][1])

        #send email with smtp gmail
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Receipt Number'
        msg['From'] = me
        msg['To'] = recepient
        msg.attach(MIMEText(html, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(me, pw)
        server.sendmail(me, recepient, msg.as_string())
        server.quit()
