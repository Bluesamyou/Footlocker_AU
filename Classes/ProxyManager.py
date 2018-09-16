#TODO: Fix this up to take multiple proxies, and format copped proxies to user:pass@ip:port
from random import randint
import datetime
from termcolor import colored
import colorama


class ProxyManager:
    def __init__(self):

        colorama.init()

        self.formattedProxies  = []
        self.badProxyArr       = []

        with open('proxies.txt') as proxy_file:
            self.proxies = proxy_file.readlines()

            if len(self.proxies) == 0:
                pass
                # print(colored('[{}] :: No proxies in proxy file'.format(datetime.datetime.now().strftime(('%H:%M:%S'))),"red"))
            else:
                for proxies in range(len(self.proxies)):
                    try:
                        if self.proxies[proxies] != "":
                            if "@" in self.proxies[proxies]:
                                self.proxies.append(self.proxies[proxies])
                            else:
                                formatProxy = "{}:{}@{}:{}".format(self.proxies[proxies].rstrip().split(":")[2],self.proxies[proxies].rstrip().split(":")[3],self.proxies[proxies].rstrip().split(":")[0],self.proxies[proxies].rstrip().split(":")[1] )
                                self.formattedProxies.append(formatProxy)
                    except:
                        if self.proxies[proxies] not in self.badProxyArr:
                            self.badProxyArr.append(self.proxies[proxies])

            badProxies = open("Bad_Proxies.txt", "w+")
            for i in range(len(self.badProxyArr)):
                badProxies.write("{}\r".format(self.badProxyArr[i]))


        self.index = 0

    def format(self, proxy):
        if proxy == None:
            return {
                'http': proxy,
                'https': proxy
            }
        else:

            return {
                'http': 'http://{}'.format(proxy),
                'https': 'https://{}'.format(proxy)
            }


    def get_next_proxy(self,randomProxy=True,index=0):
        if self.index == len(self.formattedProxies):
            return self.format(None)
        if randomProxy:
            rand = randint(0, len(self.formattedProxies) - 1)
            print(colored('[{}] :: Added to session'.format(self.formattedProxies[rand]), "cyan",attrs=['bold']))
            return self.format(self.formattedProxies[rand])
        else:
            print(colored('[{}] :: Added to session'.format(self.formattedProxies[index]), "cyan",attrs=['bold']))
            return self.format(self.formattedProxies[index])




i = 0

while i < 100:
    ProxyManager().get_next_proxy()
    i = i + 1

