# Budget Program

Command-line operated budget that tracks expenses, income, and funds in budgeted categories. It was designed to track transactions by multiple accounts with a single shared budget. All data is stored in a PostgreSQL database that is connected to using the psycopg2 Python module. All changes made to income or expense tables result in changes to the budget table.   

## Getting Started
1. Create PostgreSQL database. Code used to create the budget, expense, and income tables can be found in the 'create_tables.sql' file. 
2. Connect to database by editing line 10 of the python code to connect to your personal database containing the budget, expense, and income tables.
```
# connect to database
db = psycopg2.connect("dbname=budget_database user=postgres password=smile")
```
3. If necessary, use pip to install necessary Python modules: sys, psycopg2, pandas 

## Functionality



## Authors

* **Shelby Richins** 

