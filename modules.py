import socket
from datetime import datetime, timezone
import nmap
import whois
import pyasn
from spam_lists import SPAMHAUS_DBL, SPAMHAUS_ZEN, SURBL_MULTI
import os
import subprocess


class BlackListCheck:
    def __init__(self, url=None, urlList=None):
        self.url = url
        self.urlList = urlList
        self.blackLists = [SPAMHAUS_DBL, SPAMHAUS_ZEN, SURBL_MULTI]

    def singleLookup(self, url):
        if not url:
            url = self.url
        print('Checking blacklists for {}'.format(url))
        blacklisted = False
        for blackList in self.blackLists:
            try:
                if url in blackList:
                    print('Found {} in blacklist {}'.format(url, blackList))
                    blacklisted = True
            except:
                print('Error Checking blacklists')
        return blacklisted
    
    def listLookup(self, urlList):
        if not urlList:
            urlList = self.urlList
        blackListed = False
        for blackList in self.blackLists:
            for url in urlList:
                if url in blackList:
                    blackListed = True
        return blackListed


class UtcToLocal:
    def __init__(self, time=None):
        self.time = time

    def convertTime(self, time):
        print()
        print('Converting {} from UTC to Local Time...'.format(time))
        time = time + ' UTC+0000'
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        timeObj = datetime.strptime(time, fmt)
        return timeObj.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def convPrompt(self):
        print('What time did the event occur in UTC? (e.g. 2018-10-16 21:22:23)')
        time = input('> ')   
        if time:
            try:
                convertedTime = self.convertTime(time)
                return convertedTime
            except:
                print('I didn\'t understand that time')
                return
        else:
            return

class AsnLookup:
    
    def lookup(self, ip):

        if not os.path.isdir('asn_db'):
            print()
            print('No database folder found!')
            print()
        elif not os.path.isfile('asn_db/ipasn_db_main.dat'):
            print()
            print('No database file found!')
            print()
        else:
            asndb = pyasn.pyasn('asn_db/ipasn_db_main.dat')
            asnNum = asndb.lookup(ip)
            # print()
            # print('{} ASN number: {}'.format(ip, asnNum[0]))
            # print()
            return asnNum[0]

    def getDetails(self, asnNum):
        ASN = str(asnNum)
        querycmd2 = 'AS' + ASN + '.asn.cymru.com'
        response2 = subprocess.Popen(['dig', '-t', 'TXT', querycmd2, '+short'], stdout=subprocess.PIPE).communicate()[0]
        #response2List = response2.split('|')
        asnInfoL = response2.decode().strip('\n "').split(' | ')
        asnInfo = {"ISP" : asnInfoL[4], "Country" : asnInfoL[1], "Registry" : asnInfoL[2], "Date Registered" : asnInfoL[3]}
        return asnInfo


class Lookup:
    def doLookup(self, host):
        if not host.ip:
            print('Looking up ip from domain {}'.format(host.domainName))
            try:
                ip = socket.gethostbyname(host.domainName)
                if ip:
                    host.ip = ip
                    return host
                else:
                    print('Couldn\'t get IP')
            except:
                print('Couldn\'t look up that host')

        elif not host.domainName:
            print('Looking up domain name from ip {}'.format(host.ip))
            domainName = socket.gethostbyaddr(host.ip)
            if domainName:
                host.domainName = domainName[0]
                return host
            else:
                print('Couldn\'t get hostname')
        
        else:
            print('You already have the domain and IP!')
    
class PortScan:
    def __init__(self, ip, sType):
        self.ip = ip
        self.sType = sType
        self.ports = []
        self.state = ""

    def runScan(self, ip, sType):
        print('Running {} scan on {}...'. format(sType, ip))

        scanTypes = ['F', 'sS']
        
        if not sType:
            sType = 'F'
        
        if sType in scanTypes:
            sType = '-' + sType
            self.nm = nmap.PortScanner()
            if sType == '-F':
                self.nm.scan(hosts=ip, arguments=sType)
            else:
                self.nm.scan(hosts=ip, arguments=sType, ports='21-445,3389,8080,8081')
            print('Done! Here\'s what I got:')
            self.parseResults()
            print('Open ports: {}'.format(self.ports))
            returnL = [self.ports, self.state]
            return returnL
            
        else:
            print('I don\'t run that kind of scan')

    def parseResults(self):
        for host in self.nm.all_hosts():
            print('%s is %s' % (self.nm[host].hostname(), self.nm[host].state()))
            self.state = self.nm[host].state()

            for proto in self.nm[host].all_protocols():
                lport = self.nm[host][proto].keys()
                for port in lport:
                    self.ports.append(port)

class Whois:
    def __init__(self, hostName="", ip=""):
        self.hostName = hostName
        self.ip = ip
        self.results = ""

    def getInfo(self):
        print()
        print('Getting whois info!')
        print()

        if not self.hostName:
            try:
                self.results = whois.whois(self.ip)
            except:
                print('Could not get results')
        else:
            try:
                self.results = whois.whois(self.hostName)
                self.whoisReturn = self.parseResults()
                return self.whoisReturn
            except:
                print('Could not get info')
        
    
    def parseResults(self):
        whoisResults = {}

        whoisResults['domain_name'] = self.results['domain_name']
        whoisResults['name'] = self.results['name']
        whoisResults['organization'] = self.results['org']
        whoisResults['address'] = self.results['address']
        whoisResults['state'] = self.results['state']
        whoisResults['city'] = self.results['city']

        return whoisResults
        