from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import app, db
from app.model import Book, User, LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user

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

# original login route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == "GET":
#         form = LoginForm()
#         return render_template('login.html', form=form)
#     else:
#         username = request.form.get('email')
#         password = request.form.get('password')
#         user = User.check_user_credentials(username, password)
#         if user:
#             login_user(user)
#             flash(f'Welcome back, {username}!', 'success')
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid email or password.', 'danger')
#             form = LoginForm()
#             return render_template('login.html', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("\n--- LOGIN ROUTE ACCESSED ---")
    
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard')) 
        return redirect(url_for('index'))

    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        print(f"Login attempt - Email: {email}, Password: {'*' * len(password)}")

        user = User.check_user_credentials(email, password)
        print(f"User lookup result: {user}")
        
        if user:
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard')) 
            
            return redirect(url_for('index'))
        else:
            # IMPORTANT: Flash error and let form re-render with validation
            flash('Invalid email or password.', 'danger')
            
    # This handles both GET requests AND failed login attempts
    return render_template('login.html', form=form)

@app.route("/logout", methods=['POST']) # Add methods=['POST']
@login_required
def logout():
    # 1. Perform the actual logout action
    logout_user() 
    
    # 2. Flash the message and redirect
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# @app.route('/new_book', methods=['GET', 'POST'])
# @login_required
# def new_book():
#     """Add a new book (admin only)"""
#     if not current_user.is_admin:
#         flash('Admin access required to add new books.', 'danger')
#         return redirect(url_for('index'))
    
#     if request.method == 'POST':
#         title = request.form.get('title')
#         authors = request.form.get('authors', '').split(',')
#         genres = request.form.get('genres', '').split(',')
#         category = request.form.get('category')
#         pages = int(request.form.get('pages', 0))
#         url = request.form.get('url')
#         description = request.form.get('description', '').split('\n\n')
#         copies = int(request.form.get('copies', 1))
#         available = copies  # Initially, all copies are available
        
#         new_book = Book(
#             title=title,
#             authors=[author.strip() for author in authors if author.strip()],
#             genres=[genre.strip() for genre in genres if genre.strip()],
#             category=category,
#             pages=pages,
#             url=url,
#             description=[desc.strip() for desc in description if desc.strip()],
#             copies=copies,
#             available=available
#         )
#         new_book.save()
        
#         flash(f'Book "{title}" added successfully!', 'success')
#         return redirect(url_for('index'))
    
#     return render_template('new_book.html')
@app.route('/new_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        if request.form.get('add_author'):
            # Just re-render with one more author row
            return render_template('new_book.html')
        
        if request.form.get('remove_author'):
            # Just re-render without that author row
            return render_template('new_book.html')
        
        if request.form.get('submit_book'):
            # Process the book submission
            genres = request.form.getlist('genres')
            title = request.form.get('title')
            category = request.form.get('category')
            cover_url = request.form.get('cover_url')
            description = request.form.get('description')
            author_names = request.form.getlist('author_name')
            author_illustrators = request.form.getlist('author_illustrator')
            num_pages = request.form.get('num_pages')
            num_copies = request.form.get('num_copies')
            
            # Validate required fields
            if not title or not category or not author_names or not author_names[0]:
                flash('Please fill in all required fields.', 'danger')
                return render_template('new_book.html')
            
            try:
                # Create book in database
                book = Book(title=title, category=category, description=description,
                           cover_url=cover_url, num_pages=num_pages, num_copies=num_copies)
                
                # Add genres
                for genre in genres:
                    # Add genre to book (depends on your DB structure)
                    pass
                
                # Add authors
                for i, author_name in enumerate(author_names):
                    if author_name:  # Only add non-empty authors
                        is_illustrator = str(i) in author_illustrators
                        # Create author relationship (depends on your DB structure)
                        pass
                
                db.session.add(book)
                db.session.commit()
                
                flash(f'Book "{title}" added successfully!', 'success')
                return redirect(url_for('new_book'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding book: {str(e)}', 'danger')
    
    return render_template('new_book.html')

@app.route('/admin/dashboard')
@login_required 
def admin_dashboard():
    # REPLICATE THE BOOK FETCHING LOGIC FROM YOUR INDEX ROUTE
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