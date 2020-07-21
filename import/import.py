import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ujzioqhvxoferw:dbf64f996020ff2cf325e98bae458fab13e599813ef935afed3df68cb8d9b249@ec2-52-71-55-81.compute-1.amazonaws.com:5432/dctkuqq7oe3aua")
db = scoped_session(sessionmaker(bind=engine))
def main():
    # CREATE TABLES
    db.execute('CREATE TABLE "searches" ('
               'id SERIAL PRIMARY KEY,'
               'date VARCHAR NOT NULL,'
               'searchinput VARCHAR NOT NULL);')

    db.execute('CREATE TABLE "books" ('
               'id VARCHAR PRIMARY KEY,'
               'title VARCHAR NOT NULL,'
               'author VARCHAR NOT NULL,'
               'year INTEGER NOT NULL);')

    db.execute('CREATE TABLE "users" ('
               'id VARCHAR PRIMARY KEY,'
               'name VARCHAR NOT NULL,'
               'password VARCHAR NOT NULL);')

    db.execute('CREATE TABLE "reviews" ('
               'id SERIAL PRIMARY KEY,'
               'rating INTEGER NOT NULL,'
               'comment VARCHAR NOT NULL,'
               'book_id VARCHAR REFERENCES books,'
               'user_id VARCHAR REFERENCES users);')
    db.commit()

    # FILL UP THE TABLE books WITH DATA FROM CSV FILE
    f = open("books.csv")
    reader = csv.reader(f)
    first_row = True
    for isbn, title, author, year in reader:
        if first_row:
            first_row = False
            continue
        db.execute("INSERT INTO books (id, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year":year})
        # print(f"ISBN:{isbn}, YEAR: {year}, Title {title}, Author: {author}.")
    db.commit()


if __name__ == "__main__":
    main()
