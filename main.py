from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DecimalField, SelectField
from wtforms.validators import DataRequired, URL
import os


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
Bootstrap5(app)

db = SQLAlchemy(model_class=Base)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db.init_app(app)


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats: Mapped[str] = mapped_column(String(50), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(50), nullable=False)


class AddCafeForm(FlaskForm):
    name = StringField("Name of Cafe", validators=[DataRequired()])
    map_url = StringField("Google Maps URL", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    location = StringField("Cafe Location", validators=[DataRequired()])
    has_sockets = BooleanField("Are There Sockets?")
    has_toilet = BooleanField("Is There a Toilet?")
    has_wifi = BooleanField("Is There Wi-Fi?")
    can_take_calls = BooleanField("Can You Take Calls?")
    seats = SelectField('Amount of Seats', choices=[('0-10', '0-10'), ('11-20', '11-20'),
                                                    ('21-30', '21-30'), ('31-40', '31-40'), ('41-50', '41-50'),
                                                    ('50+', '50+')], validators=[DataRequired()])
    coffee_price = DecimalField("Coffee Price (£)", validators=[DataRequired()])
    submit = SubmitField("Submit")


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def all_cafes():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    return render_template("index.html", all_cafes=cafes)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=f"£{'{:.2f}'.format(round(form.coffee_price.data, 2))}"
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("all_cafes"))
    return render_template("add.html", form=form)


@app.route("/delete/<int:cafe_id>", methods=["GET", "POST"])
def delete_cafe(cafe_id):
    chosen_cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(chosen_cafe)
    db.session.commit()
    return redirect(url_for('all_cafes'))


@app.route("/edit/<int:cafe_id>", methods=["GET", "POST"])
def edit_cafe(cafe_id):
    chosen_cafe = db.get_or_404(Cafe, cafe_id)
    edit_form = AddCafeForm(
        name=chosen_cafe.name,
        map_url=chosen_cafe.map_url,
        img_url=chosen_cafe.img_url,
        location=chosen_cafe.location,
        has_sockets=chosen_cafe.has_sockets,
        has_toilet=chosen_cafe.has_toilet,
        has_wifi=chosen_cafe.has_wifi,
        can_take_calls=chosen_cafe.can_take_calls,
        seats=chosen_cafe.seats,
        coffee_price=float(chosen_cafe.coffee_price.replace('£', ''))
    )
    if edit_form.validate_on_submit():
        chosen_cafe.name = edit_form.name.data
        chosen_cafe.map_url = edit_form.map_url.data
        chosen_cafe.img_url = edit_form.img_url.data
        chosen_cafe.location = edit_form.location.data
        chosen_cafe.has_sockets = edit_form.has_sockets.data
        chosen_cafe.has_toilet = edit_form.has_toilet.data
        chosen_cafe.has_wifi = edit_form.has_wifi.data
        chosen_cafe.can_take_calls = edit_form.can_take_calls.data
        chosen_cafe.seats = edit_form.seats.data
        chosen_cafe.coffee_price = f"£{'{:.2f}'.format(round(edit_form.coffee_price.data, 2))}"
        db.session.commit()
        return redirect(url_for("all_cafes"))
    return render_template("add.html", form=edit_form)


if __name__ == "__main__":
    app.run(debug=True)