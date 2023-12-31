"""Simple Class for controlling Sleep mode on Dutch & Dutch 8C loudspeakers."""
#
# usage: dutch.py DNSnameofaspeaker sleep|wake
#
# The message format was found by dumping websocket traffic from the
# D&D web client, and picking out the appropriate exchanges. So
# there's a chance of it being broken by future firmware updates.
#
# The protocol between the management agent (App or web) and the
# speakers seems quite comprehensive and allows for reading state,
# updating state, and registering for notification of changes. This
# allows multiple management agents to be in use, and for all to stay
# up to date with the current status.
#
# This code just assumes a simple setup of a pair of speakers in one
# room, and will act on those (or it might work on the first room if
# you have more than one). It just makes simple command/response
# websocket requests, nothing asynchronous is expected.
#
# The D&D web app initially reads "ClerkIP.js" from whatever server
# was specified in the initial HTTP URL and then connects to the mDNS
# name listed in that response.
#
# This script will just go straight into trying to talk via websocket
# on the appropriate port of the speaker specified in the first CLI
# argument. There isn't really any error checking, so it will probably
# just backtrace if anything unexpected happens.
#
# To make the script work reliably using the Home Assistant
# command_line integration, if you supply the script with an 
# IP address instead of a hostname, it will assume that is the
# master speaker, and talk to it directly.  You can find the master
# speaker by giving it the hostname, and it will print out the master's 
# IP address
#
#

import time
import json
import re
import sys
import socket
import websocket

class DutchRoom :
    """Main class that represents a Room object in the D&D management App"""

    # Talk to either speaker and find out who the master is. Not sure
    # if this really matters, but we might as well, because the App
    # does it. If an IP address is provided as the speaker name we will just
    # assume that one is the master
    def getmasterurl(self, rawip):
        """Get the master speaker websocket URL"""
        if rawip :
            self.masterurl = 'ws://'+self.name+':8768'
        else :
            ws = websocket.WebSocket()
            ws.connect('ws://'+self.name+':8768')
            ws.send(
                json.dumps(
                    {"meta":{"id":"999912345678","method":"read","endpoint":\
                             "master"},"data":{}}
                )
            )
            response = ws.recv()
            data = json.loads(response)
            ws.close()
            masterhost = data['data']['address']['hostname']
            # Especially on Home Assistant, the mDNS resolution sometimes fails
            # initially. So retry it a few times before giving up
            tries = 5
            for i in range(tries) :
                try:
                    masteraddr = socket.gethostbyname(masterhost)   # IPv4 address only
                except:
                    if i == (tries - 1) :
                        print("gethostbyname ", masterhost," failed")
                        raise 
                    else:
                        time.sleep(1)
                        continue
                    break
            masterport = str(data['data']['address']['port_ascend'])
            self.masterurl = "ws://" + masteraddr + ":" + masterport
            print ("Master speaker IP: ", masteraddr)

    # Find out a room ID from the master speaker, by asking for a list
    # of targets. Even though the query specifies "room", it seems to
    # get speakers as well.
    def getroomid(self):
        """Get the Room ID from the master speaker"""
        self.ws = websocket.WebSocket()
        self.ws.connect(self.masterurl)
        self.ws.send(
            json.dumps(
                {"meta":{"id":"999912345678","method":"read","endpoint":\
                         "targets","targetType":"room","target":"*"},"data":{}}
            )
        )
        response = self.ws.recv()
        data = json.loads(response)
        # we expect an array of responses, one of which is a room, the
        # other two are the speakers. The room has always been the
        # first one in dumped traffic, but don't assume this.
        respcnt = (len(data['data']))
        self.roomtarget = ""
        for i in range(respcnt):
            if data['data'][i]['targetType'] == "room" :   # found a room, so copy its ID
                self.roomtarget = data['data'][i]['target']
        # get the "network" data which seems to include almost all parameters and settings
        self.ws.send(
            json.dumps(
                {"meta":{"id":"999912345678","method":"read","endpoint":\
                         "network","targetType":"room","target":"*"},"data":{}}
            )
        )
        response = self.ws.recv()
        self.dump = json.loads(response)
        # leave the websocket open for the next call.

    # Actually send the sleep or wake command.
    def dosleep(self, sleepmode):
        """Put speakers to sleep or wake them up"""
        if sleepmode == "sleep" :
            command = '{"meta":{"id":"999912345678","method":"update","endpoint":"sleep",\
            "targetType":"room","target":"' + self.roomtarget + '"},"data":{"enable":true}}'
        elif sleepmode == "wake" :
            command = '{"meta":{"id":"999912345678","method":"update","endpoint":"sleep",\
            "targetType":"room","target":"' + self.roomtarget + '"},"data":{"enable":false}}'
        self.ws.send(
            command
        )
        self.ws.recv()
        self.ws.close()

    # Dump data
    def dodump(self):
        """Dump data from speakers"""
        print(json.dumps(self.dump, indent=2))
        self.ws.close()


    #
    # Class init. Get the Room ID we want to talk to.
    #
    def __init__(self,name, rawip):
        """Init"""
        self.name = name
        self.getmasterurl(rawip)
        self.getroomid()


#
# a command line argument of "sleep" will put the speakers into standby, "wake" will wake them up.
#
def main():
    """Main function if used standalone"""
    args = sys.argv[1:]
    if (len(args) < 2) or (args[1] != "wake" and args[1] != "sleep" and args[1] != "dump")  :
        print ("Usage: " + sys.argv[0] + " name wake|sleep|dump")
        return 1

    # check for first argument being an IP address, if so we assume it's the master
    pat = re.compile ("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    rawip = bool(re.match(pat, args[0]))

    room = DutchRoom(args[0], rawip)

    if args[1] == "dump" :
        room.dodump()
    else :
        room.dosleep(args[1])
    return 0

if __name__ == '__main__':
    sys.exit(main())
