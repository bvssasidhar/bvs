#! /usr/bin/env python
from flask import Flask
from flask import render_template
from datetime import datetime
import re

app = Flask(__name__)

#@app.route("/")
#def home():
#    return "hi flask"

# @app.route("/hello/<name>")
# def hello_there(name):
#     nowinfo = datetime.now()
#     formatted_nowinfo = nowinfo.strftime("%A, %d %B, %Y at %X")
#     match_object = re.match("[a-zA-Z]+",name)
#     if match_object:
#         clean_name = match_object.group(0)
#     else:
#         clean_name = "Friend"
#     content = "Hello there, " + clean_name + "..! Now it is " + formatted_nowinfo + "."
#     return content

@app.route("/hello")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template("hello_there.html", name=name, date=datetime.now())


@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")

# Replace the existing home function with the one below
@app.route("/")
@app.route("/home/")
def home():
    return render_template("home.html")

# New functions
@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/others/")
def others():
    return render_template("others.html")


# if __name__ == '__main__':
#     ms1.run(host="0.0.0.0", port=int("5000"), debug=True)
