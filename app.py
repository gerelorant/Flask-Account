from flask import Flask
from flask_account import Account
from flask_sqlalchemy import SQLAlchemy, Model
import sqlalchemy as sa


app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'OhSoSecret',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///app.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})


class BaseModel(Model):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)


db = SQLAlchemy(app, model_class=BaseModel)
account = Account(app, db)


@app.route('/')
def hello_world():
    return 'Hello World!'


db.create_all()

if __name__ == '__main__':
    app.run()
