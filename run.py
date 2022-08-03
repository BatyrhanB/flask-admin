from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from mimesis import Person, Text

app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'anykey'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

person = Person('ru')
text = Text('ru')


@app.get('/')
def index():
    return render_template('index.html')


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    last_seen = db.Column(db.DateTime)
    user_status = db.Column(db.String(40), nullable=True, default='Лучший пользователь проекта')
    coffees = db.relationship('Coffee', backref='client', lazy=True)
    count = db.Column(db.Integer, default=0)

    # def get_count(self):
    #     count = self.coffees.count()
    #     print(count)
    #     return count

class Coffee(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=False, nullable=False)
    content = db.Column(db.Text(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    


class DashBoardView(AdminIndexView):
    @expose('/')
    def add_data_db(self):
        for i in range(10):
            if not len(User.query.all()) >= 10:
                user = User(username=person.full_name(), email=person.email(), password=person.password())
                db.session.add(user)
                db.session.commit()

                coffee = Coffee(title=text.title(), content=text.text(quantity=5))
                coffee.user_id = user.id
                db.session.add(coffee)

            db.session.commit()
        all_users = User.query.all()
        all_coffees = Coffee.query.all()
        return self.render('admin/dashboard_index.html', all_users=all_users, all_coffees=all_coffees,
                           )


admin = Admin(app, name='Coffee App', template_mode='bootstrap4', index_view=DashBoardView(), endpoint='admin')
admin.add_view(ModelView(User, db.session, name='Пользователь'))
admin.add_view(ModelView(Coffee, db.session, name='Кофе'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)