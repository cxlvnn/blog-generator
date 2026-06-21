from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = "localhost"
PORT = 8080

with open("storage/blog-1.json", "r") as file:
    blog_data = json.load(file)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        path = self.path

        match path:
            case "/":
                with open("resources/views/index.html", "r") as file:
                    resp = file.read()
                self.wfile.write(bytes(resp, "utf-8"))
            case "/blog":
                with open("resources/views/blog/show.html", "r") as file:
                    resp = file.read()
                    resp = resp.replace("^title^", blog_data["title"])
                    resp = resp.replace("^content^", blog_data["content"])
                    resp = resp.replace("^date^", blog_data["createdAt"])
                self.wfile.write(bytes(resp, "utf-8"))
            case _:
                resp = b"Not Found"
                self.wfile.write(resp)


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
