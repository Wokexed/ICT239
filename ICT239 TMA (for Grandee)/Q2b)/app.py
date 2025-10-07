from flask import Flask, render_template, request, redirect, url_for, session, flash
from books import all_books

app = Flask(__name__)
app.secret_key = 'your-secret-key'

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
def get_books_list():
    """Convert books from books.py format to display format"""
    books_list = []
    for idx, book in enumerate(all_books):
        # Join genres
        genre_str = ', '.join(book.get('genres', []))
        
        # Join description paragraphs
        description = '\n\n'.join(book.get('description', []))
        
        # Join authors
        author_str = ', '.join(book.get('authors', ['Unknown Author']))
        
        books_list.append({
            'id': idx + 1,
            'title': book.get('title', 'Unknown'),
            'author': author_str,
            'genre': genre_str,
            'category': book.get('category', 'Adult'),
            'pages': book.get('pages', 0),
            'cover_image': book.get('url', ''),
            'description': description,
            'copies_available': book.get('available', 1),
            'total_copies': book.get('copies', 1)
        })
    
    return books_list

# Routes

@app.route("/")
def index():
    """Home page showing all book titles sorted alphabetically"""
    books = get_books_list()
    books_sorted = sorted(books, key=lambda x: x['title'])
    return render_template('index.html', books=books_sorted)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    """Display detailed information about a specific book"""
    books = get_books_list()
    
    # Find book by id (id is index + 1)
    if 0 < book_id <= len(books):
        book = books[book_id - 1]
        return render_template('book_details.html', book=book)
    else:
        flash('Book not found.', 'danger')
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