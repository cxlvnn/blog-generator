from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)

        self.send_header("Content-type", "text/html")
        self.end_headers()

        response_txt: str
        with open("resources/views/index.html", "r") as file:
            response_txt = file.read()
        _ = self.wfile.write(bytes(response_txt, "utf-8"))


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
