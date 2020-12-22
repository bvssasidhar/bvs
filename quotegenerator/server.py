import os
import json
import random
import http.server
import socketserver

FONT_SIZE = os.environ.get('FONT_SIZE', '20')
RAW_INDEX_CONTENTS = bytes(open('./index.html').read(), 'UTF-8')
QUOTES = [
   'Live, laugh, love.',
   'Keep calm and carry on.',
   'Do what you feel in your heart to be right – for you’ll be criticized anyway.',
   'You may not control all the events that happen to you, but you can decide not to be reduced by them',
   'Truth is, everybody is going to hurt you; you just gotta find the ones worth suffering for'
   'If life gives you lemons, make lemonade',
   'You miss 100 percent of the shots you dont take',
   'Be the change you wish to see in the world',
   'Be kind, for everyone you meet is fighting a hard battle.',
   'Learning to unlearn is the highest form of learning.'
]

def get_quote():
   return {'size': FONT_SIZE, 'text': random.choice(QUOTES)}

class Server(http.server.SimpleHTTPRequestHandler):
   def do_GET(self):
       path = self.path
       if path == '/' or path == '/index.html':
           self.send_response(200, 'OK')
           self.send_header('Content-type', 'text/html')
           self.end_headers()
           self.wfile.write(RAW_INDEX_CONTENTS)
       elif path == '/quote':
           quote = get_quote()
           self.send_response(200, 'OK')
           self.send_header('Content-type', 'application/json')
           self.end_headers()
           self.wfile.write(bytes(json.dumps(quote), 'UTF-8'))
       else:
           self.send_response(404, 'NOT FOUND')

if __name__ == '__main__':
   print('Starting server...')
   socketserver.TCPServer(('0.0.0.0', 8080), Server).serve_forever()

