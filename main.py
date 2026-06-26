from http.server import BaseHTTPRequestHandler, HTTPServer
import http.cookies
import json
import os
import urllib.parse
import uuid

HOST = "localhost"
PORT = 8080

SESSIONS = {}

with open("storage/blogs.json", "r") as file:
    blogs = json.load(file)


def load_env(file_path=".env"):
    if not os.path.exists(file_path):
        return

    with open(file_path, "r") as file:
        for line in file:
            line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)

                key = key.strip()
                value = value.strip().strip('"').strip("'")

                os.environ[key] = value


def return_not_found(handler: BaseHTTPRequestHandler):
    handler.send_response(404)
    handler.send_header("Content-type", "text/html")
    handler.end_headers()

    app = load_app()
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


def load_app():
    with open("resources/views/index.html", "r") as file:
        app = file.read()
    with open("resources/css/main.css", "r") as file:
        style = file.read()
        app = app.replace("^mystyle^", style)

    return app


def load_page(path_to_page):
    with open(path_to_page, "r") as file:
        page = file.read()

    return page


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        path = [s for s in self.path.split("/") if s]

        match path:
            case ["login"]:
                content_length = int(self.headers.get("Content-Length", 0))

                body = self.rfile.read(content_length)
                request_body = urllib.parse.parse_qs(body.decode("utf-8"))
                username = request_body["username"][0]
                password = request_body["password"][0]

                if username == os.getenv("ADMIN_USERNAME") and password == os.getenv(
                    "ADMIN_PASSWORD"
                ):
                    session_id = str(uuid.uuid4())
                    SESSIONS[session_id] = username
                    self.send_response(303)
                    self.send_header(
                        "Set-Cookie", f"session-id={session_id}; HttpOnly; Path=/"
                    )
                    self.send_header("Location", "/admin")
                    self.end_headers()
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"<h1>Wrong credentials</h1><br><a href='/login'>try again</a>"
                    )

            case ["blogs", "edit", blog_id]:
                try:
                    blog_id = int(blog_id)
                except ValueError:
                    return_not_found(self)
                    return
                content_length = int(self.headers.get("Content-Length", 0))

                body = self.rfile.read(content_length)
                request_body = urllib.parse.parse_qs(body.decode("utf-8"))
                title = request_body["title"][0]
                content = request_body["content"][0]
                date = request_body["date"][0]

                for blog in blogs:
                    if blog["id"] == blog_id:
                        blog["title"] = title
                        blog["content"] = content
                        blog["date"] = date
                with open("storage/blogs.json", "w") as file:
                    json.dump(blogs, file, indent=4)

                default_response(self)
                self.wfile.write(bytes(title, "utf-8"))

            case _:
                return_not_found(self)

    def do_GET(self):

        path = [s for s in self.path.split("/") if s]

        match path:
            case []:
                self.send_response(301)
                self.send_header("Location", "/blogs")
                self.end_headers()
            case ["blogs"]:
                default_response(self)

                app = load_app()

                blog_index = load_page("resources/views/blog/index.html")
                app = app.replace("^app^", blog_index)
                blogs_template = "<ul>"
                for blog in blogs:
                    blogs_template += f"""
                                        <li>
                                            <a href="/blogs/{blog["id"]}">{blog["title"]}</a>
                                            <p>{blog["date"]}</p>
                                        </li>
                                        """
                blogs_template += "</ul>"
                app = app.replace("^blogs^", blogs_template)

                self.wfile.write(bytes(app, "utf-8"))
            case ["blogs", "create"]:
                default_response(self)

                app = load_app()
                create_page = load_page("resources/views/blog/create.html")

                app = app.replace("^app^", create_page)

                self.wfile.write(bytes(app, "utf-8"))

            case ["blogs", blog_id]:
                try:
                    blog_id = int(blog_id)
                except ValueError:
                    return_not_found(self)
                    return

                found = False
                for blog in blogs:
                    if blog_id == blog["id"]:
                        default_response(self)
                        found = True
                        app = load_app()

                        blog_show = load_page("resources/views/blog/show.html")
                        blog_show = blog_show.replace("^title^", blog["title"])
                        blog_show = blog_show.replace("^content^", blog["content"])
                        blog_show = blog_show.replace("^date^", blog["date"])

                        app = app.replace("^app^", blog_show)
                        self.wfile.write(bytes(app, "utf-8"))

                if not found:
                    return_not_found(self)
                    return

            case ["login"]:
                default_response(self)

                login_page = load_page("resources/views/auth/login.html")

                app = load_app()

                app = app.replace("^app^", login_page)

                self.wfile.write(bytes(app, "utf-8"))

            case ["admin"]:

                cookie_header = self.headers.get("Cookie")
                cookie = http.cookies.SimpleCookie(cookie_header)

                session_cookie = cookie.get("session-id")
                session_id = session_cookie.value if session_cookie else None

                if session_id not in SESSIONS:
                    self.send_response(302)
                    self.send_header("Location", "/login")
                    self.end_headers()
                    return

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                app = load_app()
                admin_page = load_page("resources/views/auth/admin.html")
                app = app.replace("^app^", admin_page)

                blogs_template = ""

                if len(blogs) > 0:
                    blogs_template = "<ul>"
                    for blog in blogs:
                        blogs_template += f"""
                                        <li>
                                            <a href="/blogs/{blog["id"]}">{blog["title"]}</a>
                                            <div class="action-buttons-container">

                                                <a class="edit" href="/blogs/edit/{blog["id"]}">
                                                    <button class="edit-button">Edit</button>
                                                </a>

                                                <form class="delete-form" action="/blogs/delete/{blog["id"]}">
                                                    <button type="submit" class="delete-button">Delete</button>
                                                </form>

                                            </div>
                                        </li>
                                            """
                    blogs_template += "</ul>"
                else:
                    blogs_template += """<h2>No blogs to show</h2>"""

                app = app.replace("^blogs^", blogs_template)

                self.wfile.write(bytes(app, "utf-8"))
            case ["blogs", "edit", blog_id]:
                try:
                    blog_id = int(blog_id)
                except ValueError:
                    return_not_found(self)
                    return

                found = False
                for blog in blogs:
                    if blog_id == blog["id"]:
                        found = True
                        default_response(self)

                        blog_edit = load_page("resources/views/blog/edit.html")

                        app = load_app()

                        blog_edit = blog_edit.replace(
                            "^action_url^", f"/blogs/edit/{blog_id}"
                        )
                        blog_edit = blog_edit.replace("^title^", blog["title"])
                        blog_edit = blog_edit.replace("^content^", blog["content"])
                        blog_edit = blog_edit.replace("^date^", blog["date"])

                        app = app.replace("^app^", blog_edit)
                        self.wfile.write(bytes(app, "utf-8"))

                if not found:
                    return_not_found(self)
                    return

            case _:
                return_not_found(self)
                return

    def do_DELETE(self):
        path = [s for s in self.path.split("/") if s]

        match path:
            case ["blogs", "delete", blog_id]:
                try:
                    blog_id = int(blog_id)
                except ValueError:
                    return_not_found(self)
                    return

                print(blog_id)
                print(type(blog_id))

                for blog in blogs:
                    if blog_id == blog["id"]:
                        blogs.remove(blog)

                with open("storage/blogs.json", "w") as file:
                    json.dump(blogs, file, indent=4)

                self.send_response(204)
            case _:
                return_not_found(self)


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


load_env()
run()
