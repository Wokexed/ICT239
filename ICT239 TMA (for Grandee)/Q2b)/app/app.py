from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import app, db
from app.model import Book, User, LoginForm, RegistrationForm, Author
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
        
        # Initialize authors_str for the current book
        authors_str = 'Unknown Author' 

        if book.authors:
            # Check 1: If it looks like a list of Author objects (checking the first element)
            if hasattr(book.authors[0], 'name'):
                authors_str = ', '.join([author.name for author in book.authors])
                
            # Check 2: If it looks like a list of simple strings (legacy/fallback)
            elif isinstance(book.authors[0], str):
                authors_str = ', '.join(book.authors)
                
            # Check 3: Final attempt for complex objects that might use a different attribute or need str() conversion
            else:
                try:
                    # Try to extract the name attribute if it's an object with a .name field
                    author_names = [author.name for author in book.authors]
                except AttributeError:
                    # If .name fails, convert the object to a string as a last resort
                    author_names = [str(author) for author in book.authors]
                    
                authors_str = ', '.join(author_names)
        
        # The authors_str variable is now finalized and scoped to the current book iteration.
        books_list.append({
            'id': str(book.id),
            'title': book.title,
            'author': authors_str, # Use the correctly determined string
            'genre': ', '.join(book.genres) if book.genres else 'Unknown',
            'category': book.category or 'Adult',
            'pages': book.pages or 0,
            'cover_image': book.url or '',
            'description': '\n\n'.join(book.description) if book.description else '',
            'copies_available': book.available or 0,
            'total_copies': book.copies or 1
        })
    return render_template('index.html', books=books_list)

# @app.route("/")
# def index():
#     books_list = []
#     for book in Book.objects.order_by('title'):
#         books_list.append({
#             'id': str(book.id),
#             'title': book.title,
#             'author': ', '.join(book.authors) if book.authors else 'Unknown Author',
#             'genre': ', '.join(book.genres) if book.genres else 'Unknown',
#             'category': book.category or 'Adult',
#             'pages': book.pages or 0,
#             'cover_image': book.url or '',
#             'description': '\n\n'.join(book.description) if book.description else '',
#             'copies_available': book.available or 1,
#             'total_copies': book.copies or 1
#         })
#     return render_template('index.html', books=books_list)


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
# @app.route('/book/<book_id>')
# def book_details(book_id):
#     """Display detailed information about a specific book"""
#     from bson.objectid import ObjectId

#     try:
#         book = Book.objects.get(id=ObjectId(book_id))
#         book_data = {
#             'id': str(book.id),
#             'title': book.title,
#             'author': ', '.join(book.authors) if book.authors else 'Unknown Author',
#             'genre': ', '.join(book.genres) if book.genres else 'Unknown',
#             'category': book.category or 'Adult',
#             'pages': book.pages or 0,
#             'cover_image': book.url or '',
#             'description': '\n\n'.join(book.description) if book.description else '',
#             'copies_available': book.available or 1,
#             'total_copies': book.copies or 1
#         }
#         return render_template('book_details.html', book=book_data)
#     except Exception:
#         flash('Book not found.', 'danger')
#         return redirect(url_for('index'))

@app.route('/book/<book_id>')
def book_details(book_id):
    """Display detailed information about a specific book"""
    from bson.objectid import ObjectId

    try:
        book = Book.objects.get(id=ObjectId(book_id))
        
        # --- FIX FOR AUTHOR OBJECTS ---
        authors_str = 'Unknown Author'
        if book.authors:
            # Check if it contains objects and extract the .name attribute (assuming Author model has .name)
            if hasattr(book.authors[0], 'name'):
                authors_str = ', '.join([author.name for author in book.authors])
            # Fallback for simple string lists or if .name fails
            else:
                authors_str = ', '.join([str(author) for author in book.authors])
        # -----------------------------
        
        book_data = {
            'id': str(book.id),
            'title': book.title,
            'author': authors_str, # Use the correctly formatted string
            'genre': ', '.join(book.genres) if book.genres else 'Unknown',
            'category': book.category or 'Adult',
            'pages': book.pages or 0,
            'cover_image': book.url or '',
            'description': '\n\n'.join(book.description) if book.description else '',
            'copies_available': book.available or 0,
            'total_copies': book.copies or 1
        }
        return render_template('book_details.html', book=book_data)
    except Exception:
        # It's safer to catch a more specific exception like DoesNotExist or InvalidId
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
        # Get form data for re-rendering
        form_data = {
            'genres': request.form.getlist('genres'),
            'title': request.form.get('title', ''),
            'category': request.form.get('category', ''),
            'cover_url': request.form.get('cover_url', ''),
            'description': request.form.get('description', ''),
            'author_names': request.form.getlist('author_name'),
            'author_illustrators': request.form.getlist('author_illustrator'),
            'num_pages': request.form.get('num_pages', ''),
            'num_copies': request.form.get('num_copies', '')
        }
        
        # Handle adding an author row
        if request.form.get('add_author'):
            form_data['author_names'].append('')
            return render_template('new_book.html', form_data=form_data)
        
        # Handle removing an author row
        if request.form.get('remove_author'):
            remove_index = int(request.form.get('remove_author'))
            # Remove the author at the specified index
            if remove_index < len(form_data['author_names']):
                form_data['author_names'].pop(remove_index)
                # Also remove from illustrators list if present
                form_data['author_illustrators'] = [
                    idx for idx in form_data['author_illustrators']
                    if int(idx) != remove_index
                ]
            return render_template('new_book.html', form_data=form_data)
        
        # Handle book submission
        if request.form.get('submit_book'):
            genres = form_data['genres']
            title = form_data['title']
            category = form_data['category']
            cover_url = form_data['cover_url']
            description = form_data['description']
            author_names = form_data['author_names']
            author_illustrators = form_data['author_illustrators']
            num_pages = form_data['num_pages']
            num_copies = form_data['num_copies']
            
            # Validate required fields
            if not title or not category:
                flash('Title and category are required.', 'danger')
                return render_template('new_book.html', form_data=form_data)
            
            if not any(author_names):  # Check if at least one author name exists
                flash('At least one author is required.', 'danger')
                return render_template('new_book.html', form_data=form_data)
            
            try:
                # Create author objects
                authors_list = []
                for i, author_name in enumerate(author_names):
                    if author_name.strip():  # Only add non-empty authors
                        is_illustrator = str(i) in author_illustrators
                        author = Author(name=author_name.strip(), is_illustrator=is_illustrator)
                        authors_list.append(author)
                
                # Convert description to list
                description_list = [description] if description else []
                
                # Create book in database
                book = Book(
                    title=title,
                    category=category,
                    description=description_list,
                    url=cover_url,
                    pages=int(num_pages) if num_pages else None,
                    copies=int(num_copies) if num_copies else 1,
                    available=int(num_copies) if num_copies else 1,
                    authors=authors_list,
                    genres=genres
                )
                
                book.save()
                
                flash(f'Book "{title}" added successfully!', 'success')
                # Redirect to books list or stay on add page
                return redirect(url_for('add_book'))
                
            except Exception as e:
                print(f"Error adding book: {str(e)}")
                import traceback
                traceback.print_exc()
                flash(f'Error adding book: {str(e)}', 'danger')
                return render_template('new_book.html', form_data=form_data)
    
    # Initial load - start with empty form_data
    return render_template('new_book.html', form_data=None)

# @app.route('/admin')
# @login_required 
# def admin_dashboard():
#     # REPLICATE THE BOOK FETCHING LOGIC FROM YOUR INDEX ROUTE
#     books_list = []
#     for book in Book.objects.order_by('title'):
#         books_list.append({
#             'id': str(book.id),
#             'title': book.title,
#             'author': ', '.join(book.authors) if book.authors else 'Unknown Author',
#             'genre': ', '.join(book.genres) if book.genres else 'Unknown',
#             'category': book.category or 'Adult',
#             'pages': book.pages or 0,
#             'cover_image': book.url or '',
#             'description': '\n\n'.join(book.description) if book.description else '',
#             'copies_available': book.available or 1,
#             'total_copies': book.copies or 1
#         })
        
#     return render_template('index.html', books=books_list)
@app.route('/admin')
@login_required 
def admin_dashboard():
    books_list = []
    for book in Book.objects.order_by('title'):
        
        # --- FIX FOR AUTHOR OBJECTS ---
        authors_str = 'Unknown Author'
        if book.authors:
            # Use a list comprehension to extract the display name attribute from each object.
            # We will try '.name' first, as it's the standard for UserMixin/MongoEngine references.
            try:
                author_names = [author.name for author in book.authors]
            except AttributeError:
                # Fallback if the attribute is something else, like '.author_name' 
                # or if it's already a simple list of strings.
                author_names = [str(author) for author in book.authors]

            # Join the collected names
            authors_str = ', '.join(author_names)
        
        books_list.append({
            'id': str(book.id),
            'title': book.title,
            # Use the correctly formatted string
            'author': authors_str, 
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

@app.route('/book/<book_id>/loan', methods=['GET', 'POST'])
def make_loan(book_id):
    # Your make_loan logic here
    return render_template('make_loan.html', book_id=book_id)

if __name__ == '__main__':
    app.run(debug=True)