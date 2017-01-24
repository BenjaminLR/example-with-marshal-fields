from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "posts": [post.json() for post in self.posts.all()]
        }


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                               backref=db.backref('posts', lazy='dynamic'))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User',
                             backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, body, category, author, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.category = category
        self.author = author

    def __repr__(self):
        return '<Post %r>' % self.title

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "pub_date": self.pub_date.strftime("%d/%m/%y"),
            "category": self.category.name,
            "author": self.author.username
        }


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "posts": [post.json() for post in self.posts.all()]
        }


class UserList(Resource):
    def get(self):
        users = User.query.all()
        return {"users": [user.json() for user in users]}


class PostList(Resource):
    def get(self):
        posts = Post.query.all()
        return {"posts": [post.json() for post in posts]}


class CategoryList(Resource):
    def get(self):
        categories = Category.query.all()
        return {"categories": [category.json() for category in categories]}


api = Api(app)
api.add_resource(CategoryList, '/categories')
api.add_resource(UserList, '/users')
api.add_resource(PostList, '/posts')

def populate_database():
    db.drop_all()
    db.create_all()
    category1 = Category('Python')
    category2 = Category('Mooc')
    user1 = User('guido', 'guido@example.com')
    user2 = User('john', 'john@example.com')
    post1 = Post('Hi py', 'Python is awesome', category1, user1)
    post2 = Post('Hi py again', 'Python is really awesome', category1, user1)
    post3 = Post('Another one', 'Build wonderful api', category2, user2)
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    db.session.commit()

if __name__ == '__main__':
    populate_database()
    app.run()
