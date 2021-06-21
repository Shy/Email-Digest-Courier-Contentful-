from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
import os

app = Flask(__name__)
app.secret_key = os.environ.get("secret_key")


class subscribeForm(FlaskForm):
    email = StringField("Your email", validators=[DataRequired(), Email()])


@app.route("/", methods=["GET", "POST"])
def hello_world():
    form = subscribeForm()
    if request.method == "POST" and form.validate():
        return form.email.data
    return render_template("index.html", form=form)
