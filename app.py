from flask import *
from flask_login import login_user,logout_user, UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required
import sqlalchemy as sa

app = Flask(__name__)
def test_connection():
    with app.app_context():
        
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        app.config['SECRET_KEY']='qwertyuiopasdfghjklzxcvbnm'
        db = SQLAlchemy(app)
        login_manager = LoginManager()
        login_manager.init_app(app)
        
        # Check if the database needs to be initialized
        engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = sa.inspect(engine)
        if not inspector.has_table("users"):
            with app.app_context():
                db.drop_all()
                db.create_all()
                app.logger.info('Initialized the database!')
        else:
            app.logger.info('Database already contains the users table.')

        class business(UserMixin,db.Model):
            id = db.Column(db.Integer, primary_key=True)
            email=db.Column(db.String(1000),nullable=False)
            category = db.Column(db.String(120), nullable=False)
            name=db.Column(db.String(120), nullable=False)
            amount = db.Column(db.Integer, nullable=False)
            equity=db.Column(db.Integer, nullable=False)
            description=db.Column(db.String(100000), nullable=False)
            upvotes = db.Column(db.Integer(), default=0)
            
            def upvote(self):
                self.upvotes += 1
                db.session.commit()
            
            def __repr__(self):
                return self.category + self.name + self.id

        class Investor(UserMixin,db.Model):
            id = db.Column(db.Integer, primary_key=True)
            email=db.Column(db.String(1000),nullable=False)
            category=db.Column(db.String(1000),nullable=False)
            def __repr__(self):
                return 'Email:'+self.email + ' Category:'+self.category

        class User(UserMixin,db.Model):
            id = db.Column(db.Integer, primary_key=True)
            email = db.Column(db.String(120), unique=True, nullable=False)
            fname = db.Column(db.String(80), nullable=False)
            lname = db.Column(db.String(120), nullable=False)
            password = db.Column(db.String(80), nullable=False)
            db.relationship('business')
            db.relationship('Investor')
            db.relationship('CoFounder')
            def __repr__(self):
                return '<User %r>' % self.email + self.password
    
        class MENTOR(UserMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            surname=db.Column(db.String(100), nullable=False)
            email = db.Column(db.String(100), unique=True, nullable=False)
            experience = db.Column(db.String(), nullable=False)
            category=db.Column(db.String(100), nullable=False)
            db.relationship('business')
            db.relationship('Investor')
            def __repr__(self):
                return '<MENTOR %r>' % self.email + self.password
            
        class CoFounder(UserMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            surname=db.Column(db.String(100), nullable=False)
            email = db.Column(db.String(100), unique=True, nullable=False)
            experience = db.Column(db.String(), nullable=False)
            category=db.Column(db.String(100), nullable=False)
            db.relationship('business')
            db.relationship('Investor')
            def __repr__(self):
                return '<CoFounder %r>' % self.email + self.password
            
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/about')
        def about():
            return render_template('about.html')


        @app.route('/login', methods=['POST', 'GET'])
        def login():
            if request.method=='POST':
                email=request.form.get('email')
                password=request.form.get('password')
                user =User.query.filter_by(email=email).first()
                if user and password==user.password:
                    login_user(user, remember=True)
                    response = make_response(redirect('/'))
                    response.set_cookie("user", email)
                    flash(f'Welcome to PromoDesk {email}', 'success')
                    return response
                else:
                    flash(f'Invalid Credentials.', 'warning')
                    return redirect('/login')
            return render_template("login.html")

        @app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                email = request.form.get('email')
                password = request.form.get('password')
                fname = request.form.get('first_name')
                lname = request.form.get('last_name')
                user=User(email=email,password=password,fname=fname,lname=lname)
                db.session.add(user)
                db.session.commit()
                flash(f'Welcome to PromoDesk {email}', 'success')
                return redirect('/login')

            return render_template('register.html')

        @app.route('/logout')
        def logout():
            logout_user()
            flash('Logged Out of your Account', 'success')
            response = make_response(redirect('/'))
            response.set_cookie('user', '', expires=0)
            return response

        @app.route('/form')
        def form():
            return render_template('form.html')

        @app.route('/settings')
        def settings():
            return render_template('settings.html')

        @app.route('/delete', methods=['POST','GET'])
        def delete():
            if request.method == 'POST':
                email = request.form.get("email")
                passwordAttempt = request.form.get("password")
                user =User.query.filter_by(email=email).first()
                password = user.password
                if passwordAttempt == password:
                    db.session.delete(user)
                    db.session.commit()
                    flash("Account Deleted.", "secondary")
                    response = make_response(redirect('/'))
                    response.set_cookie('user', '', expires=0)
                    return response
                else:
                    flash("Invalid Password", "danger")
                    return redirect("/")
            return render_template("delete.html")

        @app.route('/entrepreneur',methods=['POST', 'GET'])
        def entrepreneur():
            if request.method == 'POST':
                category = request.form.get("category")
                name = request.form.get("name")
                amount = request.form.get("amount")
                equity = request.form.get("equity")
                description=request.form.get("describe")
                user_cookies = request.cookies.get('user')
                bUsiness=business(email=user_cookies,category=category, name=name,amount=amount,equity=equity,description=description)
                db.session.add(bUsiness)
                db.session.commit()
                flash("Succcesfully saved your details. You can now check if there is an investor avaialable for you.", "success")
                return redirect('/')
                
            return render_template('entrepreneur.html')

        @app.route('/investor', methods=['POST','GET'])
        def investorpage():
            if request.method=="POST":
                category=request.form.get("category")
                user_cookies = request.cookies.get('user')
                investor=Investor(email=user_cookies,category=category)
                db.session.add(investor)
                db.session.commit()
                flash("Successfully added", category="success")
                return redirect("/")
            return render_template("investor.html")

        @app.route("/investorsready", methods=['GET', 'POST'])
        def investorready():
            user_cookies = request.cookies.get('user')
            investor =Investor.query.filter_by(email=user_cookies).first()
            category=investor.category
            businesses = business.query.filter_by(category=category).all()
            return render_template("investorsready.html", data=businesses)
        @app.route('/mentor', methods=['GET','POST'])
        def mentor():
            if request.method=='POST':
                firstname=request.form.get("name")
                surname=request.form.get("surname")
                category=request.form.get("category")
                experience=request.form.get("Experience")
                user_cookies = request.cookies.get('user')
                Mentor=MENTOR(email=user_cookies,name=firstname,surname=surname,experience=experience,category=category)
                db.session.add(Mentor)
                db.session.commit()
                flash(f'Succesfully registered.', 'success')
                return redirect('/')
            return render_template("mentor.html")
        
        @app.route('/mentorready', methods=['GET', 'POST'])
        def mentorready():
            user_cookies = request.cookies.get('user')
            businessesss =business.query.filter_by(email=user_cookies).first()
            category=businessesss.category
            mentors = MENTOR.query.filter_by(category=category)
            return render_template("mentorready.html", data=mentors)
    
        @app.route('/cofounder', methods=['GET','POST'])
        def cofounder():
            if request.method=='POST':
                firstname=request.form.get("name")
                surname=request.form.get("surname")
                category=request.form.get("category")
                experience=request.form.get("Experience")
                user_cookies = request.cookies.get('user')
                coFounder=CoFounder(email=user_cookies,name=firstname,surname=surname,experience=experience,category=category)
                db.session.add(coFounder)
                db.session.commit()
                flash(f'Succesfully registered.', 'success')
                return redirect('/')
            return render_template("cofounder.html")
        @app.route('/cofounderready', methods=['GET', 'POST'])
        def cofounderready():
            user_cookies = request.cookies.get('user')
            businessesss =business.query.filter_by(email=user_cookies).first()
            category=businessesss.category
            cofounder = CoFounder.query.filter_by(category=category)
            return render_template("cofounderready.html", data=cofounder)
        
        @app.route('/leaderboard', methods=['GET', 'POST'])
        def l_board():
            businesses = business.query.order_by(business.upvotes.desc()).limit(15).all()
            return render_template('leaderboard.html', stu=businesses)

        @app.route('/upvote', methods=['POST','GET'])
        @login_required
        def upvote():
            business_id = request.form.get('business_id')
            business_id = request.form['business_id']
            business_ = business.query.filter_by(id=business_id).first()
            business_.upvote()
            flash('Thanks for UpVoting The Bussiness!', 'success')
            return redirect('/')

        if __name__ == "__main__":
            db.create_all()
            app.run(debug=True)

test_connection()