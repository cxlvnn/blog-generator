from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = "localhost"
PORT = 8080

with open("storage/blogs.json", "r") as file:
    blogs = json.load(file)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):

        path = self.path

        match path:
            case "/":
                self.send_response(301)
                self.send_header("Location", "/blogs")
                self.end_headers()
            case "/blogs":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                with open("resources/views/index.html", "r") as file:
                    resp = file.read()
                    with open("resources/views/blog/index.html") as file:
                        blog_index = file.read()
                        resp = resp.replace("^app^", blog_index)
                        blogs_template = "<ul>"
                        for blog in blogs:
                            blogs_template += f"""
                                                <li>
                                                <a href="/blog/{blog["id"]}">{blog["title"]}
                                                </a>
                                                <p>{blog["date"]}</p>
                                                </li>
                                                """
                        blogs_template += "</ul>"
                        resp = resp.replace("^blogs^", blogs_template)
                    with open("resources/css/main.css") as file:
                        style = file.read()
                        resp = resp.replace("^mystyle^", style)
                self.wfile.write(bytes(resp, "utf-8"))
            case _:
                path_list = path.split("/")
                if len(path_list) == 3:
                    id = path_list[2]
                    self.wfile.write(bytes(id, "utf-8"))


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
