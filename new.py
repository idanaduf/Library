from flask import request, Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Library.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('index.html')

#------Classes------

#------class books
class Books(db.Model):
    id = db.Column('BookID', db.Integer, primary_key = True)
    book_name = db.Column('BookName', db.String(100))
    book_author = db.Column('BookAuthor', db.String(50))
    published = db.Column('PublishedDate', db.String(10))
    book_type = db.Column('BookType', db.Integer)
    loanlink = db.relationship("Loans", backref = "books")

    def __init__(self, book_name, book_author, published, book_type):
        self.book_name = book_name
        self.book_author = book_author
        self.published = published
        self.book_type = book_type        

 #------class coustomers
class Customers(db.Model):
    id = db.Column('customerID', db.Integer, primary_key = True)
    customer_name = db.Column('customerName', db.String(50))
    customer_age = db.Column('customerAge', db.Integer)
    customer_city = db.Column('customerCity', db.String(25))
    loanlink = db.relationship("Loans", backref = "customers")

    def __init__(self, customer_name, customer_age, customer_city):
        self.customer_name = customer_name
        self.customer_age = customer_age
        self.customer_city = customer_city

#------class loans
class Loans(db.Model):
    id = db.Column('LoanID', db.Integer, primary_key = True)
    customer_id = db.Column('customerID', db.Integer, db.ForeignKey("customers.customerID"))
    book_id = db.Column('BookID', db.Integer, db.ForeignKey("books.BookID"))
    loan_date = db.Column('LoanDate', db.Date)
    return_date = db.Column('ReturnDate', db.Date)
    returned = db.Column('ReturnedOn', db.Boolean)

    def __init__(self, customer_id, book_id, loan_date, return_date):
        self.customer_id = customer_id
        self.book_id = book_id
        self.loan_date = loan_date
        self.return_date = return_date
        self.returned = False 
#######################################################################################################      
########################################## Loans ######################################################
####################################################################################################### 
        
#------all function of loans
@app.route('/Loans/<id>')
@app.route('/Loans/', methods = ['GET', 'POST'])
def all_loans(id = 0):
    if request.method == 'GET':
        if int(id) > 0:
            return render_template('all_loans.html', loans = Loans.query.get(int(id)))
        if int(id) == -1:
            return render_template('all_loans.html', loans = Loans.query.filter_by(returned = True), returned = True)
        return render_template('all_loans.html', loans = Loans.query.filter_by(returned = False))
    if request.method == 'POST': 
        request_data = request.form
        customer_id = request_data ['CustomerID']
        book_id = request_data ['BookID'] 
        loan_date = (datetime.datetime.utcnow())

        book = Books.query.get(book_id)
        if book.book_type == 1: 
            return_date = date.today() + timedelta(days = 10)
        elif book.book_type == 2:
            return_date = date.today() + timedelta(days = 5)
        elif book.book_type == 3: 
            return_date = date.today() + timedelta(days = 2)
        new_loan = Loans(customer_id, book_id, loan_date, return_date)
        db.session.add(new_loan)
        db.session.commit()
        return render_template('all_loans.html', loans = Loans.query.filter_by(returned = False), action = "Loan created")

@app.route('/NewLoans/', methods = ['GET'])
def new_loan_page():
    return render_template('new_loan.html', all_books = Books.query.all(), all_customers = Customers.query.all())

@app.route('/Loans/Return/<id>', methods = ['GET'])
def delete_loan(id): 
    loan = Loans.query.get(id)
    loan.returned = True
    db.session.commit()
    return render_template('all_loans.html', loans = Loans.query.filter_by(returned = False), action = "Book returned.")

@app.route('/Loans/Late/', methods = ['GET'])
def show_late_loans():
    late_loans = []
    active_loans = Loans.query.filter_by(returned= False)
    for loan in active_loans:
            if loan.return_date < datetime.date.today():
                late_loans.append(loan)
    return render_template ("late_loans.html", late_loans = late_loans)
#######################################################################################################      
########################################## customers ##################################################
####################################################################################################### 

#------show all customers
@app.route('/customers', methods=['GET', 'POST'])
@app.route('/customers/<id>')
def show_all_customers(id = -1):
    if request.method == 'GET':
        if int(id) == -1:
            return render_template('all_customers.html', customer = Customers.query.all())
        if int(id) > -1:
            selected = Customers.query.get(int(id))
            return render_template('selected_customer.html', selected = selected)
    if request.method == 'POST':
        data = request.form
        customer_name = data['customer_name']
        customer_age = data['customer_age']
        customer_city = data['customer_city']
        customer = Customers(customer_name=customer_name, customer_age=customer_age, customer_city=customer_city)
        db.session.add(customer)
        db.session.commit()
        return render_template('all_customers.html', customer = Customers.query.all())


@app.route('/new_customer', methods = ['GET'])
def new_customer_page():
    return render_template('add_customer.html')

#------delete customers
@app.route('/deletecustomers/<id>', methods = ['GET'])
def delete_customers(id):
    customer_to_delete = Customers.query.get(id)
    if customer_to_delete:
        db.session.delete(customer_to_delete)
        db.session.commit()
        return "Done."
    else:
        return "customer does not exist."
#------search customer by name
@app.route('/SearchCustomer/', methods = ['POST'])
def search_customer():
    customer_name = request.form ['customer_name']
    all_customers = Customers.query.filter(Customers.customer_name == customer_name).first()
    if all_customers is None:
        return render_template('all_customers.html', all_customers = Customers.query.all(), no_customer = True)
    if Customers is None:
        return redirect('/customers')
    return redirect(f'/customers/{all_customers.id}')


@app.route('/search_cus/<id>', methods = ['GET'])
def search_cus(id):
    customer_to_search = Customers.query.get(id)
    if customer_to_search:
        db.session.search(customer_to_search)
        db.session.commit()
        return "Done."
    else:
        return "customer found."  

#######################################################################################################      
############################################## BOOKS ##################################################
#######################################################################################################

#------show all books
@app.route('/books', methods =['GET', 'POST'] )
@app.route('/books/<id>')
def show_all_books(id = -1):
    if request.method == 'GET':
        if int(id) == -1:
            return render_template('all_books.html', all_books = Books.query.all())
        if int(id) > -1:
            selected_book = Books.query.get(int(id))
            return render_template('selected_book.html',selected_book = selected_book)

#------search book by name  
@app.route('/SearchBooks/', methods = ['POST'])
def search_book():
    book_name = request.form ['book_name']
    all_books = Books.query.filter(Books.book_name == book_name).first()
    if all_books is None:
        return render_template('all_books.html', all_books = Books.query.all(), no_book = True)
    if Books is None:
        return redirect('/books')
    return redirect(f'/books/{all_books.id}')

#------new book    
@app.route('/newbook', methods = ['GET'])
def new_book():
    return render_template('add_book.html')

#------add book
@app.route('/addbooks', methods=['POST'])
def add_book():
    data = request.form
    published = data['published']
    book_name = data['book_name']
    book_author = data['book_author']
    book_type = data['book_type']
    book = Books(published=published, book_name=book_name, book_author=book_author, book_type=book_type)
    db.session.add(book)
    db.session.commit()
    return render_template('all_books.html',all_books=Books.query.all())
@app.route('/deletebook/<id>', methods = ['GET'])
def delete_book(id):
    book_to_delete = Books.query.get(id)
    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
        return render_template('all_books.html', all_books = Books.query.all())
    else:
        return "Book does not exist."     
#################################################################################################################################

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)