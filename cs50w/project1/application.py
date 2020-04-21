import os, requests, json

from flask import Flask, session, render_template, g, request, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

active_login_token = False

app = Flask(__name__)
db = SQLAlchemy()

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['FLASK_APP'] = 'application.py'
app.config['JSON_SORT_KEYS'] = False
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), pool_size=10, max_overflow=20)
db = scoped_session(sessionmaker(bind=engine))

app.debug = 1

# TODO: add function to check and see if the database/table exists. If not it builds it. but if it does it loads it

@app.route("/")
def index():
    try:  
        return render_template('login-register.html')
        
    except Exception as err:
        print(repr(err))
        return render_template('error.html', err = repr(err))
    return render_template('index.html')

@app.route("/login")
def loginregister():
    try:
        return render_template('login-register.html')
    except Exception as err:
        print(repr(err))
        return render_template('error.html', err = repr(err))



@app.route("/book_page/<string:isbn>")
def generate_book_page(isbn):
  # Generate page for single selected book
  try:
    counter = 0
    to_send = {}
    to_send[isbn] = {}
    book_object = db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{isbn}%'").fetchall()
    review_info = requests.get('https://www.goodreads.com/book/review_counts.json', params={'key': '7CXiGcXrotgoPlcPvEFZMw', 'isbns': isbn, 'format': 'json'}).json()
    to_send[isbn]['isbn'] = isbn
    to_send[isbn]['title'] = book_object[0][1]
    to_send[isbn]['author'] = book_object[0][2]
    to_send[isbn]['pub_date'] = book_object[0][3]
    to_send[isbn]['ratings_count'] = review_info['books'][0]['ratings_count']
    to_send[isbn]['average_score'] = review_info['books'][0]['average_rating']
    to_send[isbn]['review_list'] = db.execute(f"SELECT * FROM reviews WHERE isbn = '{isbn}'").fetchall()
    return render_template('bookpage.html', to_send = to_send, isbn = isbn)
    
  except Exception as err:
    print(repr(err))
    return render_template('error.html', err = repr(err))
    

@app.route("/submit_review", methods=['POST'])
def add_review(isbn):
  rating = request.form['rating']
  review = request.form['review_text']
  review_to_add = db.execute('INSERT INTO reviews(%s, %s, %s)', isbn, rating, review)
  print(review_to_add.fetchall())

    

@app.route("/review_data")
def review_data():
        try:
            return 'this is the data review'
        except Exception as err:
            print(repr(err))
            return render_template('error.html', err = repr(err))
    

@app.route('/api/<string:isbn>')
def api_direct(isbn):
    try:
        results = db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{isbn}%'").fetchall()
        review_info = requests.get('https://www.goodreads.com/book/review_counts.json', params={'key': '7CXiGcXrotgoPlcPvEFZMw', 'isbns': isbn, 'format': 'json'}).json()
        to_send = []
        for isbn, title, author, year in results:
            temp = {'isbn': isbn, 'title': title, 'author': author, 'year': year}
            temp['ratings_count'] = review_info['books'][0]['ratings_count']
            temp['average_score'] = review_info['books'][0]['average_rating']
            to_send.append(temp)
        length = len(to_send)
        print(to_send)
        return jsonify(to_send)
    except Exception as err:
        print(err)
        return render_template('api.html', message = repr(err))


@app.route('/error')
def return_error():
    try:
        return render_template('error.html')
    except Exception as err:
        print(repr(err))
    return render_template('error.html', err = repr(err))



@app.route("/search", methods=['POST', 'GET'])
def search():
    search_term = request.form.get('searchBar')
    if search_term == "None":
        search_term = int('0345418263')
    print(f'search term is {search_term}')
  # Generate page for single selected book
    try:
        counter = 0
        to_send = []
        isbn_list = []
        search_results = db.execute("SELECT * FROM books WHERE lower(author) LIKE '%{0}%' OR lower(title) like '%{0}%' OR isbn LIKE '%{0}%'".format(search_term)).fetchall()
        result_num = len(search_results)
        print(result_num)
         
        for x in range(result_num):
            book_object = search_results[x]
            isbn = book_object[0]
            title = book_object[1]
            author = book_object[2]
            date = book_object[3]
            review_info = requests.get('https://www.goodreads.com/book/review_counts.json', params={'key': '7CXiGcXrotgoPlcPvEFZMw', 'isbns': isbn, 'format': 'json'}).json()
            
            temp = {}
            temp['isbn'] = isbn            
            temp['title'] = title
            temp['author'] = author
            temp['pub_date'] = date
            temp['ratings_count'] = review_info['books'][0]['ratings_count']
            temp['average_score'] = review_info['books'][0]['average_rating']
            to_send.append(temp)
            isbn_list.append(isbn)
            
        print('to send = ', to_send)
        print(to_send[1])
        print('isbn list =', isbn_list)
        return render_template('search_results.html', to_send=to_send, isbn_list=isbn_list)
            
        
    except Exception as err:
        print(repr(err))
        return render_template('error.html', err = repr(err))
    


@app.route('/register')
def register():
    #temp_user = db.execute(f'SELECT * FROM users WHERE username = { userName }')
    print('test1')
    

''' ------------------------------------------------------
    TODO: 1.check for cookie
          2a. if cookie is not found assume this to be the first visit and direct to login/register
          2b. if cookie is found check to see if it is valid and if so direct to user landing page

          register
          1. check to see if user exists
          2a. if user does not exist. create user and assign encrypted form of password to that user
              and store as a cookie
          2b. if user does exist check for a history
          3a. if there is no history prep to add an entry in the history and send request for an
              entry from the database


   TODO:
    @route('<path:originalPath>')
    if active_login_token == False:
        redirect(loginPage)
    else:
        redirect(originalPath)


        




   if user_token
   
   if temp_user != None:
        return render_template('index.html', message='it worked')
    return 'try again'
    
    
    
    
    
    
    
    search_target = request.form.get('searchBar')
        if search_target == "None":
            search_target = int('0345418263')
        print(f'search target is {search_target}')
        search_results = db.execute("SELECT * FROM books WHERE lower(author) LIKE '%{0}%' OR lower(title) like '%{0}%' OR isbn LIKE '%{0}%'".format(search_target)).fetchall()
        for result in list(search_results):
            print(result)
        to_send = list(search_results)
        print(to_send)
        return render_template('index.html', to_send=to_send)
    except Exception as err:
        print(repr(err))
        return render_template('error.html', err = repr(err))












    

@app.route('/search', methods=["GET", "POST"])
def search():
    search_target = request.form.get('searchBar')
    if search_target == "None":
        search_target = int('0345418263')
    print(f'search target is {search_target}')

    try:
        counter = 0
        to_send = {}
        book_object = 
        to_send[isbn] = {}
        search_results = db.execute("SELECT * FROM books WHERE lower(author) LIKE '%{0}%' OR lower(title) like '%{0}%' OR isbn LIKE '%{0}%'".format(search_target)).fetchall()
        review_info = requests.get('https://www.goodreads.com/book/review_counts.json', params={'key': '7CXiGcXrotgoPlcPvEFZMw', 'isbns': isbn_list, 'format': 'json'}).json()
        to_send[isbn]['isbn'] = isbn
        to_send[isbn]['title'] = book_object[0][1]
        to_send[isbn]['author'] = book_object[0][2]
        to_send[isbn]['pub_date'] = book_object[0][3]
        to_send[isbn]['ratings_count'] = review_info['books'][0]['ratings_count']
        to_send[isbn]['average_score'] = review_info['books'][0]['average_rating']
        print(to_send)
        return render_template('bookpage.html', to_send = to_send, isbn = isbn)
    
    except Exception as err:
        print(repr(err))
        return render_template('error.html', err = repr(err))
        
        
        
    try: 
        search_target = request.form.get('searchBar')
        if search_target == "None":
            search_target = int('0345418263')
        results = db.execute("SELECT * FROM books WHERE lower(author) LIKE '%{0}%' OR lower(title) like '%{0}%' OR isbn LIKE '%{0}%'".format(search_target)).fetchall()
        to_send = {}
        isbn_list = []
        for isbn, title, author, year in results:
            review_info = requests.get('https://www.goodreads.com/book/review_counts.json', params={'key': '7CXiGcXrotgoPlcPvEFZMw', 'isbns': isbn, 'format': 'json'}).json()
            temp = {}
            temp = {'isbn': isbn, 'title': title, 'author': author, 'year': year}
            temp['ratings_count'] = review_info['books'][0]['ratings_count']
            temp['average_score'] = review_info['books'][0]['average_rating']
            to_send[isbn] = temp
            isbn_list.append(isbn)
        
        print(to_send)
        return render_template('index.html', to_send= json.dumps(to_send), isbn_list=isbn_list)

    except Exception as err:
        print(repr(err))
        return render_template('error.html', err = repr(err))


'''



def create_post(book_object, review_info):

    post = {}
    post['isbn'] = book_object[0]
    post['title'] = book_object[1]
    post['author'] = book_object[2]
    post['year'] = book_object[3]
    post['review_count'] = review_info['books']['ratings_count']
    post['average_score'] = review_info['books']['average_rating']


#goodreads api sample
#{'books': [{'id': 846984, 'isbn': '0375913750', 'isbn13': '9780375913754', 'ratings_count': 35755, 'reviews_count': 60079, 'text_reviews_count': 2853, 'work_ratings_count': 38058, 'work_reviews_count': 64427, 'work_text_reviews_count': 3174, 'average_rating': '3.82'}]}

#db response example
#[('0553803700', 'I, Robot', 'Isaac Asimov', 1950)]