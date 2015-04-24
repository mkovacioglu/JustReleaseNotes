import sys, re
import requests
import json

class GitHubIssues:
    __conf = None
    __cache = {}
    
    def __init__(self, conf):
        self.__conf = conf
        self.__iconMappings = { "closed" : "http://hydra-media.cursecdn.com/wiki.bukkit.org/8/8c/Favicon-github.png?version=3ba18692efbc14e64d1bfd7c9639a0f2",
                                "open" : "http://hydra-media.cursecdn.com/wiki.bukkit.org/8/8c/Favicon-github.png?version=3ba18692efbc14e64d1bfd7c9639a0f2"
                                }
        headers = { 'Authorization': "token " + self.__conf["ApiToken"] }
        response = requests.get( self.__conf["Url"] + "?filter=all&state=all", headers = headers, verify=False )
        tickets = json.loads(response.text)
        for ticketData in tickets:
            ticketNumber = str(ticketData["number"])
            self.__cache[ticketNumber] = ticketData

    def __log(self, message):
        print ("GitHub Issues: " + message)
        sys.stdout.flush()
        
    def __readJsonInfo(self, ticket):

        if ticket in self.__cache.keys():
            self.__log("Cached ticket info for " + ticket)
            return self.__cache[ticket]
        else:
            uri = self.__conf["Url"] + "/" + ticket
            self.__log("Retrieving ticket info for {0}: {1}".format(ticket, uri))

            headers = { 'Authorization': "token " + self.__conf["ApiToken"] }
            r = requests.get( uri, headers = headers, verify=False )

            data = json.loads(r.text)
            if "message" in data and data["message"] == "Not Found":
                self.__log("Error retrieving GitHub Issue info: " + data["message"])
            self.__cache[ticket] = data
            return data

    def getTicketInfo(self, ticket):
        data = self.__readJsonInfo(ticket)

        if "title" in data:
            title = data["title"]
            embedded_links = {}
            for ticket in self.extractTicketsFromMessage(title):
                embedded_links["#" + ticket] = "{0}/{1}".format(self.__conf["HtmlUrl"],ticket)
        else:
            title = "Untitled"

        return { "state_icon" : self.__iconMappings[data["state"]],
            "html_url" : data["html_url"],
            "ticket" : ticket,
            "title" : title,
            "embedded_link" : embedded_links }

    def extractTicketsFromMessage(self, message):
        message = message.replace("\n", " ").replace("\r", " ").replace("\t", " ");
        p = re.compile('#([0-9]+)');
        results = p.findall(message)
        if results.count > 0:
            return results
        else:
            return ["NULL"]