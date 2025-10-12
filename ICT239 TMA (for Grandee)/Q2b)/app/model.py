from app import db, login_manager
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.loan import Loan

class Author(db.EmbeddedDocument):
    name = db.StringField(required=True)
    is_illustrator = db.BooleanField(default=False)

# class Loan(db.EmbeddedDocument):
#     user_id = db.StringField(required=True)
#     borrowed_date = db.DateTimeField(required=True)
#     returned_date = db.DateTimeField()
#     is_returned = db.BooleanField(default=False)

class Book(db.Document):
    title = db.StringField(required=True)
    authors = db.ListField(db.EmbeddedDocumentField(Author))
    genres = db.ListField(db.StringField())
    category = db.StringField()
    pages = db.IntField()
    url = db.StringField()
    description = db.ListField(db.StringField())
    available = db.IntField()
    copies = db.IntField()
    # loans = db.ListField(db.EmbeddedDocumentField(Loan))

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
    
    def borrow(self):
        if self.available is None or self.available <= 0:
            raise ValueError(f"No copies of '{self.title}' are currently available to borrow.")
        self.available -= 1
        self.save()
        return True

    def return_book(self):
        if self.available is None:
            self.available = 0
        if self.available >= self.copies:
            raise ValueError(f"All copies of '{self.title}' are already in the library. Cannot return more.")
        self.available += 1
        self.save()
        return True
    
    # def borrow_book(self, user_id):
    #     """
    #     Borrow a book for a user.
    #     Returns: (success: bool, message: str)
    #     """
    #     # Sanity check: ensure book has available copies
    #     if not self.available or self.available <= 0:
    #         return False, "No available copies of this book."
        
    #     # Sanity check: ensure user_id is provided
    #     if not user_id:
    #         return False, "Invalid user ID."
        
    #     # Create a new loan record
    #     loan = Loan(
    #         user_id=str(user_id),
    #         borrowed_date=datetime.now(),
    #         is_returned=False
    #     )
        
    #     # Add loan to the loans list
    #     if self.loans is None:
    #         self.loans = []
    #     self.loans.append(loan)
        
    #     # Decrease available count
    #     self.available -= 1
        
    #     # Save the book
    #     self.save()
        
    #     return True, f"Book '{self.title}' borrowed successfully."
    
    # def return_book(self, user_id):
    #     """
    #     Return a book that was borrowed by a user.
    #     Returns: (success: bool, message: str)
    #     """
    #     # Sanity check: ensure user_id is provided
    #     if not user_id:
    #         return False, "Invalid user ID."
        
    #     # Sanity check: ensure loans list exists
    #     if not self.loans:
    #         return False, "This book has no loan records."
        
    #     # Find an unreturned loan for this user
    #     user_loan = None
    #     for loan in self.loans:
    #         if loan.user_id == str(user_id) and not loan.is_returned:
    #             user_loan = loan
    #             break
        
    #     # Sanity check: ensure the book was previously borrowed by this user
    #     if not user_loan:
    #         return False, "This book was not borrowed by this user or has already been returned."
        
    #     # Mark the loan as returned
    #     user_loan.is_returned = True
    #     user_loan.returned_date = datetime.now()
        
    #     # Increase available count
    #     self.available += 1
        
    #     # Save the book
    #     self.save()
        
    #     return True, f"Book '{self.title}' returned successfully."
    
    # def get_active_loans(self):
    #     """Get all active (unreturned) loans for this book."""
    #     if not self.loans:
    #         return []
    #     return [loan for loan in self.loans if not loan.is_returned]
    
    # def get_user_loan_status(self, user_id):
    #     """Check if a user currently has an unreturned copy of this book."""
    #     if not self.loans:
    #         return False
    #     for loan in self.loans:
    #         if loan.user_id == str(user_id) and not loan.is_returned:
    #             return True
    #     return False

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
        print(f"Attempting login for: {email}, User found: {bool(user)}")
        if user and check_password_hash(user.password_hash, password):
            print("Password check passed.") 
            return user
        return None
    
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)