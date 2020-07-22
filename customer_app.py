from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy import Column, Integer, String, ForeignKey
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzashop.db'
app.config['SECRET_KEY'] = 'sldflsdfkjlksjdflksj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

#data models

#bridging table
pizza_purchase = db.Table('pizza_purchase',
    db.Column('purchase_id', db.Integer, db.ForeignKey('purchase.id')),
    db.Column('pizza_id', db.Integer, db.ForeignKey('pizza.id'))
)

#the Purchase model- each purchase could be many pizzas and there will be many purchases (so thats why the bridging table is there)
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

#the pizza model
class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    purchases = db.relationship('Purchase', secondary=pizza_purchase , backref='pizzas')

#forms
class PurchaseForm(FlaskForm):
    name = StringField('Order Name:',  validators=[DataRequired()])
    submit_order = SubmitField('Place The Order')


class PizzaForm(FlaskForm):
    add_pizza = SubmitField('Add to Order')

@app.route('/', methods=['GET','POST'])
def home():
    #set the current order to be None
    #set the session variable for the current orde4r to none so we can create one only if we enter the place order route
    session['current_order'] = None
    #display the form for creating a new purchase
    purchase_form = PurchaseForm()
    if purchase_form.validate_on_submit():
        #we clicked to submit an order
        #create the new entry in the purchase database
        new_purchase = Purchase(name=purchase_form.name.data)
        db.session.add(new_purchase)
        db.session.commit()
        session['current_order'] = new_purchase.id
        return redirect(url_for('place_order'))
    return render_template('customer_home.html', form=purchase_form)

@app.route('/place_order', methods=['GET','POST'])
def place_order():
    current_order = Purchase.query.filter_by(id=session['current_order']).first()
    #now set up the ability to add to the purchase
    pizzas = Pizza.query.all()
    form=PizzaForm()
    #this is run after a successful post from customer_home
    #an order has been created and we just want to add pizza's to it!
    return render_template('customer_place_order.html', 
        current_order=current_order, 
        pizzas=pizzas, 
        form=form) 


@app.route('/add_to_order/<int:id>', methods=['GET','POST'])
def add_to_order(id):
    #the pizza form will run this and the form will pass the id of the pizza to add to the order- the current_order is used to check the id of the current order we are processing

    current_order = Purchase.query.filter_by(id=session['current_order']).first()
    if current_order != None:
        #we can add the pizza to the database for this purchase
        pizza = Pizza.query.filter_by(id=id).first()
        current_order.pizzas.append(pizza)
        db.session.commit()
    return redirect(url_for('place_order'))


def populate_pizzas():
    pizzas = ["Pepperoni","Cheese","Cheese and Ham","Bacon double cheesburger","Ham and Pinapple"]
    for p in pizzas:
        pizza = Pizza(name=p)
        db.session.add(pizza)
    db.session.commit()



if __name__ == "__main__":
    #run the app
    answer = input('Rebuild data?: ')
    if answer == "y":
        db.drop_all()
        db.create_all()
        populate_pizzas()
    app.run(debug=True)


