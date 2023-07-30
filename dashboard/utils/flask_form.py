from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, validators
from wtforms.validators import DataRequired

class InfoForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=(validators.DataRequired(),), render_kw={'class': 'datepicker'})
    submit = SubmitField('Submit')
