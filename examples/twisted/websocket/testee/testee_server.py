###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import autobahn

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory

from autobahn.websocket.protocol import WebSocketProtocol
from autobahn.websocket.compress import *



class TesteeServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      self.sendMessage(payload, isBinary)



class StreamingTesteeServerProtocol(WebSocketServerProtocol):

   def onMessageBegin(self, isBinary):
      WebSocketServerProtocol.onMessageBegin(self, isBinary)
      self.beginMessage(isBinary)

   def onMessageFrameBegin(self, length):
      WebSocketServerProtocol.onMessageFrameBegin(self, length)
      self.beginMessageFrame(length)

   def onMessageFrameData(self, payload):
      self.sendMessageFrameData(payload)

   def onMessageFrameEnd(self):
      pass

   def onMessageEnd(self):
      self.endMessage()



class TesteeServerFactory(WebSocketServerFactory):

   #protocol = TesteeServerProtocol
   protocol = StreamingTesteeServerProtocol

   def __init__(self, url, debug = False, ident = None):
      if ident is not None:
         server = ident
      else:
         server = "AutobahnPython-Twisted/%s" % autobahn.version
      WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debug, server = server)
      self.setProtocolOptions(failByDrop = False) # spec conformance
      self.setProtocolOptions(failByDrop = True) # needed for streaming mode
      #self.setProtocolOptions(utf8validateIncoming = False)

      ## enable permessage-deflate
      ##
      def accept(offers):
         for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
               return PerMessageDeflateOfferAccept(offer)

      self.setProtocolOptions(perMessageCompressionAccept = accept)



if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor

   log.startLogging(sys.stdout)

   factory = TesteeServerFactory("ws://localhost:9001", debug = False)

   reactor.listenTCP(9001, factory)
   reactor.run()
