# IT S AN IMPORTANT FILE
# I GOT PRACTISE HERE
# YOU R WELCOME
from pathlib import Path


from flask import Flask, render_template, redirect, make_response, session, request
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from data import db_session
from data.news import News
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.loginform1 import LoginForm
from forms.news import NewsForm
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'meawmurkissshshshsh'
UPLOAD_FOLDER = r'C:\Users\gulin\PycharmProjects\LEARNING\HTTP_SKATE\static\img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def main():

    db_session.global_init("db/blogs.db")
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('loginform1.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('loginform1.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")


    @app.route("/")
    def index():
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            news = db_sess.query(News).filter(
                (News.user == current_user) | (News.is_private != True))
        else:
            news = db_sess.query(News).filter(News.is_private != True)
        return render_template("index.html", news=news)

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()

        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                phone=form.phone.data,
                email=form.email.data,
                about=form.about.data
            )
            user.set_password(form.password.data)
            print(form.phone.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)


    @app.route('/news', methods=['GET', 'POST'])
    @login_required
    def add_news():
        form = NewsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = News()
            news.title = form.title.data

            file = request.files['photo']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            news.content = form.content.data
            news.photo = 'img/' + filename


            news.is_private = form.is_private.data
            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('news.html', title='Добавить обЪявление',
                               form=form)

    @app.route('/news/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_news(id):
        form = NewsForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            if news:
                form.title.data = news.title
                form.content.data = news.content
                form.photo.data = news.photo
                form.is_private.data = news.is_private
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            if news:
                news.title = form.title.data
                news.content = form.content.data
                news.is_private = form.is_private.data
                file = request.files['photo']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                news.photo = 'img/' + filename
                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template('news.html',
                               title='Редактирование обЪявления',
                               form=form
                               )

    @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def news_delete(id):
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            db_sess.delete(news)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')

    @app.route('/skate/<int:id>')
    def news_view(id):
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id
                                          ).first()

        return render_template('news_view.html', news=news)

    """@app.route("/cookie_test")
    def cookie_test():
        visits_count = int(request.cookies.get("visits_count", 0))
        if visits_count:
            res = make_response(
                f"Вы пришли на эту страницу {visits_count + 1} раз")
            res.set_cookie("visits_count", str(visits_count + 1),
                           max_age=60 * 60 * 24 * 365 * 2)
        else:
            res = make_response(
                "Вы пришли на эту страницу в первый раз за последние 2 года")
            res.set_cookie("visits_count", '1',
                           max_age=60 * 60 * 24 * 365 * 2)
        return res

    @app.route("/session_test")
    def session_test():
        visits_count = session.get('visits_count', 0)
        session['visits_count'] = visits_count + 1
        return make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")"""

    app.run(debug=True)







if __name__ == '__main__':
    main()