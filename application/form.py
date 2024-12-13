from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,EmailField,PasswordField
from wtforms.validators import DataRequired,Email,Length


class ContactForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email = EmailField('Email address', validators=[DataRequired(),Email()])
    suggestion=StringField("Suggestion",validators=[DataRequired()])
    message=StringField("Additional Message",validators=[DataRequired()])
    submit=SubmitField("Submit")

class authForm(FlaskForm):
    uname=StringField("Username",validators=[DataRequired(),Length(min=5, max=20, message="min 5 and max 20")])
    email = EmailField('Email address', validators=[DataRequired(),Email()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")


