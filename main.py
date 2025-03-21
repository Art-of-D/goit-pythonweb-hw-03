from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
from pathlib import Path
from urllib.parse import urlparse
import mimetypes
import logging
from socket_server import start_socket_server, transfer_data

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000
BASE_DIR = Path(__file__).parent

class QueryHandler(BaseHTTPRequestHandler):
  def do_GET(self):
      router = urlparse(self.path).path
      match router:
          case "/":
              self.send_html("index.html")
          case "/message":
              self.send_html("message.html")
          case _:
              file = BASE_DIR.joinpath(router[1:])
              if file.exists():
                  self.send_static(file)
              else:
                  self.send_html("error.html", 404)

  def do_POST(self):
      size = int(self.headers["Content-Length"])
      data = self.rfile.read(size)
      transfer_data(data)
      self.send_response(302)
      self.send_header("Location", "/")
      self.end_headers()

  def send_html(self, filename, status=200):
      self.send_response(status)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      with open(filename, "rb") as f:
          self.wfile.write(f.read())

  def send_static(self, filename, status=200):
      self.send_response(status)
      mimetype = mimetypes.guess_type(filename)[0] or "text/plain"
      self.send_header("Content-type", mimetype)
      self.end_headers()
      with open(filename, "rb") as f:
          self.wfile.write(f.read())

#Function that is starting http server and configuring it
def run_http_server():
  httpd = HTTPServer((HTTP_HOST, HTTP_PORT), QueryHandler)
  try:
      print(f"HTTP server started: http://{HTTP_HOST}:{HTTP_PORT}")
      httpd.serve_forever()
  except Exception as e:
      logging.error(e)
  finally:
      logging.info("Server stopped")
      httpd.server_close()

#Function to start socket server and http server
if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(threadName)s - %(message)s")
  Process(target=run_http_server).start()
  Process(target=start_socket_server).start()