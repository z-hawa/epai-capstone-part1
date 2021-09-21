import difflib
import glob
import json
import os
import re
from flask_wtf import file

import jellyfish
import os.path
import time
import signal
from datetime import date, datetime

from flask import Flask, flash, render_template, request
from flask.helpers import send_file, url_for
from flask.templating import render_template_string
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.form import SUBMIT_METHODS
from werkzeug.utils import redirect, validate_arguments,secure_filename
from wtforms import (BooleanField, PasswordField, RadioField, StringField,
                     SubmitField, ValidationError)
from wtforms.fields.core import (DateField, Field, FieldList, IntegerField,
                                 SelectField, SelectMultipleField)
from wtforms.fields.simple import FileField
from wtforms.validators import URL, DataRequired, EqualTo, InputRequired, Length, NumberRange, Required
from wtforms.widgets import TextArea


def timer():
	raise TimeoutError("Timed out.")


forms_path=glob.glob('/forms/*.json')


class MyForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])
app=Flask(__name__)
app.config['SECRET_KEY']='HMM YES YES MUCH'
app.config['UPLOAD_FOLDER']="forms/"
## CLASSES START HERE


class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[InputRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	user_name=StringField("Username",validators=[InputRequired()])
	user_password=PasswordField("Password",validators=[InputRequired()])
	submit=SubmitField("Submit")

class CreateForm(FlaskForm):
	total_marks=IntegerField("Total marks for the test",validators=[InputRequired()])
	total_time=IntegerField('Duration limit of the test',validators=[InputRequired()])

class QuestionForm(FlaskForm):
	question_name=StringField("Question name",validators=[InputRequired()])
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
	score=IntegerField('Maximum marks for this question?',validators=[InputRequired()])
	submit=SubmitField("Submit")

class OneMoreQuestion(FlaskForm):
	yesonemore=BooleanField('Add one more question?')
	submit=SubmitField("Submit")


class MCQ(FlaskForm):
	choices=FieldList(StringField('Choice'),label="test",min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[InputRequired()])
	submit=SubmitField('Submit')

class MultipleAnswer(FlaskForm):
	choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[InputRequired()]),label='Choices',min_entries=5,max_entries=5)
	correct_choices=FieldList(IntegerField(label='Choice',validators=[InputRequired()]),label='Correct choice indexes')
	submit=SubmitField("Submit")

class PictureMCQ(FlaskForm):
	choices=FieldList(StringField('Choice'),label="test",min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[InputRequired()])
	image_link=StringField(label='IMAGE URL',validators=[InputRequired(),URL()])
	question_layout=RadioField('Layout ',choices=[('above','Image above question'),('side','Image on the side of the question')])
	submit=SubmitField('Submit')

class PictureMultipleChoices(FlaskForm):
	choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[InputRequired()]),label='Choices',min_entries=5,max_entries=5)
	correct_choices=FieldList(IntegerField(label='Choice',validators=[InputRequired()]),label='Correct choice indexes')
	image_link=StringField(label='IMAGE URL',validators=[InputRequired(),URL(),lambda x:x.endswith(('png','jpeg','jpg'))])
	question_layout=RadioField('Layout ',choices=[('above','Image above question'),('side','Image on the side of the question')])
	submit=SubmitField('Submit')

class Likert(FlaskForm):
	choices=FieldList(StringField(label='Likert option',filters=[lambda x:x.strip()],validators=[InputRequired()]),label='Choices',min_entries=7,max_entries=7)
	rating_choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[InputRequired()]),label='Rating strings',min_entries=5,max_entries=5)
	submit=SubmitField('Submit')

class FillInOneBlank(FlaskForm):
	sentence=StringField("What is the sentence? (Please indicate the blank with a series of underscores)",validators=[InputRequired()])
	blank=StringField("What is the correct blank/answer?",validators=[InputRequired()],filters=[lambda x:x.strip()])
	submit=SubmitField("Submit")

class FillinTheBlanks(FlaskForm):
	sentence=StringField("What is the sentence? (Please indicate the blank with two consecutive '$' signs)",validators=[InputRequired()])
	blank=FieldList(StringField("What is the correct blank/answer according to the order?",validators=[InputRequired()],filters=[lambda x:x.strip()]),label="Blanks",min_entries=5,max_entries=7)
	submit=SubmitField('Submit')

class Dropdown(FlaskForm):
	choices=FieldList(StringField(label='Choice',filters=[lambda x:x.strip()],validators=[InputRequired()]),label='Dropdown choices',min_entries=5,max_entries=5)
	correct_choice=IntegerField('Correct choice index number',validators=[InputRequired()])
	submit=SubmitField('Submit')

class FileUpload(FlaskForm):
	FileNameShouldEndWith=StringField(label='What is the file extension required to be?',validators=[InputRequired()])
	submit=SubmitField("Submit")

class FormName(FlaskForm):
	yesonemore=StringField("What is the name of the form?",validators=[InputRequired(),lambda x,y:x not in ["create","create-new","edit","upload-new","download"],lambda x,y:"/" not in x])
	time=IntegerField("How much time should be given (in minutes) to solve the quiz?",validators=[InputRequired()])
	submit=SubmitField("Submit")

class Integer(FlaskForm):
	yesonemore=IntegerField('What is the correct integer?',validators=[InputRequired()])
	submit=SubmitField("Submit")

class Boolean(FlaskForm):
	yesonemore=IntegerField('What is the correct option?',validators=[InputRequired()])
	submit=SubmitField("Submit")
## FORM CREATION CLASSES END HERE

## FORM FILLING CLASSES START HERE
class IntegerForm(FlaskForm):
	choice=IntegerField("Answer?",validators=[InputRequired()])
	submit=SubmitField("Submit")

class BooleanForm(FlaskForm):
	choice=BooleanField("True or False? (Check if true)",validators=[InputRequired()])
	submit=SubmitField("Submit")

class MCQForm(FlaskForm):
	selected_choice=RadioField("Choices",validators=[InputRequired()])
	submit=SubmitField("Submit")

class MultipleAnswerForm(FlaskForm):
	choices=SelectMultipleField(label="Select all that are right")
	submit=SubmitField("Submit")

class PhoneNumberForm(FlaskForm):
	number=IntegerField("Phone Number",validators=[InputRequired(),NumberRange(1_000_000_000,9_999_999_999)])
	submit=SubmitField("Submit")

class STextForm(FlaskForm):
	text=StringField("Enter the response",validators=[InputRequired(),Length(1,144,"failed")])
	submit=SubmitField("Submit")

class LTextForm(FlaskForm):
	text=StringField("Enter the response",validators=[InputRequired(),Length(50,500,"failed")])
	submit=SubmitField("Submit")

class YesNoForm(FlaskForm):
	choice=BooleanField("Yes or No?",validators=[InputRequired()])
	submit=SubmitField("Submit")

class EmailForm(FlaskForm):
	email=StringField("Email",validators=[InputRequired(),lambda x,y:len(x,y.split("@"))==2])
	submit=SubmitField("Submit")

class LikertForm(FlaskForm):
	choices=[]
	rating_choices=["11","22","33"]
	choices_passed=["1","2","3"]
	choices=RadioField(
        'Choice?',
        [InputRequired()],
        choices=[('choice1', 'Choice One'), ('choice2', 'Choice Two')], default='choice1'
    )
	submit=SubmitField("Submit")


class RatingForm(FlaskForm):
	rating=IntegerField(label="Rating",validators=[InputRequired(),lambda x,y:0<=x<=5])
	submit=SubmitField("Submit")

class DateForm(FlaskForm):
	date=DateField(label="Date",validators=[InputRequired()])
	submit=SubmitField("Submit")

class NumberForm(FlaskForm):
	number=StringField(label="Number",validators=[InputRequired(),lambda x,y:x.isdigit()],filters=(lambda x:x.strip()))
	submit=SubmitField("Submit")

class FillInABlankForm(FlaskForm):
	blank=StringField(validators=[InputRequired()])

class FillInBlanksForm(FlaskForm):
	blanks=FieldList(StringField(validators=[InputRequired()],label='What are the blanks (in order of the blanks in the sentence.)'))

class DropDownForm(FlaskForm):
	dropdown=SelectField('Select one',validators=[InputRequired()])
	submit=SubmitField("Submit")

class FileUploadForm(FlaskForm):
	file=FileField(label="Upload file",validators=[InputRequired(),FileAllowed(['pdf','txt'])])
	submit=SubmitField("Submit")

class WebsiteLinkForm(FlaskForm):
	websitelink=StringField(label="URL for website",validators=[InputRequired(),URL()])
	submit=SubmitField("Submit")

## END OF FORM FILL CLASSES

class QuizUpload(FlaskForm):
	file=FileField(label="Upload file",validators=[InputRequired(),FileAllowed('json')])
	submit=SubmitField("Submit")

## EDIT FORM CLASSES

class EditForm(FlaskForm):
	nextquestion=SubmitField("Next question")
	beforequestion=SubmitField("Previous question")
	create_new_question=SubmitField("Insert new question")
	delete_question=SubmitField('Delete question')
	change_time=SubmitField("Change time")

class TimeForm(FlaskForm):
	yesonemore=IntegerField("Time?",validators=[InputRequired()])
	submit=SubmitField("Submit")
@app.route("/forms/download/<hmm>")
def download_file(hmm):
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
	except:
		return redirect("/")
	if hmm not in os.listdir("forms"):
		return "Invalid download"
	return send_file(f"forms/{hmm}",as_attachment=True)
@app.route('/', methods=['GET', 'POST'])
def name():
	global logged_in_as
	global logged_in
	try:
		if logged_in:
			return redirect("/forms")
	except:
		logged_in_as=''
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
			logged_in=True
			return redirect('/forms')
		else:
			flash("Login failed.",'warning')
			form.user_password.data=''
			form.user_name.data=''
			logged_in_as=""
			logged_in=False
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
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
	except:
		return redirect("/")
	# content=[f"{url_for('edit_form')}/{file}" for file in forms_path]
	content=[f"{url_for('edit_form',hash=x.split('.')[0])}" for x in os.listdir('/forms') if x.endswith('.json')]
	return render_template("forms.html",files=os.listdir("./forms"))

@app.route("/forms/upload-new",methods=['GET','POST'])
def upload_form():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
	except:
		return redirect("/")
	form=QuizUpload()
	return render_template("upload_form.html",form=form)

@app.route("/uploader",methods=['GET','POST'])
def upload_form_():
	keys={"question_name","question_type","time","required"}
	if request.method == 'POST':
		try:
			f=request.files['file']
			if secure_filename(f.filename) in os.listdir("forms"):
				flash("You need to upload a file with a different name as a form with that name already exists.")
				time.sleep(5)
				return redirect("/forms/upload-new")
			f.save(f"forms/{secure_filename(f.filename)}")
			filetobedumped=json.load(open(f"forms/{secure_filename(f.filename)}"))
			print(f.stream.read(),filetobedumped)
		except Exception as exc:
			return redirect("/forms/upload-new")
		if type(filetobedumped)!=list:
			os.remove(f"forms/{secure_filename(f.filename)}")
			flash("Invalid file")
			return redirect("/forms/upload-new")
		else:
			for e in filetobedumped:
				if len(keys.intersection(e.keys()))!=len(keys):				
					flash("Invalid File")
					os.remove(f"forms/{secure_filename(f.filename)}")
					return redirect("/forms/upload-new")
		flash("Success")
		return redirect("/forms/upload-new")

@app.route("/forms/edit/<hash>",methods=['GET','POST'])
def edit_form(hash):
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
	except:
		return redirect("/")
	try:
		with open(f"forms/{hash}.json",encoding='utf-8') as filequiz:
			global q_list
			q_list=json.load(filequiz)
			global name_of_edit
			try:
				if name_of_edit:
					pass
			except:
				try:
					name_of_edit=q_list[-1]["name"]
				except:
					name_of_edit=q_list[0]["name"]
			current=0
			form=EditForm()
			current_question:dict=q_list[current]
			current_question.pop("csrf_token",None)
			current_question.pop("submit",None)
			if form.validate_on_submit():
				if form.nextquestion.data:
					if not len(q_list)<=current+1:
						current+=1
						current_question:dict=q_list[current]
						current_question.pop("csrf_token",None)
						current_question.pop("submit",None)
					else:
						flash('This is the last question!')
				elif form.beforequestion.data:
					if not len(q_list)>=current+1:
						current-=1
						current_question:dict=q_list[current]
						current_question.pop("csrf_token",None)
						current_question.pop("submit",None)
					else:
						flash('This is the first question!')
				elif form.create_new_question.data:
					current=None					
					return redirect("/forms/create")
				elif form.delete_question.data:
					q_list.pop(current)
					flash("Question deleted successfully")
					if len(q_list)==0:
						return redirect("/forms/create")
					current_question.pop("csrf_token",None)
					current_question.pop("submit",None)
				elif form.change_time.data:
					name_of_edit=name_of_edit
					return redirect("/forms/create/time-setter")
			return render_template("edit.html",q_list=current_question,form=form,d={'mcq': 'Multiple Choice Questions', 'MulAns': 'Multiple Answers', 'PhoNum': 'Phone Number', 'SText': 'Short Text', 'LText': 'Long Text', 'PMCQ': 'Picture Multiple Choice Questions', 'PMA': 'Picture Multiple Answers', 'stmt': 'Statement', 'bool': 'Yes/No', 'email': 'Email', 'Lkrt': 'Likert', 'Rtg': 'Rating', 'date': 'Date', 'int': 'Number', 'fitb': 'Fill in the blank', 'fitbs': 'Fill in the blanks', 'drpdwn': 'Dropdown', 'wbst': 'Website'})
	except OSError:
		return "An error occurred with the file name passed"
@app.route("/forms/create/time-setter",methods=['GET','POST'])
def test_time():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
	except:
		return redirect("/")
	try:
		if not name_of_edit:
			redirect("/forms")
	except:
		redirect("/forms")
	hmm=TimeForm()
	if hmm.validate_on_submit():
		q_list[-1].update({"time":hmm.yesonemore.data})
		with open(f"forms/{name_of_edit}.json","w") as file:
			json.dump(q_list,file)
		return redirect(f"/forms/edit/{name_of_edit}")
	return render_template("nextquestion.html",form=hmm)
@app.route("/forms/<hash>",methods=["GET",'POST'])
def form(hash):
		with open(f"forms/{hash}.json",encoding='utf-8') as filequiz:
			form_q_list:list=json.load(filequiz)
			try:
				time_for_form=form_q_list[-1]["time"]
				#csrf=form_q_list[-1]["csrf_token"]
			except:
				time_for_form=form_q_list[0]["time"]
				#csrf=form_q_list[0]["csrf_token"]
			results=[]
			score=0
			flag=False
			def handler():
				raise TimeoutError("Error")
			try:
				signal.signal(signal.SIGALRM, handler)
				signal.alarm(time_for_form*60)
			except:
				pass
			try:
				for i,q in enumerate(form_q_list,start=1):
					q_type=q["question_type"]
					if q_type=="mcq":
						picture_link=None
						former=MCQForm()
						former.selected_choice.choices=q["choices"]
						form_attribs=[former.selected_choice]
					elif q_type=="MulAns":
						picture_link=None
						former=MultipleAnswerForm()
						former.choices.choices=q["choices"]
						form_attribs=[former.choices]
					elif q_type=="PMCQ":
						former=MCQForm()
						former.selected_choice.choices=q["choices"]
						form_attribs=[former.selected_choice]
						picture_link=q["image_link"]
						layout=q["layout"]
					elif q_type=="PMA":
						former=MultipleAnswerForm()
						former.choices.choices=q["choices"]
						form_attribs=[former.choices]
						picture_link=q["image_link"]
						layout=q["layout"]	
					elif q_type=="PhoNum":
						picture_link=None
						former=PhoneNumberForm()
						form_attribs=[former.number]
					elif q_type=="SText":
						picture_link=None
						former=STextForm()
						form_attribs=[former.text]
					elif q_type=="LText":
						picture_link=None
						former=LTextForm()
						form_attribs=[former.text]
					elif q_type=="stmt":
						picture_link=None
						statement=True
						former=[]
					elif q_type=="bool":
						picture_link=None
						former=BooleanForm()
						form_attribs=[former.choice]
					elif q_type=="email":
						picture_link=None
						former=EmailForm()
						form_attribs=[former.email]
					# elif q_type=="Lkrt":
					# 	picture_link=None
					# 	former=LikertForm()
					# 	global choices
					# 	choices=q["choices"]
					# 	global rating_choices
					# 	rating_choices=q["rating_choices"]
					# 	form_attribs=[former.rating_choices,former.choices]
					elif q_type=="fitb":
						picture_link=None
						former=FillInABlankForm()
						former.blank.label=q["sentence"].replace("$$","_________________")
						form_attribs=[former.blank]
					elif q_type=="fitbs":
						picture_link=None
						former=FillInBlanksForm()
						former.blank.label=q["sentence"].replace("$$","_________________")
						form_attribs=[former.blanks]
					elif q_type=="drpdwn":
						picture_link=None
						former=DropDownForm()
						former.dropdown.choices=q["choices"]
						form_attribs=[former.dropdown]
					elif q_type=="upl":
						picture_link=None
						former=FileUploadForm()
						form_attribs=[former.file]
					elif q_type=="wbst":
						picture_link=None
						former=WebsiteLinkForm()
						form_attribs=[former.websitelink]
					elif q_type=="int":
						picture_link=None
						former=IntegerForm()
						form_attribs=[former.choice]
					elif q_type=="date":
						picture_link=None
						former=DateForm()
						form_attribs=[former.date]
					elif q_type=="Rtg":
						picture_link=None
						former=RatingForm()
						form_attribs=[former.rating]
					try:
						layout
					except:
						layout=None
					try:
						picture_link
					except:
						picture_link=None
					if former.validate_on_submit():
						flag=True
					elif former.is_submitted() and not former.validate() and not q["required"]:
						flag=True
					else:
						flag=False
					if flag==True:
							for f in form_attribs:
								if q_type=="mcq" or q_type=="PMCQ":
									data=q["score"] if former.selected_choice.data==q["choices"][q["correct_choice"]] else 0
									score=data+score
									data="Score - "+str(data)
								elif q_type=="MulAns" or q_type=="PMA":
									selected_choices=former.choices.data
									correct_choices:list=q["correct_choices"]
									correct=list(set(correct_choices).intersection(selected_choices))
									data=len(correct)/len(correct_choices) if correct else 0
									data=round(data*q["score"])
									score=data+score
									data="Score - "+str(data)
								elif q_type=="int":
									data=q["score"] if former.choice.data==q["correct"] else 0
									score=data+score
									data="Score - "+str(data)
								elif q_type=="bool":
									data=q["score"] if former.choice.data==q["correct"] else 0
									score=data+score
									data="Score - "+str(data)
								elif q_type=="upl":
									student_files = [doc for doc in os.listdir("uploadedfiles") if doc.endswith(('.txt','.pdf'))]
									student_notes =[open(f"uploadedfiles/{File}").read() for File in  student_files]
									filedata=request.files["file"]
									print(os.path.isfile(f"uploadedfiles/{secure_filename(filedata.filename)}"))
									if os.path.isfile(f"uploadedfiles/{secure_filename(filedata.filename)}"):
										print("hi")
										num=len([f for f in os.listdir("uploadedfiles/") if f.endswith(secure_filename(filedata.filename))])
										filedata.save(f"uploadedfiles/({num}){secure_filename(filedata.filename)}")
									else:
										filedata.save(f"uploadedfiles/{secure_filename(filedata.filename)}")
									current=(open(f"uploadedfiles/{secure_filename(filedata.filename)}")).read()
									plagiarism_results=[]
									for student_note in student_notes:
										plagiarism_results.append(jellyfish.jaro_similarity(student_note,current))
									if not plagiarism_results:
										avg="Could not find the plagiarism score as there was no previous file"
									else:
										avg=(sum(plagiarism_results)/len(plagiarism_results)).__round__(4)
									data="Question : "+q["question_type"]+" ; Plagiarism score : "+str(avg)
								else:
									data=str(f.data) if f.data else "None"+"; Score - "+str(q["score"])
									score=q["score"]+score
								
								if not former.validate():
									data=data+" ; This question wasn't validated as the question wasn't a required one."
								results.extend([f"{q['question_name']} : {(data)} \n"])
							if i==len(form_q_list):
								results.insert(0,f"Score of the quiz was {score}")
								with open(f'forms/results/{hash}{time.time().__round__()}.json',"w") as g:
									json.dump(results,g)
								flag=False
								try:
									signal.alarm(0) # Alarm is stopped so the rest of the program can go ahead without any problems
								except:
									pass
								return render_template_string(f"Quiz completed ! \n You can now go close this page!")
							flag=False
							continue
							
							
					if q_type=="upl":
						return render_template("file copy.html",question_string=q["question_name"],form=former)
					return render_template("baseform.html",form=former,form_attribs=form_attribs,question_string=q["question_name"],picture_link=picture_link,layout=layout)
			except TimeoutError:
				return "You could not complete the quiz in time... \n Good luck next time"
			

@app.route("/forms/<hash>/results")
def form_results(hash):
	files=os.listdir("forms/results/")
	files=[f for f in files if f.endswith(".json") and f.startswith(hash)]
	if not files:
		return "There are no results for that file until now"
	final=[]
	for f in files:
		final.append(f"{'~~~'*35}<br/>This version of results was obtained at {time.ctime(int(f.split(hash)[1].split('.')[0]))}")
		with open(f"forms/results/{f}") as g:
			for e in json.load(g):
				final.append(e)
	return '<br/>'.join(final)

@app.route("/forms/create",methods=['GET','POST'])
def create_form():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
	except:
		return redirect("/")
	form=QuestionForm()
	if form.validate_on_submit():
		global details_dict
		details_dict=form.data
		if form.question_type.data=="mcq":
			return redirect("/forms/create/mcq")
		elif form.question_type.data=="MulAns":
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
		# elif form.question_type.data=="upl":
		# 	return redirect("/forms/create/upload")
		else:
			return redirect('/forms/create-new')
	return render_template('create-form.html',form=form,login_status=logged_in_as)

@app.route("/forms/create-new",methods=['GET','POST'])
def next_question():
	global logged_in
	global q_list
	global details_dict
	try:
		if q_list:
			pass
	except:
		q_list=[]
	try:
		if not logged_in:
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
			global name_of_edit
			try:
				if name_of_edit:
					print("e")
					with open(f"forms/{name_of_edit}.json","w") as file:
						json.dump(q_list,file)
						q_list=[]
						details_dict={}
						return redirect(f"/forms/edit/{name_of_edit}")
			except:
				pass
			return redirect("/forms/create/name-setter")
			
	return render_template("nextquestion.html",form=OneMore)

@app.route('/forms/create/name-setter',methods=['GET','POST'])
def nameform():
	global q_list
	global details_dict
	try:
		if details_dict:
			pass
	except:
		return redirect("/")
	try:
		if q_list:
			pass
	except:
		return redirect('/')
	nameform=FormName()
	if nameform.validate_on_submit():
		details_dict.update({'name':nameform.yesonemore.data,'time':nameform.time.data})
		q_list[-1].update(details_dict)
		if os.path.isfile(f"forms/{nameform.yesonemore.data}.json"):
			flash("That name has already been used")
		else:
			with open(f"forms/{details_dict['name']}.json","w") as file:
				json.dump(q_list,file)
				q_list=[]
				details_dict={}
				return redirect("/forms")
	return render_template("nextquestion copy.html",form=nameform)
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
	global logged_in
	try:
		if not logged_in or not details_dict:
			return redirect("/")
	except:
		return redirect("/")
	choiceform=MCQ()
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
			details_dict.update({'choices':choices,'correct_choice':correct})
			return redirect('/forms/create-new')	
	return render_template('mcq.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/ma",methods=['GET','POST'])
def create_ma():
	global logged_in
	try:
		if not logged_in or not details_dict:
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
			details_dict.update({'choices':choices,'correct_choices':correct_choices})
			return redirect('/forms/create-new')
	return render_template('MA.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/pmcq",methods=['GET','POST'])
def create_pmcq():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=PictureMCQ()
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
			details_dict.update({'choices':choices,'correct_choice':correct,'image_link':imagelink,'layout':layout})
			return redirect('/forms/create-new')	
	return render_template('PMCQ.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/int",methods=['GET','POST'])
def create_int():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=Integer()
	if choiceform.validate_on_submit():
		correct=choiceform.yesonemore.data
		details_dict.update({'correct':correct})
		return redirect('/forms/create-new')	
	return render_template('nextquestion copy.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/bool",methods=['GET','POST'])
def create_bool():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=Boolean()
	if choiceform.validate_on_submit():
		correct=choiceform.yesonemore.data
		details_dict.update({'correct':correct})
		return redirect('/forms/create-new')	
	return render_template('nextquestion copy.html',form=choiceform,login_status=logged_in_as)

@app.route("/forms/create/pma",methods=['GET','POST'])
def create_pma():
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=PictureMultipleChoices()
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
	global logged_in
	try:
		if not logged_in:
			return redirect("/")
		try:details_dict
		except NameError:return redirect("/")
	except:
		return redirect("/")
	choiceform=Likert()
	if choiceform.validate_on_submit():
		choices=choiceform.choices.data
		rating_choices=choiceform.rating_choices.data
		choices=[x for x in choices if x.strip()]
		details_dict.update({'choices':choices,'rating_choices':rating_choices})
		return redirect('/forms/create-new')
	return render_template('likert.html',form=choiceform,login_status=logged_in_as)

@app.route('/forms/create/fiob',methods=['GET','POST'])
def create_FIOB():
	global logged_in
	try:
		if not logged_in:
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
	global logged_in
	try:
		if not logged_in:
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
	global logged_in
	try:
		if not logged_in:
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




if __name__ == '__main__':
    # This will be useful for running the app locally
    app.run(debug=False)
