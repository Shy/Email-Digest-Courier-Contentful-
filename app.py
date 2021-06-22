from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Email
from contentful import Client
from trycourier import Courier
from flaskext.markdown import Markdown
import pendulum
import os
import uuid


app = Flask(__name__)
app.secret_key = os.environ.get("secret_key")
Markdown(app)

CTFLclient = Client(
    os.environ.get("CTFL_SpaceID"),
    os.environ.get("CTFL_CDA"),
    environment="master",
)


courierClient = Courier()

@app.template_filter("strftime")
def _jinja2_filter_datetime(date, fmt="dddd MMMM Do YYYY"):
    date = pendulum.parse(f"{date.year}-{date.month}-{date.day}", strict=False)
    return date.format(fmt)


class subscribeForm(FlaskForm):
    email = StringField(
        "Your email",
        render_kw={"class": "u-full-width"},
    )
    phoneNumber = StringField(
        "Your phone number",
        render_kw={"class": "u-full-width"},
    )
    digest = BooleanField("Digest?",
                            render_kw={"class": "u-full-width"})

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):

            # your logic here e.g.
            if not (self.email.data or self.phoneNumber.data):
                self.email.errors.append('At least one field must have a value')
                return False
            else:
                return True

        return False


@app.route("/", methods=["GET", "POST"])
def home():
    form = subscribeForm()
    if request.method == "POST" and form.validate():
        recipient_id = uuid.uuid4()
        resp = courierClient.profiles.merge(
            recipient_id,
            {
                "phone_number": form.phoneNumber.data,
                "email": form.email.data
            } 
        )
        list_id = "thing.each"
        if form.digest.data:
            list_id = "thing.digest"
        courierClient.lists.subscribe(list_id, recipient_id)
        return(list_id)
    posts = CTFLclient.entries({"content_type": "blogPost", "order": "-fields.publishDate"})
    return render_template("index.html", form=form, posts=posts)


@app.route("/post/<string:slug>")
def post(slug):
    post = CTFLclient.entries({"content_type": "blogPost", "fields.slug": slug})
    if post:
        return render_template("post.html", post=post[0])
    return redirect(url_for("home"))
