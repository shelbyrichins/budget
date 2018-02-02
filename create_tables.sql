CREATE TABLE budget (
	id SERIAL,
	category VARCHAR PRIMARY KEY,
	proportion NUMERIC (3,2),
	funds NUMERIC(10,2)
);

CREATE TABLE income (
	id SERIAL,
	income_date DATE,
	contributor VARCHAR,
	amount NUMERIC(10,2)
);

CREATE TABLE expense (
	id SERIAL,
	expense_date DATE,
	category VARCHAR REFERENCES budget(category),
	payee VARCHAR, 
	amount NUMERIC(10,2),
	account VARCHAR
);

CREATE TABLE payout (
	id SERIAL, 
	payout_date DATE, 
	amount NUMERIC(10,2),
	account VARCHAR
);
