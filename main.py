'''
The MIT License (MIT)

Copyright (c) 2013 Andy Hamilton - FINEIO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import sqlite3
import stripe

from flask import *

##
# Start up the Application
##

app = Flask(__name__)
app.config.from_pyfile('config/settings.py')

##
# Common database operations
##

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def query_db(query, args=(), one=False):
	cur = g.db.execute(query,args)
	rv  = [dict((cur.description[idx][0], value)
			for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None)

##
# Request before/after filters
##

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

##
# Application Code
##

@app.route('/')
def index_action():
	return redirect(url_for('show_customers'))

@app.route('/customers')
def show_customers():
	cur = g.db.execute('select id, first_name, last_name from customers')
	customers = [dict(id=row[0], first_name=row[1], last_name=row[2]) for row in cur.fetchall()]

	return render_template('customers/show.html', customers=customers)

@app.route('/customers/add', methods=['POST'])
def add_customer():
	g.db.execute('insert into customers (first_name, last_name) values(?,?)',[request.form['first_name'], request.form['last_name']])
	g.db.commit()

	flash('New customer was created')

	return redirect(url_for('show_customers'))

@app.route('/customers/<int:customer_id>/payments')
def add_payment(customer_id):
	customer = query_db('select id, first_name, last_name from customers where id = ?', [customer_id], one=True)

	payments_cur = g.db.execute('select amount, charge_id from payments where customer_id = ?', [customer_id])
	payments = [dict(amount=row[0], charge_id=row[1]) for row in payments_cur.fetchall()]

	if customer is None:
		print 'No such customer'
	else:
		return render_template('payments/add.html', customer=customer, payments=payments)

@app.route('/payments/create', methods=['POST'])
def create_payment():
	customer = query_db('select * from customers where id = ?', [request.form['customer_id']], one=True)

	if customer is None:
		print 'No such customer'
	else:
		stripe.api_key = app.config['STRIPE_API_KEY']

		charge = stripe.Charge.create(
			amount   = int(request.form['amount'])*100,
			currency = "gbp",
			card     = {
				'number':4242424242424242,
				'exp_month':'12',
				'exp_year':'13',
				'cvc':'123',
				'name':str(customer['first_name'])+" "+str(customer['last_name'])
			},
			description = request.form['description']
		)

		if charge.paid:
			g.db.execute('insert into payments (customer_id, charge_id, amount) values(?,?,?)', [customer['id'], charge.id, charge.amount])
			g.db.commit()

			flash('Payment charge succesful')

			return redirect('/customers/'+str(customer['id'])+'/payments')
		else:
			print "There was an error processing the payment. Please try again"

if __name__ == '__main__':
	app.run()