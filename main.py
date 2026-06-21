from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from dataclasses import dataclass


@dataclass
class Blog:
    title = str
    content = str
    date = str


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
                    app = file.read()
                    with open("resources/views/blog/index.html") as file:
                        blog_index = file.read()
                        app = app.replace("^app^", blog_index)
                        blogs_template = "<ul>"
                        for blog in blogs:
                            blogs_template += f"""
                                                <li>
                                                <a href="/blogs/{blog["id"]}">{blog["title"]}
                                                </a>
                                                <p>{blog["date"]}</p>
                                                </li>
                                                """
                        blogs_template += "</ul>"
                        app = app.replace("^blogs^", blogs_template)
                    with open("resources/css/main.css") as file:
                        style = file.read()
                        app = app.replace("^mystyle^", style)
                self.wfile.write(bytes(app, "utf-8"))
            case _:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                path_list = path.split("/")
                if len(path_list) == 3:
                    id = int
                    if int(path_list[2]):
                        id = int(path_list[2])
                    title = ""
                    content = ""
                    date = ""
                    for blog in blogs:
                        if id == blog["id"]:
                            title = blog["title"]
                            content = blog["content"]
                            date = blog["date"]
                    with open("resources/views/index.html") as file:
                        app = file.read()
                        with open("resources/css/main.css") as css:
                            style = css.read()
                            app = app.replace("^mystyle^", style)
                    with open("resources/views/blog/show.html") as file:
                        blog_show = file.read()
                        blog_show = blog_show.replace("^title^", title)
                        blog_show = blog_show.replace("^content^", content)
                        blog_show = blog_show.replace("^date^", date)
                        app = app.replace("^app^", blog_show)
                        self.wfile.write(bytes(app, "utf-8"))


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
