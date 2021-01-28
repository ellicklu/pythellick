import os
import re
import urllib
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class TestHTTPHandler(BaseHTTPRequestHandler):
	#Process GET request
    def do_GET(self):
		#output template strings
        templateStr = '''  
<html>  
<head>  
<title>QR Link Generator</title>  
</head>  
<body>  
%s
<br>  
<br>  
<form action="/qr" name=f method="GET"><input maxLength=1024 size=70  
name=s value="" title="Text to QR Encode"><input type=submit  
value="Show QR" name=qr>  
</form>
</body>  
</html> '''
 
 
	#pattern of qr code for RegEX
	pattern = re.compile(r'/qr\?s=([^\&]+)\&qr=Show\+QR')
	#Trying matching the path pattern, if not maching , do nothing
	match = pattern.match(self.path)
	qrImg = ''
		
	if match:
		#Use match group to get group information
		qrImg = '<img src="http://chart.apis.google.com/chart?chs=300x300&cht=qr&choe=UTF-8&chl=' + match.group(1) + '" /><br />' + urllib.unquote(match.group(1)) 
 
	self.protocal_version = 'HTTP/1.1'	#Set protocol version
	self.send_response(200)	#response code
	self.send_header("Welcome", "Contect")	#response content
	self.end_headers()
	self.wfile.write(templateStr % qrImg)	#response content outuput
	
#Start server function
def start_server(port):
    http_server = HTTPServer(('', int(port)), TestHTTPHandler)
    http_server.serve_forever()	#set the listener
 
os.chdir('static')	#change working directory to 'static'

start_server(8000)