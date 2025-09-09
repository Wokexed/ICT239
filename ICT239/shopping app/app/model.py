from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf import FlaskForm
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Item(db.Document):
    meta = {'collection': 'items'}

    item_id = db.IntField(required=True, unique=True)
    item_name = db.StringField(required=True, max_length=100)
    description = db.StringField()
    price = db.FloatField(default="NA")
    inventory_quantity = db.IntField(required=True, min_value=0)

    @staticmethod
    def get_item_by_id(item_id):
        return Item.objects(item_id=item_id).first()

    @staticmethod
    def get_all_items():
        return Item.objects()
    
    @staticmethod
    def save_item(id, name, description, price, quantity):
        item = Item(
            item_id=id,
            item_name=name,
            description=description,
            price=price,
            inventory_quantity=quantity
        )
        item.save()
        return item
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Register')

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(254), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
    
def __repr__(self):
    return f"<User {self.username}>"
