import glob
import json
import os
import re
import time
from datetime import date, datetime
from types import LambdaType

from flask import Flask, flash, render_template, request
from flask.helpers import url_for
from flask_wtf import FlaskForm
from werkzeug import datastructures
from werkzeug.utils import redirect
from wtforms import (BooleanField, PasswordField, RadioField, StringField,
                     SubmitField, ValidationError)
from wtforms.fields.core import Field, FieldList, IntegerField, SelectField
from wtforms.validators import URL, DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
import os.path


forms_path=glob.glob('/forms/*.json')


class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
app=Flask(__name__)
app.config['SECRET_KEY']='HMM YES YES MUCH'

## CLASSES START HERE

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
    ("wbst", "Website"),
	('upl','File Upload')])
	required=BooleanField('Required Question?')
	image_link=StringField('Image URL',validators=[URL()])
	score=IntegerField('Maximum marks for this question?',validators=[DataRequired()])
	question_layout=RadioField('Layout (only needed if you have an image URL)',choices=[('above','Image above question'),('side','Image on the side of the question')])
	submit=SubmitField("Submit")

class OneMoreQuestion(FlaskForm):
	yesonemore=BooleanField('Add one more question?')
	submit=SubmitField("Submit")


class MCQForm(FlaskForm):
	choices=FieldList(StringField('Choice'),label="test",min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[DataRequired()])
	submit=SubmitField('Submit')

class MultipleAnswer(FlaskForm):
	choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[DataRequired()]),label='Choices',min_entries=5,max_entries=5)
	correct_choices=FieldList(IntegerField(label='Choice',validators=[DataRequired()]),label='Correct choice indexes')
	submit=SubmitField("Submit")

class PictureMCQForm(FlaskForm):
	choices=FieldList(StringField('Choice'),label="test",min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[DataRequired()])
	image_link=StringField(label='IMAGE URL',validators=[DataRequired(),URL(),lambda x:x.endswith(('png','jpeg','jpg'))])
	question_layout=RadioField('Layout ',choices=[('above','Image above question'),('side','Image on the side of the question')])
	submit=SubmitField('Submit')

class PictureMultipleChoicesForm(FlaskForm):
	choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[DataRequired()]),label='Choices',min_entries=5,max_entries=5)
	correct_choices=FieldList(IntegerField(label='Choice',validators=[DataRequired()]),label='Correct choice indexes')
	image_link=StringField(label='IMAGE URL',validators=[DataRequired(),URL(),lambda x:x.endswith(('png','jpeg','jpg'))])
	question_layout=RadioField('Layout ',choices=[('above','Image above question'),('side','Image on the side of the question')])
	submit=SubmitField('Submit')

class LikertForm(FlaskForm):
	choices=FieldList(StringField(label='Likert option',filters=[lambda x:x.strip()],validators=[DataRequired()]),label='Choices',min_entries=7,max_entries=7)
	rating_choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[DataRequired()]),label='Rating strings',min_entries=5,max_entries=5)
	submit=SubmitField('Submit')

class FillInOneBlank(FlaskForm):
	sentence=StringField("What is the sentence? (Please indicate the blank with a series of underscores)",validators=[DataRequired()])
	blank=StringField("What is the correct blank/answer?",validators=[DataRequired()],filters=[lambda x:x.strip()])
	submit=SubmitField("Submit")

class FillinTheBlanks(FlaskForm):
	sentence=StringField("What is the sentence? (Please indicate the blank with two consecutive '$' signs)",validators=[DataRequired()])
	blank=FieldList(StringField("What is the correct blank/answer according to the order?",validators=[DataRequired()],filters=[lambda x:x.strip()]),label="Blanks",min_entries=5,max_entries=7)
	submit=SubmitField('Submit')

class Dropdown(FlaskForm):
	choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[DataRequired()]),label='Dropdown choices',min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[DataRequired()])
	submit=SubmitField('Submit')

class FileUpload(FlaskForm):
	FileNameShouldEndWith=StringField(label='What is the file extension required to be?',validators=[DataRequired()])
	submit=SubmitField("Submit")

class FormName(FlaskForm):
	yesonemore=StringField("What is the name of the form?",validators=[DataRequired()])
	submit=SubmitField("Submit")

## CLASSES END HERE

@app.route('/', methods=['GET', 'POST'])
def name():
	global logged_in_as
	try:
		if logged_in_as=="tsai":
			return redirect("/forms")
	except:
		pass
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
			return redirect("/forms/create/mcq")
		elif form.question_type.data=="mulans":
			return redirect("/forms/create/ma")
		elif form.question_type.data=="PMCQ":
			return redirect("/forms/create/pmcq")
		elif form.question_type.data=="PMA":
			return redirect("/forms/create/pma")
		elif form.question_type.data=="Lkrt":
			return redirect("/forms/create/likert")
		elif form.question_type.data=="fitb":
			return redirect("/forms/create/fiob")
		elif form.question_type.data=="fitbs":
			return redirect("/forms/create/fitb")
		elif form.question_type.data=="drpdwn":
			return redirect("/forms/create/drpdwn")
		elif form.question_type.data=="upl":
			return redirect("/forms/create/upl")
		else:
			return redirect('/forms/create-new')
	return render_template('create-form.html',form=form,login_status=logged_in_as)

@app.route("/forms/create-new",methods=['GET','POST'])
def next_question():
	global q_list
	global details_dict
	try:
		if q_list:
			pass
	except:
		q_list=[]
	try:
		if not logged_in_as:
			return redirect("/")
		try:
			details_dict
		except NameError:
			return redirect("/")
	except:
		return redirect("/")
	OneMore=OneMoreQuestion()
	if OneMore.is_submitted():
		q_list.append(details_dict)
		details_dict={}
		if OneMore.yesonemore.data==True:
			return redirect('/forms/create')
		else:
			return redirect("/forms/name-setter")
			
	return render_template("nextquestion.html",form=OneMore)

@app.route('/forms/name-setter',methods=['GET','POST'])
def nameform():
	global q_list
	global details_dict
	if not details_dict:
		return redirect("/")
	if not q_list:
		return redirect("/")
	nameform=FormName()
	if nameform.validate_on_submit():
		details_dict.update({'name':nameform.yesonemore.data})
		if os.path.isfile(f"forms/{nameform.yesonemore.data}.json"):
			flash("That name has already been used")
		else:
			with open(f"forms/{details_dict['name']}.json","w") as file:
				json.dump(q_list,file)
				q_list=[]
				details_dict={}
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

@app.route("/forms/create/mcq",methods=['GET','POST'])
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

@app.route("/forms/create/ma",methods=['GET','POST'])
def create_ma():
	try:
		if not logged_in_as or not details_dict:
			return redirect("/")
	except:
		return redirect("/")
	choiceform=MultipleAnswer()
	if choiceform.validate_on_submit():
		correct_choices=choiceform.correct_choices.entries
		choices=choiceform.choices.data
		choices=[x for x in choices if x.strip()]
		if len(choices)==0 or len(choices)==1:
			flash("Please enter more than one unique choice.")
		if len(correct_choices)>len(choices):
			flash("There are more correct choices than the choices!")
		else:
			details_dict.update({'choices':choices,'correct':correct_choices})
			return redirect('/forms/create-new')
	return render_template('MA.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/pmcq",methods=['GET','POST'])
def create_pmcq():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=PictureMCQForm()
	if choiceform.validate_on_submit():
		correct=choiceform.correct_choice.data-1
		choices=choiceform.choices.data
		imagelink=choiceform.image_link.data
		layout=choiceform.question_layout.data
		choices=[x for x in choices if x.strip()]
		if correct>len(choices):
			flash("Correct choice not within bounds")
		elif len(choices)==1:
			flash("Only one unique choice exists!")
		else:
			details_dict.update({'choices':choices,'correct':correct,'image_link':imagelink,'layout':layout})
			return redirect('/forms/create-new')	
	return render_template('mcq.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/pma",methods=['GET','POST'])
def create_pma():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=PictureMultipleChoicesForm()
	if choiceform.validate_on_submit():
		correct_choices=choiceform.correct_choices.entries
		choices=choiceform.choices.data
		image_link=choiceform.image_link.data
		layout=choiceform.question_layout.data
		choices=[x for x in choices if x.strip()]
		if len(choices)==0 or len(choices)==1:
			flash("Please enter more than one unique choice.")
		if len(correct_choices)>len(choices):
			flash("There are more correct choices than the choices!")
		else:
			details_dict.update({'choices':choices,'correct':correct_choices,'image_link':image_link,'layout':layout})
			return redirect('/forms/create-new')
	return render_template('PMA.html',form=choiceform,login_status=logged_in_as)

@app.route('/forms/create/likert',methods=['GET','POST'])
def create_likert():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=LikertForm()
	if choiceform.validate_on_submit():
		choices=choiceform.choices.data
		rating_choices=choiceform.rating_choices.data
		choices=[x for x in choices if x.strip()]
		details_dict.update({'choices':choices,'rating_choices':rating_choices})
		return redirect('/forms/create-new')
	return render_template('likert.html',form=choiceform,login_status=logged_in_as)

@app.route('/forms/create/fiob',methods=['GET','POST'])
def create_FIOB():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=FillInOneBlank()
	if choiceform.validate_on_submit():
		sentence=choiceform.sentence.data
		blank=choiceform.blank.data
		if "$$" not in sentence:
			flash("There is no blank present in the sentence")
		elif sentence.count("$$")>1:
			flash("Only one blank is needed!")
		details_dict.update({'sentence':sentence,'blank':blank})
		return redirect('/forms/create-new')
	return render_template('FIOB.html',form=choiceform,login_status=logged_in_as)

@app.route('/forms/create/fitb',methods=['GET','POST'])
def create_FITB():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=FillinTheBlanks()
	if choiceform.validate_on_submit():
		sentence=choiceform.sentence.data
		blank=choiceform.blank.data
		if "$$" not in sentence:
			flash("There is no blank present in the sentence")
		elif len(blank)!=sentence.count("$$"):
			flash("Something is wrong with the number of blanks or sentence")
		details_dict.update({'sentence':sentence,'blank':blank})
		return redirect('/forms/create-new')
	return render_template('FIOB.html',form=choiceform,login_status=logged_in_as)

@app.route('/forms/create/dd',methods=['GET','POST'])
def create_dd():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=Dropdown()
	if choiceform.validate_on_submit():
		rawchoices=choiceform.choices.data
		choices=[]
		for choice in rawchoices:
			if choice not in choices:
				choices.append(choice.strip())
		correct_choice=choiceform.correct_choice.data-1
		if correct_choice>len(choices):
			flash("You've entered an incorrect index for the correct choice")
		elif correct_choice<0:
			flash("Positive indexes only.")
		details_dict.update({'choices':choices,'correct':correct_choice})
		return redirect('/forms/create-new')
	return render_template('MCQ.html',form=choiceform,login_status=logged_in_as)

@app.route('/forms/create/upload',methods=['GET','POST'])
def create_upload():
	try:
		if not logged_in_as:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=FileUpload()
	if choiceform.validate_on_submit():
		file_ext=choiceform.FileNameShouldEndWith.data
		file_ext=file_ext.split()
		details_dict.update({'file_ext':file_ext})
		return redirect('/forms/create-new')
	return render_template('FIOB.html',form=choiceform,login_status=logged_in_as)


if __name__ == '__main__':
    # This will be useful for running the app locally
    app.run(debug=False)
