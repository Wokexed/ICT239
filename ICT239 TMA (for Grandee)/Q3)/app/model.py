from app import db, login_manager
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

class Book(db.Document):
    title = db.StringField(required=True)
    authors = db.ListField(db.StringField())
    genres = db.ListField(db.StringField())
    category = db.StringField()
    pages = db.IntField()
    url = db.StringField()
    description = db.ListField(db.StringField())
    available = db.IntField()
    copies = db.IntField()

    meta = {'collection': 'books'}

    @staticmethod
    def get_book_by_id(book_id):
        return Book.objects(id=book_id).first()
    
    @staticmethod
    def delete_book_by_id(book_id):
        book = Book.get_book_by_id(book_id)
        if book:
            book.delete()
            return True
        return False
    
    @staticmethod
    def update_book(book_id, data):
        book = Book.get_book_by_id(book_id)
        if book:
            for key, value in data.items():
                setattr(book, key, value)
            book.save()
            return True
        return False    
    
    @staticmethod
    def add_book(data):
        book = Book(**data)
        book.save()
        return book

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Register')

class User(db.Document, UserMixin):
    name = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    is_admin = db.BooleanField(default=False)

    meta = {'collection': 'users'}

    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get_user_by_email(email):
        return User.objects(email=email).first()
    
    @staticmethod
    def create_user(name, email, password, is_admin=False):
        try:
            print(f"🔍 Attempting to create user: {name}, {email}")
            hashed_pw = generate_password_hash(password)
            print(f"🔍 Password hashed successfully")
            
            user = User(name=name, email=email, password_hash=hashed_pw, is_admin=is_admin)
            print(f"🔍 User object created: {user}")
            
            user.save()
            print(f"✅ User saved successfully: {name} ({email})")
            print(f"✅ User ID: {user.id}")
            
            return user
        except Exception as e:
            print(f"❌ Error creating user: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.objects(id=user_id).first()
    
    @staticmethod
    def check_user_credentials(email, password):
        user = User.get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
    
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)
    