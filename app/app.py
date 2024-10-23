from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired, NumberRange
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True, unique=True)
    price = db.Column(db.Integer)
    envimpact = db.Column(db.Integer)
    description = db.Column(db.Text)
    image = db.Column(db.Text)

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)]) #must be at least 1, data has to be entered (cant be blank)
    submit = SubmitField('Submit')

class SortForm(FlaskForm):
    sort_by = SelectField('Sort by', choices=[('name', 'Name'), ('price', 'Price'), ('environment', 'Environmental Impact')])

class CheckoutForm(FlaskForm):
    card_number = StringField('Card Number')
    expiry_date = StringField('Expiry Date')
    cvv = StringField('CVV')
    

# All html routes

@app.route('/', methods=['GET', 'POST'])
def galleryPage():
    form = AddToCartForm()
    sort_form = SortForm()

    if sort_form.validate_on_submit():
        sort_option = sort_form.sort_by.data
    else:
        #default sorting is by name
        sort_option = 'name' 

    #queries by price / name / envimpact and as a result returns the order
    if sort_option == 'price':
        products_query = Product.query.order_by(Product.price).all()
    elif sort_option == 'environment':
        products_query = Product.query.order_by(Product.envimpact).all()
    else:
        products_query = Product.query.order_by(Product.name).all()

    return render_template('index.html',products = products_query, form = form, sort_form = sort_form)


@app.route('/product/<int:product_id>',methods=['GET','POST'])
def singleProductPage(product_id):
    form = AddToCartForm()
    products_query = Product.query.all()

    if form.validate_on_submit():

        if 'products' not in session:
            print("New session",flush=True)
            session['products'] = []

        product_exists = False
        for product in session['products']:
            if(product[0] == product_id):
                product[1] = int(product[1]) + int(form.quantity.data)
                print(product[1])
                session.modified = True
                product_exists = True
                break

        if not product_exists:
            session['products'] += [[product_id, form.quantity.data]]

        return render_template('single-product-response.html', product = products_query[product_id-1],quantity = form.quantity.data)
    else:
        return render_template('single-product.html', product = products_query[product_id-1], form = form)
    

@app.route('/basket',methods=['GET','POST'])
def basketPage():
    total = 0
    if 'products' in session:
        products = []
        quantities = []

        for product_id, quantity in session['products']:
            product = Product.query.get(product_id)
            if product:
                products.append(product)
                quantities.append(quantity)
                total += product.price * int(quantity)

        total = round(total, 2)
        return render_template('basket.html', products=products, quantities=quantities, total=total)
    else:
        #returns empty if no products
        return render_template('basket.html', products=[], quantities=[], total=total)
    
#handles the quantity adjustment per item

@app.route('/increment/<int:product_id>', methods=['POST'])
def incrementQuantity(product_id):
    if 'products' in session:
        for product in session['products']:
            if product[0] == product_id:
                product[1] += 1
                session.modified = True
                break
    return redirect(url_for('basketPage'))


@app.route('/decrement/<int:product_id>', methods=['POST'])
def decrementQuantity(product_id):
    if 'products' in session:
        for product in session['products']:
            if product[0] == product_id:
                product[1] = int(product[1])
                product[1] -= 1
                if product[1] <= 0:
                    session['products'].remove(product)
                session.modified = True 
                break
    return redirect(url_for('basketPage'))


@app.route('/clear/<int:product_id>', methods=['POST'])
def clearQuantity(product_id):
    if 'products' in session:
        for product in session['products']:
            if product[0] == product_id:
                session['products'].remove(product)
                session.modified = True
                break
    return redirect(url_for('basketPage'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkoutPage():
    checkout_form = CheckoutForm()

    total = 0
    for product_id, quantity in session['products']:
        product = Product.query.get(product_id)
        if product:
            total += product.price * int(quantity)   

    total = round(total, 2)

    if checkout_form.validate_on_submit():

        card_number = checkout_form.card_number.data
        expiry_date = checkout_form.expiry_date.data
        cvv = checkout_form.cvv.data
        successful = ValidatePaymentInfo(card_number, expiry_date, cvv)

        if(successful):
            print("New session",flush=True)
            session['products'] = []

        return render_template('checkout-response.html', successful=successful)
    else:
        return render_template('checkout.html',total=total, checkout_form = checkout_form)


#validates payment information
def ValidatePaymentInfo(card_number, expiry_date, cvv):
    successful = False
    card_number = card_number.replace("-", "").replace(" ", "").strip()
    expiry_date = expiry_date.replace("/", "").replace(" ", "").strip()

    print(card_number,expiry_date,cvv)

    #checks the lengths of each input
    if len(card_number) == 16 and len(expiry_date) == 4 and len(cvv) == 3:

        month = int(expiry_date[:2])
        year = int(expiry_date[-2:])

        print(month, year)

        #if expiry date is within 1 - 12 months and greater than or equal to year 2000
        if 1 <= month <= 12 and 0 <= year:
            successful = True

    return successful

if __name__ == '__main__':
    app.run(host='0.0.0.0')
