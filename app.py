from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
from contentful import Client
from flaskext.markdown import Markdown
import pendulum
import os


app = Flask(__name__)
app.secret_key = os.environ.get("secret_key")
Markdown(app)

client = Client(
    os.environ.get("CTFL_SpaceID"),
    os.environ.get("CTFL_CDA"),
    environment="master",
)


@app.template_filter("strftime")
def _jinja2_filter_datetime(date, fmt="dddd MMMM Do YYYY"):
    date = pendulum.parse(f"{date.year}-{date.month}-{date.day}", strict=False)
    return date.format(fmt)


class subscribeForm(FlaskForm):
    email = StringField(
        "Your email",
        validators=[DataRequired(), Email()],
        render_kw={"class": "u-full-width"},
    )


@app.route("/", methods=["GET", "POST"])
def home():
    form = subscribeForm()
    if request.method == "POST" and form.validate():
        return form.email.data
    posts = client.entries({"content_type": "blogPost", "order": "-fields.publishDate"})
    return render_template("index.html", form=form, posts=posts)


@app.route("/post/<string:slug>")
def post(slug):
    post = client.entries({"content_type": "blogPost", "fields.slug": slug})
    if post:
        return render_template("post.html", post=post[0])
    return redirect(url_for("home"))
