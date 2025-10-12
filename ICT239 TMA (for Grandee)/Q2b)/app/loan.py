from app import db
from datetime import datetime

class Loan(db.Document):
    """
    Loan document representing a book loan by a user.
    Each loan is a standalone document in the 'loans' collection.
    """
    member = db.ReferenceField('User', required=True)
    book = db.ReferenceField('Book', required=True)
    borrowDate = db.DateTimeField(required=True, default=datetime.now)
    returnDate = db.DateTimeField()
    renewCount = db.IntField(default=0)
    
    meta = {
        'collection': 'loans',
        'indexes': [
            'member',
            'book',
            ('member', 'book')  # Compound index for efficient queries
        ]
    }
    
    # ==================== CREATE METHOD ====================
    @staticmethod
    def create_loan(user, book, borrow_date=None):
        """
        Create a Loan document for a user.
        A Loan document can be created only if the user does not already have 
        an unreturned loan for the same book title.
        
        Args:
            user: User object (or user_id string)
            book: Book object (or book_id string)
            borrow_date: Date of borrowing (defaults to now)
            
        Returns:
            tuple: (success: bool, message: str, loan: Loan or None)
        """
        # Handle string IDs or objects
        if isinstance(user, str):
            from model import User
            user = User.get_user_by_id(user)
        if isinstance(book, str):
            from model import Book
            book = Book.get_book_by_id(book)
        
        # Validate inputs
        if not user:
            return False, "Invalid user.", None
        if not book:
            return False, "Book not found.", None
        
        # Check if user already has an unreturned loan for this book title
        existing_loan = Loan.objects(
            member=user,
            book=book,
            returnDate=None  # returnDate is None means unreturned
        ).first()
        
        if existing_loan:
            return False, f"You already have an unreturned loan for '{book.title}'.", None
        
        # Check if book has available copies
        if not book.available or book.available <= 0:
            return False, f"No available copies of '{book.title}'.", None
        
        # Create the loan
        try:
            loan = Loan(
                member=user,
                book=book,
                borrowDate=borrow_date or datetime.now(),
                renewCount=0
            )
            loan.save()
            
            # Update book's available count
            book.available -= 1
            book.save()
            
            return True, f"Successfully borrowed '{book.title}'.", loan
            
        except Exception as e:
            return False, f"Error creating loan: {str(e)}", None
    
    # ==================== RETRIEVE METHODS ====================
    @staticmethod
    def get_all_loans_by_user(user):
        """
        Retrieve all loans for a specific user.
        
        Args:
            user: User object or user_id string
            
        Returns:
            list: List of Loan documents
        """
        if isinstance(user, str):
            from model import User
            user = User.get_user_by_id(user)
        
        if not user:
            return []
        
        return Loan.objects(member=user).order_by('-borrowDate')
    
    @staticmethod
    def get_active_loans_by_user(user):
        """
        Retrieve all unreturned loans for a specific user.
        
        Args:
            user: User object or user_id string
            
        Returns:
            list: List of active Loan documents
        """
        if isinstance(user, str):
            from model import User
            user = User.get_user_by_id(user)
        
        if not user:
            return []
        
        return Loan.objects(member=user, returnDate=None).order_by('-borrowDate')
    
    @staticmethod
    def get_loan_by_id(loan_id):
        """
        Retrieve a specific loan by its ID.
        
        Args:
            loan_id: ID of the loan
            
        Returns:
            Loan: Loan document or None
        """
        try:
            return Loan.objects(id=loan_id).first()
        except:
            return None
    
    @staticmethod
    def get_loans_by_book(book):
        """
        Retrieve all loans for a specific book.
        
        Args:
            book: Book object or book_id string
            
        Returns:
            list: List of Loan documents
        """
        if isinstance(book, str):
            from model import Book
            book = Book.get_book_by_id(book)
        
        if not book:
            return []
        
        return Loan.objects(book=book).order_by('-borrowDate')
    
    @staticmethod
    def get_active_loans_by_book(book):
        """
        Retrieve all unreturned loans for a specific book.
        
        Args:
            book: Book object or book_id string
            
        Returns:
            list: List of active Loan documents
        """
        if isinstance(book, str):
            from model import Book
            book = Book.get_book_by_id(book)
        
        if not book:
            return []
        
        return Loan.objects(book=book, returnDate=None).order_by('-borrowDate')
    
    # ==================== UPDATE METHODS ====================
    def renew_loan(self):
        """
        Renew the loan by updating the renew count and the borrow date.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if loan has already been returned
        if self.returnDate is not None:
            return False, "Cannot renew a returned loan."
        
        try:
            # Update renew count and borrow date
            self.renewCount += 1
            self.borrowDate = datetime.now()
            self.save()
            
            return True, f"Loan for '{self.book.title}' renewed successfully. Renew count: {self.renewCount}"
            
        except Exception as e:
            return False, f"Error renewing loan: {str(e)}"
    
    def return_loan(self):
        """
        Return the loan by updating the return date.
        The available count for the book is also updated.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if loan has already been returned
        if self.returnDate is not None:
            return False, "This loan has already been returned."
        
        try:
            # Update loan record with return date
            self.returnDate = datetime.now()
            self.save()
            
            # Update book's available count
            self.book.available += 1
            self.book.save()
            
            return True, f"Book '{self.book.title}' returned successfully."
            
        except Exception as e:
            return False, f"Error returning loan: {str(e)}"
    
    # ==================== DELETE METHOD ====================
    @staticmethod
    def delete_loan(loan_id):
        """
        Delete a loan document.
        Only loans that have been returned can be deleted.
        
        Args:
            loan_id: ID of the loan to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        loan = Loan.get_loan_by_id(loan_id)
        
        if not loan:
            return False, "Loan not found."
        
        # Check if loan has been returned
        if loan.returnDate is None:
            return False, "Cannot delete an unreturned loan. Please return the loan first."
        
        try:
            loan.delete()
            return True, "Loan record deleted successfully."
        except Exception as e:
            return False, f"Error deleting loan: {str(e)}"
    
    def delete(self):
        """
        Override delete method to ensure only returned loans can be deleted.
        """
        if self.returnDate is None:
            raise Exception("Cannot delete an unreturned loan. Please return the loan first.")
        super(Loan, self).delete()
    
    # ==================== HELPER METHODS ====================
    def is_returned(self):
        """
        Check if the loan has been returned.
        
        Returns:
            bool: True if returned, False otherwise
        """
        return self.returnDate is not None
    
    def is_overdue(self, max_loan_days=14):
        """
        Check if the loan is overdue.
        
        Args:
            max_loan_days: Maximum number of days allowed for a loan (default: 14)
            
        Returns:
            bool: True if overdue, False otherwise
        """
        if self.is_returned():
            return False
        
        days_borrowed = (datetime.now() - self.borrowDate).days
        return days_borrowed > max_loan_days
    
    def days_borrowed(self):
        """
        Calculate the number of days the book has been borrowed.
        
        Returns:
            int: Number of days
        """
        if self.is_returned():
            return (self.returnDate - self.borrowDate).days
        else:
            return (datetime.now() - self.borrowDate).days
    
    def can_renew(self, max_renewals=2):
        """
        Check if the loan can be renewed.
        
        Args:
            max_renewals: Maximum number of renewals allowed (default: 2)
            
        Returns:
            tuple: (can_renew: bool, message: str)
        """
        if self.is_returned():
            return False, "Cannot renew a returned loan."
        
        if self.renewCount >= max_renewals:
            return False, f"Maximum renewal limit ({max_renewals}) reached."
        
        if self.is_overdue():
            return False, "Cannot renew an overdue loan."
        
        return True, "Loan can be renewed."
    
    def to_dict(self):
        """
        Convert loan to dictionary format for API responses.
        
        Returns:
            dict: Loan data as dictionary
        """
        return {
            'id': str(self.id),
            'member': {
                'id': str(self.member.id),
                'name': self.member.name,
                'email': self.member.email
            },
            'book': {
                'id': str(self.book.id),
                'title': self.book.title
            },
            'borrowDate': self.borrowDate.isoformat() if self.borrowDate else None,
            'returnDate': self.returnDate.isoformat() if self.returnDate else None,
            'renewCount': self.renewCount,
            'is_returned': self.is_returned(),
            'days_borrowed': self.days_borrowed(),
            'is_overdue': self.is_overdue()
        }
    
    def __repr__(self):
        status = "Returned" if self.is_returned() else "Active"
        return f"<Loan {self.id}: '{self.book.title}' by {self.member.name} - {status}>"