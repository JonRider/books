CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    rating INT NOT NULL,
    review VARCHAR NOT NULL,
    books_id INTEGER REFERENCES books,
    user_id INTEGER REFERENCES users
);
