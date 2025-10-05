from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf import FlaskForm
from flask_login import UserMixin
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

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

class User(db.Document, UserMixin):
    meta = {'collection': 'users'} 
    username = db.StringField(required=True, unique=True, max_length=20)
    email = db.StringField(required=True, unique=True, max_length=120)
    password_hash = db.StringField(required=True)

    @staticmethod
    def find_by_username(username):
        return User.objects(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        return User.objects(email=email).first()
    
    @staticmethod
    def create_user(username, email, password_hash):
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        user.save()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.objects(id=user_id).first()
    
    @staticmethod
    def check_user_credentials(username, password_hash):
        user = User.find_by_username(username)
        if user and user.password_hash == password_hash:
            return user
        return None
    
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)

def __repr__(self):
    return f"<User {self.username}>"
