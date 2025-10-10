from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import app
from app.model import Book, User, LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user


# Create an admin user account (admin@lib.sg, password 12345, name Admin). 
# Create also a non-admin user account (poh@lib.sg, password 12345, name Peter Oh).
# users = {
#     'admin@lib.sg': {
#         'password': '12345',
#         'is_admin': True
#     },
#     'peter@lib.sg': {
#         'password': '12345',
#         'is_admin': False
#     }
# }

# # Login required decorator
# def login_required(f):
#     def decorated_function(*args, **kwargs):
#         if 'username' not in session:
#             flash('Please log in to access this page.', 'warning')
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# Process books data for display
# def get_books_list():
#     """Convert books from books.py format to display format"""
#     books_list = []
#     for idx, book in enumerate(all_books):
#         # Join genres
#         genre_str = ', '.join(book.get('genres', []))
        
#         # Join description paragraphs
#         description = '\n\n'.join(book.get('description', []))
        
#         # Join authors
#         author_str = ', '.join(book.get('authors', ['Unknown Author']))
        
#         books_list.append({
#             'id': idx + 1,
#             'title': book.get('title', 'Unknown'),
#             'author': author_str,
#             'genre': genre_str,
#             'category': book.get('category', 'Adult'),
#             'pages': book.get('pages', 0),
#             'cover_image': book.get('url', ''),
#             'description': description,
#             'copies_available': book.get('available', 1),
#             'total_copies': book.get('copies', 1)
#         })
    
#     return books_list

# Routes

# @app.route("/")
# def index():
#     for book in all_books:
#         Book.add_book(book)
    
#     return render_template('index.html', books=Book.objects)
        
# @app.route("/")      # IF TS DONT WORK RESTORE THIS
# def index():
#     """Home page showing all book titles sorted alphabetically"""
#     books = Book.objects.order_by('title')
#     books_sorted = sorted(books, key=lambda x: x['title'])
#     return render_template('index.html', books=books_sorted)

@app.route("/")
def index():
    books_list = []
    for book in Book.objects.order_by('title'):
        books_list.append({
            'id': str(book.id),
            'title': book.title,
            'author': ', '.join(book.authors) if book.authors else 'Unknown Author',
            'genre': ', '.join(book.genres) if book.genres else 'Unknown',
            'category': book.category or 'Adult',
            'pages': book.pages or 0,
            'cover_image': book.url or '',
            'description': '\n\n'.join(book.description) if book.description else '',
            'copies_available': book.available or 1,
            'total_copies': book.copies or 1
        })
    return render_template('index.html', books=books_list)

# @app.route('/book/<int:book_id>')
# def book_details(book_id):
#     """Display detailed information about a specific book"""
#     books = Book.objects.order_by('title')
    
#     # Find book by id (id is index + 1)
#     if 0 < book_id <= len(books):
#         book = books[book_id - 1]
#         return render_template('book_details.html', book=book)
#     else:
#         flash('Book not found.', 'danger')
#         return redirect(url_for('index'))
@app.route('/book/<book_id>')
def book_details(book_id):
    """Display detailed information about a specific book"""
    from bson.objectid import ObjectId

    try:
        book = Book.objects.get(id=ObjectId(book_id))
        book_data = {
            'id': str(book.id),
            'title': book.title,
            'author': ', '.join(book.authors) if book.authors else 'Unknown Author',
            'genre': ', '.join(book.genres) if book.genres else 'Unknown',
            'category': book.category or 'Adult',
            'pages': book.pages or 0,
            'cover_image': book.url or '',
            'description': '\n\n'.join(book.description) if book.description else '',
            'copies_available': book.available or 1,
            'total_copies': book.copies or 1
        }
        return render_template('book_details.html', book=book_data)
    except Exception:
        flash('Book not found.', 'danger')
        return redirect(url_for('index'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == "GET":
        return render_template('register.html', form=form)

    print("Form submitted!")

    if form.validate_on_submit():
        print("Form validated!")
        name = form.name.data
        email = form.email.data
        password = form.password.data
        is_admin = form.is_admin.data if hasattr(form, "is_admin") else False

        print(f"📝 Form data - Name: {name}, Email: {email}, Password length: {len(password)}")

        # Check if user already exists
        print(f"🔍 About to check for existing user with email: {email}")
        existing_user = User.get_user_by_email(email)
        print(f"🔍 Existing user result: {existing_user}")
        print(f"🔍 Type of existing_user: {type(existing_user)}")
        
        if existing_user:
            print("⚠️ User already exists! Redirecting...")
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        # ✅ Only create user if email doesn't exist
        print("🚀 About to call User.create_user()...")
        new_user = User.create_user(name, email, password, is_admin)
        print(f"🔍 create_user() returned: {new_user}")

        if new_user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error creating user. Please try again.', 'danger')
            return render_template('register.html', form=form)

    else:
        # Only runs if validation fails
        print("❌ Form validation failed!")
        print("Form errors:", form.errors)
        flash('Error in form submission. Please check your inputs.', 'danger')
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        form = LoginForm()
        return render_template('login.html', form=form)
    else:
        username = request.form.get('email')
        password = request.form.get('password')
        user = User.check_user_credentials(username, password)
        if user:
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            form = LoginForm()
            return render_template('login.html', form=form)

@app.route("/logout", methods=['POST']) # Add methods=['POST']
@login_required
def logout():
    # 1. Perform the actual logout action
    logout_user() 
    
    # 2. Flash the message and redirect
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
    
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """User login page"""
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
        
#         # Check if user exists and password matches
#         if username in users and users[username]['password'] == password:
#             session['username'] = username
#             session['is_admin'] = users[username]['is_admin']
#             flash(f'Welcome back, {username}!', 'success')
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid username or password.', 'danger')
    
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     """Logout user"""
#     session.clear()
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)