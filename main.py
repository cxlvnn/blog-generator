from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = "localhost"
PORT = 8080


def return_not_found(handler: BaseHTTPRequestHandler):
    handler.send_response(404)
    handler.send_header("Content-type", "text/html")
    handler.end_headers()

    with open("resources/views/index.html", "r") as file:
        app = file.read()
        with open("resources/css/main.css", "r") as file:
            app = app.replace("^mystyle^", file.read())
        app = app.replace(
            "^app^",
            """
                          <div>
                          <h1>404 - Not Found</h1>
                          </div>
                          """,
        )
    handler.wfile.write(bytes(app, "utf-8"))


def default_response(handler: BaseHTTPRequestHandler):
    handler.send_response(200)
    handler.send_header("Content-type", "text/html")
    handler.end_headers()


with open("storage/blogs.json", "r") as file:
    blogs = json.load(file)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):

        path = [s for s in self.path.split("/") if s]

        match path:
            case []:
                self.send_response(301)
                self.send_header("Location", "/blogs")
                self.end_headers()
            case ["blogs"]:
                default_response(self)

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
            case ["blogs", blog_id]:
                try:
                    blog_id = int(blog_id)
                except ValueError:
                    return_not_found(self)

                default_response(self)

                found = False
                for blog in blogs:
                    if blog_id == blog["id"]:
                        found = True
                        with open("resources/views/index.html", "r") as file:
                            app = file.read()

                        with open("resources/css/main.css", "r") as file:
                            app = app.replace("^mystyle^", file.read())

                        with open("resources/views/blog/show.html", "r") as file:
                            blog_show = file.read()
                            blog_show = blog_show.replace("^title^", blog["title"])
                            blog_show = blog_show.replace("^content^", blog["content"])
                            blog_show = blog_show.replace("^date^", blog["date"])

                        app = app.replace("^app^", blog_show)
                        self.wfile.write(bytes(app, "utf-8"))

                if not found:
                    return_not_found(self)

            case ["admin"]:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                with open("resources/views/index.html", "r") as file:
                    app = file.read()
                    with open("resources/views/auth/admin.html") as file:
                        blog_index = file.read()
                        app = app.replace("^app^", blog_index)
                        blogs_template = "<ul>"
                        for blog in blogs:
                            blogs_template += f"""
                                                <li>
                                                <a href="/blogs/{blog["id"]}">{blog["title"]}
                                                </a>
                                                <div class="action-buttons-container">

                                                <a href="/blogs/edit/{blog["id"]}">
                                                <button class="edit-button">Edit</button>
                                                </a>

                                                <a href="/blogs/delete/{blog["id"]}">
                                                <button class="delete-button">Delete</button>
                                                </a>

                                                </div>
                                                </li>
                                                """
                        blogs_template += "</ul>"
                        app = app.replace("^blogs^", blogs_template)
                    with open("resources/css/main.css") as file:
                        style = file.read()
                        app = app.replace("^mystyle^", style)
                self.wfile.write(bytes(app, "utf-8"))
            case ["blogs", "edit", blog_id]:
                try:
                    blog_id = int(blog_id)
                except ValueError:
                    return_not_found(self)

                found = False
                for blog in blogs:
                    if blog_id == blog["id"]:
                        found = True
                        default_response(self)
                        self.wfile.write(bytes(blog["title"], "utf-8"))

                if not found:
                    return_not_found(self)

            case _:
                return_not_found(self)


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
