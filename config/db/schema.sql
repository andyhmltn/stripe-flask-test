drop table if exists customers;
create table customers (
	id integer primary key autoincrement,
	first_name string not null,
	last_name string not null,
	primary_card string
);

drop table if exists payments;
create table payments (
	id integer primary key autoincrement,
	customer_id integer,
	charge_id string,
	amount integer
);