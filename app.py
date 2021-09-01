import os
from flask import Flask, render_template, flash, request
from flask.helpers import url_for
from flask_wtf import FlaskForm
from werkzeug import datastructures
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError,RadioField
from wtforms.fields.core import FieldList, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length,URL
from datetime import datetime
import time
from datetime import date
from wtforms.widgets import TextArea
import re
import glob
import json


forms_path=glob.glob('/forms/*.json')


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
	
def validate_username(name:str):
	name=name.strip()
	if name==login_name:
		return True
	else:
		raise ValidationError("Incorrect username")

def validate_password(password):
	password=password.strip()
	if password==login_name:
		return True
	else:
		raise ValidationError("Incorrect password")
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	user_name=StringField("Username",validators=[DataRequired()])
	user_password=PasswordField("Password",validators=[DataRequired()])
	submit=SubmitField("Submit")

class CreateForm(FlaskForm):
	total_marks=IntegerField("Total marks for the test",validators=[DataRequired()])
	total_time=IntegerField('Duration limit of the test',validators=[DataRequired()])

class QuestionForm(FlaskForm):
	question_name=StringField("Question name",validators=[DataRequired()])
	question_type=SelectField("Which type of question is this?",choices=[
    ("mcq", "Multiple Choice Questions"),
    ("MulAns", "Multiple Answers"),
    ("PhoNum", "Phone Number"),
    ("SText", "Short Text"),
    ("LText", "Long Text"),
    ("PMCQ", "Picture Multiple Choice Questions"),
    ("PMA", "Picture Multiple Answers"),
    ("stmt", "Statement"),
    ("bool", "Yes/No"),
    ("email", "Email"),
    ("Lkrt", "Likert"),
    ("Rtg", "Rating"),
    ("date", "Date"),
    ("int", "Number"),
    ("fitb", "Fill in the blank"),
    ("fitbs", "Fill in the blanks"),
    ("drpdwn", "Dropdown"),
    ("wbst", "Website")])
	required=BooleanField('Required Question',validators=[DataRequired()])
	image_link=StringField('Image URL',validators=[URL()])
	question_layout=RadioField('Layout',choices=[('above','Image above question'),('side','Image on the side of the question')])
	# if question_type=="mcq":
	# 	name=StringField('hi')
	submit=SubmitField("Submit")

class MCQForm(FlaskForm):
	choices=FieldList(StringField('Choice'),label="test",min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[DataRequired()])
	submit=SubmitField('Submit')

class OneMoreQuestion(FlaskForm):
	yesonemore=BooleanField('Add one more question?')
	submit=SubmitField("Submit")



@app.route('/', methods=['GET', 'POST'])
def name():
	global logged_in_as
	try:
		if logged_in_as=="tsai":
			return redirect("/forms")
	except:
		pass
	logged_in_as=""
	user_name=None
	user_password=None
	form:FlaskForm=LoginForm()
	if form.validate_on_submit() and request.method=="POST":
		name=form.user_name.data
		password=form.user_password.data
		form.user_password.data=''
		form.user_name.data=''
		if name=='tsai' and password=='tsai99':
			logged_in_as="tsai"
			return redirect('/forms')
		else:
			flash("Login failed.",'warning')
			form.user_password.data=''
			form.user_name.data=''
			logged_in_as=""
			return render_template('login.html',user_name=user_name,user_password=user_password,form=form,login_status=logged_in_as)
	else:
		return render_template('login.html',user_name=user_name,user_password=user_password,form=form,login_status=logged_in_as)
	# if form.validate_on_submit():
	# 	name=form.user_name.data
	# 	password=form.user_password.data
	# 	if name=='tsai' and password=='tsai99':
	# 		flash('Logged in successfully!')
	# 		return forms()
	# 	else:
	# 		flash('Login failed.')
	# 		logged_in_as=""
	# 		return name(logged_in_as)
	

@app.route('/forms',methods=['GET','POST'])
def all_forms():
	try:
		if not logged_in_as:
			return redirect("/")
	except:
		return redirect("/")
	# content=[f"{url_for('edit_form')}/{file}" for file in forms_path]
	content=[f"{url_for('edit_form',hash=x.split('.')[0])}" for x in os.listdir('./forms')]
	return render_template("forms.html",files=os.listdir("./forms"),login_status=logged_in_as)

@app.route("/forms/edit/<hash>")
def edit_form(hash):
	try:
		if not logged_in_as:
			return redirect("/")
	except:
		return redirect("/")
	try:
		with open(f"forms/{hash}.json",encoding='utf-8') as filequiz:
			return "\n".join(filequiz.readlines())
	except OSError:
		return "An error occurred with the file name passed"

@app.route("/forms/<hash>")
def form(hash):
	try:
		if not logged_in_as:
			return redirect("/")
	except:
		return redirect("/")
	try:
		with open(f"forms/{hash}.json",encoding='utf-8') as filequiz:
			return "\n".join(filequiz.readlines())
	except OSError:
		return "An error occurred with the file name passed"
@app.route("/forms/create",methods=['GET','POST'])
def create_form():
	try:
		if not logged_in_as:
			return redirect("/")
	except:
		return redirect("/")
	form=QuestionForm()
	if form.validate_on_submit():
		global details_dict
		details_dict=form.data
		if form.question_type.data=="mcq":
			return redirect("/forms/create-mcq")
	return render_template('create-form.html',form=form,login_status=logged_in_as)

@app.route("/forms/create-mcq",methods=['GET','POST'])
def create_mcq():
	try:
		if not logged_in_as or not details_dict:
			return redirect("/")
	except:
		return redirect("/")
	choiceform=MCQForm()
	if choiceform.validate_on_submit():
		correct=choiceform.correct_choice.data-1
		choices=choiceform.choices.data
		choices=[x for x in choices if x.strip()]
		if correct>len(choices):
			flash("Correct choice not within bounds")
			choiceform.correct_choice.data=None
		elif len(choices)==1:
			flash("Only one unique choice exists!")
		else:
			details_dict.update({'choices':choices,'correct':correct})
			return redirect('/forms/create-new')	
	return render_template('mcq.html',form=choiceform,login_status=logged_in_as)

class FormName(FlaskForm):
	yesonemore=StringField("What is the name of the form?",validators=[DataRequired()])
	submit=SubmitField("Submit")

@app.route("/forms/create-new",methods=['GET','POST'])
def next_question():
	global q_list
	try:
		if q_list:
			pass
	except:
		q_list=[]
	try:
		if not logged_in_as:
			return redirect("/")
		# elif not details_dict:
		# 	return redirect("/")
	except:
		return redirect("/")
	OneMore=OneMoreQuestion()
	if OneMore.is_submitted():
		print("ji")
		q_list.append(details_dict)
		print(details_dict)
		if OneMore.yesonemore.data==True:
			return redirect('/forms/create')
		else:
			return redirect("/forms/name-setter")
			
	return render_template("nextquestion.html",form=OneMore)

import os.path

@app.route('/forms/name-setter',methods=['GET','POST'])
def nameform():
	nameform=FormName()
	if nameform.validate_on_submit():
		details_dict['name']=nameform.yesonemore.data
		if os.path.isfile(details_dict['name']):
			flash("That name has already been used")
		else:
			with open(f"forms/{details_dict['name']}.json","w") as file:
				json.dump(q_list,file)
			return redirect("/forms")
	return render_template("nextquestion.html",form=nameform)
	# nonlocal logged_in
	# if not logged_in:
	# 	user_name=None
	# 	user_password=None
	# form = LoginForm()
	# # Validate Form
	# if form.validate_on_submit():
	# 	if form.user_name.data=="tsai" and form.user_password.data=="tsai99":
	# 		flash("Invalid username and/or password!")
	# 		logged_in=False
	# 		user_name=None
	# 		user_password=None
	# 		return render_template("login.html", 
	# 		user_name = user_name,
	# 		user_password=user_password,
	# 		form = form)

	# 	elif form.user_name.data=="tsai" and form.user_password.data=="tsai99":
	# 		logged_in_as = form.user_name.data
	# 		logged_in=True
	# 		form.user_name.data = ''

	# 		flash("Logged in Successfully!")
						
	# return render_template("login.html", 
	# 	user_name = user_name,
	# 	user_password=user_password,
	# 	form = form)
if __name__ == '__main__':
    # This will be useful for running the app locally
    app.run(debug=False)
