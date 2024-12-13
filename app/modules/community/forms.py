from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from app.modules.community.repositories import CommunityRepository


class CommunityForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=256)])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save community')

    def validate_name(self, name):
        repository = CommunityRepository()
        if not repository.is_name_unique(name.data):
            raise ValidationError('The community name must be unique.')
