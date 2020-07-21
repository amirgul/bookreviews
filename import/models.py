from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


CREATE TABLE books (
      id INTEGER PRIMARY KEY,
      title VARCHAR NOT NULL,
      author VARCHAR NOT NULL,
      year INTEGER NOT NULL);

CREATE TABLE reviews (
      id SERIAL PRIMARY KEY,
      rating INTEGER NOT NULL,
      comment VARCHAR NOT NULL,
      book_id INTEGER REFERENCES books
      user_id INTEGER REFERENCES users
  );
 CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       name VARCHAR NOT NULL,
       username VARCHAR NOT NULL,
       password VARCHAR NOT NULL
   );

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
