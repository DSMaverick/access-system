from urllib.parse import urlencode
from urllib.request import Request, urlopen

url = 'http://192.168.100.123:5000/raspi' #Destination URL

def send_image_to_server(base64, extension):
  #Dict with data that will be trasnmited in post
  post_fields = {'image': base64, 'extension': extension} 
  
  #Convert dict to URL format and code it in bite
  request = Request(url, urlencode(post_fields).encode())
  json = urlopen(request).read().decode()
  
  return json

  
