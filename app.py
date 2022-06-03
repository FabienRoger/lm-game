import flask
from flask import Flask, send_file, request, jsonify
import json
import random
import ast
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Connection
from dataclasses import dataclass
import datetime


app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
        "postgres://", "postgresql://"
    )
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or "DEVELOPMENT SECRET KEY"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # get rid of warning

db: SQLAlchemy = SQLAlchemy(app)
session = db.session


def get_database_connection() -> Connection:
    return session.connection()


tokens = ast.literal_eval(open("./tokens.json").read())
docs = json.load(open("./docs.json"))


@app.route("/tokens")
def get_tokens():
    return jsonify(tokens)


@app.route("/get_doc")
def get_doc():
    doc_choice_num = random.randint(0, len(docs) - 1)

    return jsonify({"docId": doc_choice_num, "tokens": docs[doc_choice_num]})


@dataclass
class LmGameGuess(db.Model):
    __tablename__ = "lm_game_guesses"
    id: int
    id = db.Column(db.Integer, primary_key=True)

    username: str
    username = db.Column(db.String, nullable=False)

    guess: str
    guess = db.Column(db.String, nullable=False)

    correct_answer: str
    correct_answer = db.Column(db.String, nullable=False)

    guessed_token_idx: int
    guessed_token_idx = db.Column(db.Integer, nullable=False)

    doc_id: int
    doc_id = db.Column(db.Integer, nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


@app.route("/submit_guess", methods=["POST"])
def submit_guess():
    stuff = request.get_json()
    db.session.add(LmGameGuess(**stuff))
    db.session.commit()

    return "whatever"