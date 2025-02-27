# Import necessary libraries for the app
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import session

# Initialize the Flask app and configure the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'

# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    ratings = db.relationship('Rating', backref='book', lazy=True)

    # Function to calculate the average rating of a book
    def average_rating(self):
        if not self.ratings:
            return None
        total = sum(rating.rating for rating in self.ratings)
        return round(total / len(self.ratings), 2)

# Rating Model
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1 to 5

    # Ensure each user can rate a book only once
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_rating'),)

# Create the database tables
with app.app_context():
    db.create_all()

# Routes
# Home page route, displaying featured books (2 books)
@app.route('/')
def home():
    featured_books = Book.query.limit(2).all()  # Get only 2 books
    return render_template('home.html', featured_books=featured_books)

# Login route for user authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first() # Find user by email
        if user and check_password_hash(user.password, password): # Find user by email
            session['user_id'] = user.id # Find user by email
            session['role'] = user.role # Store user role in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

# Register route for new user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate form data
        if not all([username, email, password, confirm_password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # Check if the email or username already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Email or username already exists!', 'error')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Logout route for ending the user's session
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Route to add a new book (only accessible by admin users)
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    # Check if the user is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        price = float(request.form.get('price', 0.0))  # Get the price

        # Validate form data
        if not all([title, author]):
            flash('Title and Author are required!', 'error')
            return redirect(url_for('add_book'))

        # Create a new book and save it in the database
        new_book = Book(
            title=title,
            author=author,
            description=description,
            image_url=image_url,
            price=price
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_book.html')

# Route to delete a book (only accessible by admin users)
@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    # Check if the user is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('You do not have permission to perform this action.', 'error')
        return redirect(url_for('home'))

    # Find the book by ID
    book = Book.query.get_or_404(book_id)

    # Delete the book
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('home'))

# Route to display all books, with optional search functionality
@app.route('/all_books')
def all_books():
    search_query = request.args.get('search', '').strip()  # Get the search query
    if search_query:
        # Filter books by title (case-insensitive)
        books = Book.query.filter(Book.title.ilike(f'%{search_query}%')).all()
    else:
        # Show all books if no search query
        books = Book.query.all()
    return render_template('all_books.html', books=books, search_query=search_query)

# Route for users to rate a book
@app.route('/rate_book/<int:book_id>', methods=['POST'])
def rate_book(book_id):
    if 'user_id' not in session:
        flash('You must be logged in to rate books.', 'error')
        return redirect(url_for('login'))

    rating = int(request.form.get('rating'))
    if rating < 1 or rating > 5:
        flash('Invalid rating. Please choose a rating between 1 and 5.', 'error')
        return redirect(url_for('all_books'))

    # Check if the user has already rated this book
    existing_rating = Rating.query.filter_by(user_id=session['user_id'], book_id=book_id).first()
    if existing_rating:
        existing_rating.rating = rating  # Update the existing rating
    else:
        # Create a new rating
        new_rating = Rating(user_id=session['user_id'], book_id=book_id, rating=rating)
        db.session.add(new_rating)
    db.session.commit()
    flash('Thank you for your rating!', 'success')
    return redirect(url_for('all_books'))

# Route to update the price of a book (only accessible by admin users)
@app.route('/update_price/<int:book_id>', methods=['POST'])
def update_price(book_id):
    # Check if the user is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('You do not have permission to perform this action.', 'error')
        return redirect(url_for('home'))

    # Find the book by ID
    book = Book.query.get_or_404(book_id)

    # Update the price
    new_price = float(request.form.get('price', 0.0))
    book.price = new_price
    db.session.commit()
    flash(f'Price updated to ${new_price:.2f}!', 'success')
    return redirect(url_for('all_books'))

# Route to display details of a specific book
@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

# Route to display the shopping cart
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])  # Get the cart from the session
    books = []
    total_price = 0.0
    for book_id in cart_items: # Loop through cart items and get book details
        book = Book.query.get(book_id)
        if book:
            books.append(book)
            total_price += book.price # Calculate the total price of books in the cart
    return render_template('cart.html', books=books, total_price=total_price)

# Route to add a book to the cart
@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    if 'cart' not in session:  # If no cart exists, create one
        session['cart'] = []
    session['cart'].append(book_id) # Add the book to the cart
    session.modified = True # Mark session as modified
    flash('Book added to cart!', 'success')
    return redirect(url_for('book_details', book_id=book_id))

# Route to submit the order (empty the cart)
@app.route('/submit_order', methods=['POST'])
def submit_order():
    session.pop('cart', None) # Remove cart from session
    flash('Your order has been submitted!', 'success')
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)