from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length,ValidationError
from datetime import datetime 
from datetime import date
from wtforms.widgets import TextArea
import re

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
app=Flask(__name__)
app.config['SECRET_KEY']='HMM YES YES MUCH'

def validate_name(name:str):
	name=name.strip()
	if len(name)==0:
		raise ValidationError("You cannot have only spaces in your name!")
	if not re.search("[A-Z|a-z]",name):
		raise ValidationError("You cannot have special characters in your name!")
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")

@app.route('/', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")
		
	return render_template("name.html", 
		name = name,
		form = form)

if __name__ == '__main__':
    # This will be useful for running the app locally
    app.run(debug=False)
