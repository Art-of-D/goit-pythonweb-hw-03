from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib
import mimetypes
import logging
import json
import time
from templates_gen.messages_template import generate_html

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000
BASE_DIR = Path(__file__).parent


class QueryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        router = urllib.parse.urlparse(self.path).path
        match router:
            case "/":
                self.send_html("./pages/index.html")
            case "/message":
                self.send_html("./pages/message.html")
            case "/read":
                generate_html(BASE_DIR)
                self.send_html("./pages/messages_history.html")
            case _:
                file = BASE_DIR.joinpath(router[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("./pages/error.html", 404)

    def do_POST(self):
        router = urllib.parse.urlparse(self.path).path
        if router == "/message":

            data = self.rfile.read(int(self.headers['Content-Length']))
            logging.info(data)
            data_parse = urllib.parse.unquote_plus(data.decode())
            logging.info(data_parse)
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            logging.info(data_dict)
            self.save_to_json(data_dict)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            logging.warning(f"Unhandled POST request to {router}")
            self.send_response(404)
            self.end_headers()

    def save_to_json(self, data):
        storage_path = BASE_DIR.joinpath("storage/data.json")

        try:
            try:
                with open(storage_path, "r") as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                raise Exception("Failed to load existing data")
            current_time = time.localtime()
            t = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            existing_data[t] = data
            with open(storage_path, "w") as f:
                json.dump(existing_data, f, indent=4)

            logging.info(f"Data successfully saved to {storage_path}")

        except Exception as e:
            logging.error(f"Failed to save data: {e}")

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


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(threadName)s - %(message)s"
    )
    run_http_server()
