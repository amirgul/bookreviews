import os
import requests
import hashlib
from flask import Flask, session, render_template, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
from questions import *
from datetime import datetime
app = Flask(__name__)
app.secret_key = "whatever secret key"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
engine = create_engine("postgres://ujzioqhvxoferw:dbf64f996020ff2cf325e98bae458fab13e599813ef935afed3df68cb8d9b249@ec2-52-71-55-81.compute-1.amazonaws.com:5432/dctkuqq7oe3aua")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def login():
    if session.get("username") is None:
        return render_template("login.html")
    else:
        return render_template("home.html", personname=session["personname"], username=session["username"])




@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_success", methods=["POST"])
def signup_success():
    #user_username.title()
    #string.lower()
    user_username = request.form.get("username")
    user_personname = request.form.get("personname")
    user_pswd = request.form.get("pswd")
    db_username = db.execute("SELECT id, name FROM users WHERE LOWER(id) = :username",
                            {"username": user_username.lower()}).fetchone()
    if len(user_pswd)<4:
        errormsg=f"Password too short. Make it at least 4 characters long."
        return render_template("signup.html", errormsg=errormsg)
    elif not(db_username is None):
        errormsg = f"Username {db_username[0]} already exist."
        return render_template("signup.html", errormsg=errormsg)
    else:
        user_pswd = "the0ce4nesunav@!n4l0ka"+user_pswd
        user_pswd = hashlib.md5(user_pswd.encode())
        user_pswd = user_pswd.hexdigest()
        db.execute("INSERT INTO users (id, name, password) VALUES (:id, :name, :password)",
                   {"id": user_username.lower(), "name": user_personname, "password": user_pswd})
        db.commit()
        return render_template("signup_success.html", username=user_username, personname=user_personname)

@app.route("/home", methods=["GET", "POST"]) # Change to POST
def home():
    if request.method == "GET":
        return render_template("login.html")
    # On Visiting from the login page:
    if session.get("username") is None:
        user_username = request.form.get("username")
        user_pswd = request.form.get("pswd")
        user_pswd = "the0ce4nesunav@!n4l0ka"+user_pswd
        user_pswd = hashlib.md5(user_pswd.encode())
        user_pswd = user_pswd.hexdigest()
        user_personname = db.execute("SELECT name FROM users WHERE LOWER(id) = :username AND password = :password",
                            {"username": user_username.lower(), "password": user_pswd}).fetchone()
        # Make sure flight user has given valid credentials.
        if user_personname is None:
            return render_template("login.html", errormsg=f"Username or password incorrect for {user_username}")
        else:
            user_personname = user_personname[0]
            session["personname"]=user_personname
            db_user_username = db.execute("SELECT id FROM users WHERE LOWER(id) = :username",
                                {"username": user_username.lower()}).fetchone()
            db_user_username = db_user_username[0]
            session["username"]=db_user_username

    db_top_5 = db.execute("SELECT DISTINCT book_id, AVG(rating) FROM reviews GROUP BY book_id ORDER BY AVG(rating) DESC, book_id limit 5").fetchall()
    top_5_books = []
    for i in db_top_5:
        an_item = []
        book_details = db.execute(f"SELECT * FROM books WHERE id = :id",
                            {"id": i.book_id}).fetchone()
        an_item.append(round(i['avg'], 2))
        an_item.append(book_details['id'])
        an_item.append(book_details['title'])
        an_item.append(book_details['author'])
        an_item.append(book_details['year'])
        top_5_books.append(an_item)
    return render_template("home.html", personname=session["personname"], username=session["username"], top_5_books=top_5_books)

@app.route("/home_book_results", methods=["GET", "POST"]) # Change to POST
def home_book_results():
    if request.method == "GET":
        return render_template("login.html")
    searchby = request.form.get("searchby")
    search_input = request.form.get("search-input")
    searchinput = "%"+search_input+"%"
    query_results = db.execute(f"SELECT * FROM books WHERE LOWER({searchby}) LIKE :searchinput",
                        {"searchinput": searchinput.lower()}).fetchall()
    return render_template("home_book_results.html", personname=session["personname"], username=session["username"], query_results=query_results, searchby=searchby, searchinput=search_input)





@app.route("/home_book_details", methods=["GET", "POST"]) # Change to POST
def home_book_details():
    if request.method == "GET":
        return render_template("login.html")
    book_id = request.form.get("book_id")
    book_title = request.form.get("book_title")
    book_author = request.form.get("book_author")
    book_year = request.form.get("book_year")
    searchby = request.form.get("searchby")
    searchinput = request.form.get("searchinput")
    # Get book data from goodreads.com
    gr_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BjMoDGVJQ03DZxkYG5tzQ", "isbns": book_id})
    gr_data = gr_data.json()
    gr_count = gr_data['books'][0]['work_ratings_count']
    gr_avg   = gr_data['books'][0]['average_rating']
    user_review_id   = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id",
                        {"book_id": book_id, "user_id": session["username"]}).fetchone()
    new_rating = request.form.get("new_rating")
    new_comment= request.form.get("new_comment")
    user_review_comment = ""
    user_review_rating = ""
    if user_review_id:
        user_review_comment= user_review_id['comment']
        user_review_rating = user_review_id['rating']
        user_review_id     = user_review_id['id']
    if new_rating: # We have to insert or update review with new rating/comment
        if user_review_id:  # update
            db.execute("UPDATE reviews SET comment = :comment, rating = :rating  WHERE id = :id",
                        {"comment": new_comment, "rating": new_rating, "id": user_review_id})
            db.commit()

        else:               # insert
            db.execute("INSERT INTO reviews (rating, comment, book_id, user_id) VALUES (:rating, :comment, :book_id, :user_id)",
                       {"rating": new_rating, "comment": new_comment, "book_id": book_id, "user_id": session["username"]})
            db.commit()
    all_reviews = db.execute(f"SELECT * FROM reviews WHERE book_id = :book_id",
                        {"book_id": book_id}).fetchall()
    local_rating_avg = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id",
                        {"book_id": book_id}).fetchone()
    local_rating_avg = local_rating_avg[0]
    if local_rating_avg:
        local_rating_avg = round(local_rating_avg, 2)
    return render_template("home_book_details.html", personname=session["personname"], username=session["username"], book_id=book_id, book_title=book_title, book_author=book_author, book_year=book_year, gr_count=gr_count, gr_avg=gr_avg, searchby=searchby, searchinput=searchinput, user_review_id=user_review_id, user_review_rating=user_review_rating, user_review_comment=user_review_comment, all_reviews=all_reviews, local_rating_avg=local_rating_avg)



@app.route("/home_book_review", methods=["GET", "POST"])
def home_book_review():
    if request.method == "GET":
        return render_template("login.html")
    book_id = request.form.get("book_id")
    book_title = request.form.get("book_title")
    book_author = request.form.get("book_author")
    book_year = request.form.get("book_year")
    gr_count = request.form.get("gr_count")
    gr_avg   = request.form.get("gr_avg")
    searchby = request.form.get("searchby")
    searchinput = request.form.get("searchinput")

    form_user_review_id = request.form.get("user_review_id")
    db_user_review_id = db.execute(f"SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id",
                        {"book_id": book_id, "user_id": session["username"]}).fetchone()
    user_review_id = None
    user_review_comment = ""
    user_review_rating  = ""
    if db_user_review_id:
        user_review_comment= db_user_review_id['comment']
        user_review_rating = db_user_review_id['rating']
        user_review_id     = db_user_review_id['id']
    return render_template("home_book_review.html", personname=session["personname"], username=session["username"], book_id=book_id, book_title=book_title, book_author=book_author, book_year=book_year, gr_count=gr_count, gr_avg=gr_avg, searchby=searchby, searchinput=searchinput, user_review_id=user_review_id, user_review_comment=user_review_comment, user_review_rating=user_review_rating)


@app.route("/api/<string:book_ISBN>")
def api(book_ISBN):
    user_book = db.execute("SELECT * FROM books WHERE id = :id",
                        {"id": book_ISBN}).fetchone()
    if user_book is None:
        return  404

    gr_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BjMoDGVJQ03DZxkYG5tzQ", "isbns": book_ISBN})
    gr_data = gr_data.json()
    gr_count = gr_data['books'][0]['work_ratings_count']
    gr_avg   = gr_data['books'][0]['average_rating']

    return jsonify({
            "title":  user_book['title'],
            "author": user_book['author'] ,
            "year":   user_book['year'],
            "isbn":   user_book['id'],
            "review_count":  gr_count,
            "average_score": gr_avg
        })

@app.route("/cs50aip6b",  methods=["GET", "POST"])
def cs50aip6b():
    if request.method == "GET":
        return render_template("cs50aip6b.html", wiki_answers=None, searchinput=None)
    else:
        searchinput = request.form.get("search-input")
        query, result_ls = process_input(searchinput)
        if result_ls == None:
            return render_template("cs50aip6b.html", wiki_answers=None, searchinput=searchinput)

        files = load_files(result_ls)
        file_words = { filename: tokenize(files[filename]) for filename in files }
        file_idfs = compute_idfs(file_words)
        # Determine top file matches according to TF-IDF
        filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

        # Extract sentences from top files
        sentences = dict()
        for filename in filenames:
            for passage in files[filename].split("\n"):
                for sentence in nltk.sent_tokenize(passage):
                    tokens = tokenize(sentence)
                    if tokens:
                        sentences[sentence] = tokens
        # Compute IDF values across sentences
        idfs = compute_idfs(sentences)

        # Determine top sentence matches
        matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
        wiki_answers = []
        time = datetime.now()
        time = str(time.date())+", "+str(time.hour)+":"+str(time.minute)
        db.execute("INSERT INTO searches (date, searchinput) VALUES (:date, :searchinput)",
                   {"date": time, "searchinput": searchinput})
        db.commit()
        for match in matches:
            wiki_answers.append(match)
        return render_template("cs50aip6b.html", wiki_answers=wiki_answers, searchinput=searchinput)
