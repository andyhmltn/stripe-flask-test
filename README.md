Stripe/Flask Test
=====================

This is a test. I'm trying out both the Flask framework and the payment provider 'Stripe' using their UK beta. 

Getting Started
=====================
First, you need to import the database:

	sqlite3 config/db/payments.db < config/db/schema.sql

Next rename `config/settings.py.sample` to `config/settings.py` and edit to your liking.

Then just run `python main.py`... Enjoy!