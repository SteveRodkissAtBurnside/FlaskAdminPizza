from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileRequired
from wtforms import validators, StringField, SubmitField
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzashop.db'
app.config['SECRET_KEY'] = 'sldflsdfkjlksjdflksj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

#create the sql-alchemy table classes
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))

class Pizza(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30))
    image_filename = db.Column(db.String(100))
    def __repr__(self):
        return self.name

class Order(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    order_name = db.Column(db.String(30))
    

#the bridging table
pizza_order = db.Table('pizza_order',
    db.Column('pizza_id',db.Integer,db.ForeignKey('Pizza.id')),
    db.Column('order_id',db.Integer,db.ForeignKey('Order.id')))

#the forms that I will need for data input
#extrnd flaskform so we can use the validators
class PizzaForm(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired()])
    image_file = FileField(validators=[FileRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField('username', validators=[validators.DataRequired()])
    submit = SubmitField("Login")

def pizza_query():
    return Pizza.query

def get_pk(obj):
    return str(obj)

class OrderForm(FlaskForm):
    order_name = StringField('Name', validators=[validators.DataRequired()])
    pizza_select = QuerySelectField(query_factory=pizza_query, get_pk=get_pk)
    submit = SubmitField("Order")
    finished = SubmitField("Finished")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login/', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    loginform = LoginForm()
    if loginform.validate_on_submit():
        #login submitted
        user = User.query.filter_by(username=loginform.username.data).first()
        if user is None:
            return redirect('/')
        #otherwiae we can log in the user
        login_user(user)
        return redirect('/')
    return render_template('login.html', form=loginform)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')
    

@app.route('/')
def home():
    data = Pizza.query.all()
    print(data)
    return render_template('index.html', data=data)


@app.route('/place_order/', methods=['POST','GET'])
def place_order():
    #create the order form
    order_form = OrderForm()
    return render_template('order_form.html', form=order_form)




@app.route('/upload_photo/',methods=['GET','POST'])
def upload_photo():
    form = PizzaForm()
    if form.validate_on_submit():
        # we tried to submit
        f = form.image_file.data        #the data from the file that was submitted
        filename = secure_filename(f.filename)      #make sure it is a secure filename
        f.save('./static/'+filename)                #save the file data
        #and add the data to the database
        new_entry = Pizza(name=form.name.data,image_filename=filename)   #construct a new Pizza object
        db.session.add(new_entry)                                        #and add it to the session and dbase
        db.session.commit()                                              #and commit the changes
        return redirect('/')                                            #redirect to home page
    return render_template('upload_photo.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)


