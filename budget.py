# Budget script for CLI
import sys
import psycopg2


import pprint
import pandas as pd
from datetime import datetime as dt

db = psycopg2.connect("dbname=budget_database user=postgres password=smile")
cur = db.cursor()

solid_line = "_______________________________________________________________\n\n"
dash_line = "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n\n"

def request_command():
    n = input("INPUT: ").lower()
    items = n.split()
    return items

def get_action(items):
    if "exit" in items:
        print("Exiting the budget... \nGoodbye")
        sys.exit(0)
    elif "insert" in items:
        return "insert"
    elif "delete" in items:
        return "delete"
    elif "update" in items:
        return "update"
    elif "view" in items:
        return "view"
    elif "balance" in items:
        return "balance"
    elif "surplus" in items:
        return "surplus"
    elif "payout" in items:
        return "payout"
    elif "analyze" in items:
        return "analyze"
    elif "else" in items or "custom" in items:
        return "custom"
    else:
        return "unknown"

def get_table(items):
    if "exit" in items:
        print("Exiting the budget... \nGoodbye")
        sys.exit(0)
    if "budget" in items:
        return "budget"
    elif "" in items or "monthly_transactions" in items:
        return "monthly_transactions"
    elif "transactions" in items:
        return "transactions"
    elif "else" in items or "custom" in items or "analyze" in items or "surplus" in items or "payout" in items or "balance" in items:
        return None
    else:
        return "unknown"

def parse_command():
    to_do_list = request_command()
    action = get_action(to_do_list)
    sql_table = get_table(to_do_list)

    while action == "unknown":
        print("{}Please select an ACTION:\n \nINSERT, DELETE, UPDATE, VIEW, ANALYZE, EXIT \nOr ELSE for custom queries. \n".format(solid_line))
        to_do_list = request_command()
        action = get_action(to_do_list)


    while sql_table == "unknown":
        print("{}Please select a TABLE for your {}: \n \nbudget, transactions, monthly_transactions \n".format(dash_line, action.upper()))
        to_do_list = request_command()
        sql_table = get_table(to_do_list)

    return [action, sql_table]

def validate_entry():
    print("\nCommit change?\n")
    entry = input("[y]/n: ").lower()
    if entry != "n" and entry != "no":
        return True
    else:
        return False

def insert(sql_table):
    category_value = input("{}INSERT INTO {}: \n \nCATEGORY: ".format(solid_line, sql_table)).lower()
    amount_value = float(input("\nAMOUNT: "))
    if sql_table == "budget":
        month_value = input("\nMONTH: ")
        year_value = int(input("\nYEAR: "))

        print("{}New budget item:\n".format(dash_line))

        print(pd.DataFrame(data = [[category_value, amount_value, month_value, year_value]],
        columns = ['category', 'amount', 'month', 'year']
        ))

        commit_change = validate_entry()
        if commit_change:
            insert_query = """INSERT INTO budget (category, amount, month, year)
                              VALUES (%s, %s, %s, %s);"""
            cur.execute(insert_query, (category_value, amount_value, month_value, year_value))
            db.commit()
            print("\nCommitted to budget database!")
        else:
            print("\nChange discarded!")
    else:
        transaction_type_value = input("\nTRANSACTION TYPE [income/expense]: ")
        account_value = input("\nACCOUNT (Corey/Shelby/Shared): ")
        payee_value = input("\nPAYEE: ")

        if sql_table == "transactions":
            transaction_date_value = input("\nTRANSACTION DATE: ")
            print("{}New transaction:\n".format(dash_line))

            print(pd.DataFrame(data = [[category_value, amount_value, transaction_type_value, account_value, payee_value, transaction_date_value]],
            columns = ['category', 'amount', 'transaction type', 'account', "payee", "transaction date"]
            ))

            commit_change = validate_entry()
            if commit_change:
                insert_query = """INSERT INTO transactions (transaction_type, category, amount, account, payee, transaction_date)
                                  VALUES (%s, %s, %s, %s, %s, %s);"""
                cur.execute(insert_query, (transaction_type_value, category_value, amount_value, account_value, payee_value, transaction_date_value))
                db.commit()
                print("\nCommitted to budget database!")
            else:
                print("\nChange discarded!")

        else:
            day_of_month_value = input("\nDAY OF MONTH: ")
            print("{}New monthly transaction:\n".format(dash_line))

            print(pd.DataFrame(data = [[category_value, amount_value, transaction_type_value, account_value, payee_value, day_of_month_value]],
            columns = ['category', 'amount', 'transaction type', 'account', "payee", "day of month"]
            ))

            commit_change = validate_entry()
            if commit_change:
                insert_query = """INSERT INTO monthly_transactions (transaction_type, category, amount, account, payee, day_of_month)
                                  VALUES (%s, %s, %s, %s, %s, %s);"""
                cur.execute(insert_query, (transaction_type_value, category_value, amount_value, account_value, payee_value, day_of_month_value))
                db.commit()
                print("\nCommitted to budget database!")
            else:
                print("\nChange discarded!")

def custom_query():
    print("{}Custom SQL query:\n".format(solid_line))
    n = input("INPUT: ")
    while ";" not in n:
        n += (" " + input("->  "))
    items = n.lower().split()
    if "insert" in items or "delete" in items or "drop" in items or "create" in items:
        commit_change = validate_entry()
        if commit_change:
            cur.execute(n)
            db.commit()
    else:
        results = pd.read_sql(n, db)
        print(dash_line)
        print(results)

def delete_query(sql_table):
    print("{}Select a row to DELETE from {}, or enter 'VIEW' to see the table.\n".format(solid_line, sql_table))
    delete_row = input("INPUT: ").lower()
    while not delete_row.isdigit():
        if "exit" in delete_row:
            print("Exiting the budget... \nGoodbye")
            sys.exit(0)
        if "view" in delete_row:
            view_query(sql_table)
            print(dash_line)
        delete_row = input("DELETE FROM {} WHERE id = ").lower()
    query = "DELETE FROM {} WHERE id = {};".format(sql_table, delete_row)
    commit_change = validate_entry()
    if commit_change:
        cur.execute(query)
        db.commit()
        print("\nCommitted to budget database!")
    else:
        print("\nChange discarded!")

    # delete row

def view_query(sql_table):
    # get filter
    view_where = input("{}SELECT * FROM {}... ".format(solid_line, sql_table))
    # create query
    query = "SELECT * FROM {} {};".format(sql_table, view_where)
    # execute statement and fetch the results
    results = pd.read_sql(query, db)
    print(dash_line)
    print(results)

def get_one(sql_table, column, id_row):
    query = "SELECT {} FROM {} WHERE id = {};".format(column, sql_table, id_row)
    cur.execute(query)
    return cur.fetchone()

def update_query(sql_table):
        print("{}Select a row to UPDATE from {}, or enter 'VIEW' to see the table.\n".format(solid_line, sql_table))
        update_row = input("INPUT: ").lower()
        while not update_row.isdigit():
            if "exit" in update_row:
                print("Exiting the budget... \nGoodbye")
                sys.exit(0)
            if "view" in update_row:
                view_query(sql_table)
                print(dash_line)
            update_row = input("UPDATE WHERE id = ").lower()
        # enter new values
        print("\nEnter new values, or press enter to keep old value")
        category_value = input("\nCATEGORY: ").lower()
        if category_value == "":
            category_value = get_one(sql_table, "category", update_row)
        amount_value = input("\nAMOUNT: ")
        if amount_value == "":
            amount_value = get_one(sql_table, "amount", update_row)
        else:
            amount_value = float(amount_value)

        if sql_table == "budget":
            month_value = input("\nMONTH: ")
            if month_value == "":
                month_value = get_one(sql_table, "month", update_row)
            else:
                month_value = int(month_value)
            year_value = input("\nYEAR: ")
            if year_value == "":
                year_value = get_one(sql_table, "year", update_row)
            else:
                year_value = int(year_value)
            print("{}Updated budget item:\n".format(dash_line))

            print(pd.DataFrame(data = [[category_value, amount_value, month_value, year_value]],
            columns = ['category', 'amount', 'month', 'year']
            ))

            commit_change = validate_entry()
            if commit_change:
                insert_query = """UPDATE budget
                                  SET
                                    category = %s,
                                    amount = %s,
                                    month = %s,
                                    year = %s
                                  WHERE id = %s;"""
                cur.execute(insert_query, (category_value, amount_value, month_value, year_value, update_row))
                db.commit()
                print("\nCommitted to budget database!")
            else:
                print("\nChange discarded!")
        else:
            transaction_type_value = input("\nTRANSACTION TYPE [income/expense]: ")
            if transaction_type_value == "":
                transaction_type_value = get_one(sql_table, "transaction_type", update_row)

            account_value = input("\nACCOUNT (Corey/Shelby/Shared): ")
            if account_value == "":
                account_value = get_one(sql_table, "account", update_row)

            payee_value = input("\nPAYEE: ")
            if payee_value == "":
                payee_value = get_one(sql_table, "payee", update_row)

            if sql_table == "transactions":
                transaction_date_value = input("\nTRANSACTION DATE: ")
                if transaction_date_value == "":
                    transaction_date_value = get_one(sql_table, "transaction_date", update_row)
                print("{}New transaction:\n".format(dash_line))

                print(pd.DataFrame(data = [[category_value, amount_value, transaction_type_value, account_value, payee_value, transaction_date_value]],
                columns = ['category', 'amount', 'transaction type', 'account', "payee", "transaction date"]
                ))

                commit_change = validate_entry()
                if commit_change:
                    update_query = """UPDATE transactions
                                      SET
                                        transaction_type = %s,
                                        category = %s,
                                        amount = %s,
                                        account = %s,
                                        payee = %s,
                                        transaction_date= %s
                                      WHERE id = %s;
                                  """
                    cur.execute(update_query, (transaction_type_value, category_value, amount_value, account_value, payee_value, transaction_date_value, update_row))
                    db.commit()
                    print("\nCommitted to budget database!")
                else:
                    print("\nChange discarded!")

            else:
                day_of_month_value = input("\nDAY OF MONTH: ")
                if day_of_month_value == "":
                    day_of_month_value = get_one(sql_table, "day_of_month", update_row)

                print("{}New monthly transaction:\n".format(dash_line))

                print(pd.DataFrame(data = [[category_value, amount_value, transaction_type_value, account_value, payee_value, day_of_month_value]],
                columns = ['category', 'amount', 'transaction type', 'account', "payee", "day of month"]
                ))

                commit_change = validate_entry()
                if commit_change:
                    insert_query = """UPDATE monthly_transactions
                                      SET
                                        transaction_type = %s,
                                        category = %s,
                                        amount = %s,
                                        account = %s,
                                        payee = %s,
                                        day_of_month = %s
                                      WHERE id = %s;"""
                    cur.execute(insert_query, (transaction_type_value, category_value, amount_value, account_value, payee_value, day_of_month_value, update_row))
                    db.commit()
                    print("\nCommitted to budget database!")
                else:
                    print("\nChange discarded!")

def budget_balance(today_value):
    print("\nEnter month (#), or press enter for current month")
    month_value = input("\nMONTH: ")
    if month_value == "":
        month_value = today.month
    else:
        month_value == int(month_value)
    print("\nEnter year, or press enter for current year")
    year_value = input("\nYEAR: ")
    if year_value == "":
        year_value = today.year
    else:
         year_value = int(year_value)
    # create the query
    balance_query = """WITH months_budget AS (
	                  SELECT
		                    category,
		                    SUM(amount) AS amount
	                  FROM budget
	                  WHERE year = {}
	                  AND month = {}
	                  GROUP BY category
                      ),
                      months_transactions AS (
	                     SELECT
		                      category,
		                      SUM(amount) as amount
	                     FROM transactions
	                     WHERE EXTRACT(YEAR FROM transaction_date) = {}
	                     AND EXTRACT(MONTH FROM transaction_date) = {}
                         GROUP BY category
                     )
                     SELECT
	                    b.category AS category,
	                    b.amount AS budgeted,
	                    t.amount AS spent,
	                    (b.amount - t.amount) AS remainder
                    FROM months_budget b
                    FULL JOIN months_transactions t ON b.category = t.category
                    ORDER BY (b.amount - t.amount) DESC;""".format(year_value, month_value, year_value, month_value)
    results = pd.read_sql(balance_query, db)
    print(dash_line)
    print(results)

def budget_surplus(today_value):
    print("\nEnter month (#), or press enter for current month")
    month_value = input("\nMONTH: ")
    if month_value == "":
        month_value = today.month
    else:
        month_value == int(month_value)
    print("\nEnter year, or press enter for current year")
    year_value = input("\nYEAR: ")
    if year_value == "":
        year_value = today.year
    else:
         year_value = int(year_value)
    # create the query
    surplus_query = """WITH months_budget AS (
	                  SELECT
		                    SUM(amount) AS amount
	                  FROM budget
	                  WHERE year = {}
	                  AND month = {}
                      ),
                      months_transactions AS (
	                     SELECT
		                      SUM(amount) as amount
	                     FROM transactions
	                     WHERE EXTRACT(YEAR FROM transaction_date) = {}
	                     AND EXTRACT(MONTH FROM transaction_date) = {}
                     )
                     SELECT
	                    (b.amount - t.amount) AS months_surplus
                    FROM months_budget b, months_transactions t
                    ORDER BY (b.amount - t.amount) DESC;""".format(year_value, month_value, year_value, month_value)
    results = pd.read_sql(surplus_query, db)
    print(dash_line)
    print(results)

def budget_payout(today_value):
    print("\nEnter month (#), or press enter for current month")
    month_value = input("\nMONTH: ")
    if month_value == "":
        month_value = today.month
    else:
        month_value == int(month_value)
    print("\nEnter year, or press enter for current year")
    year_value = input("\nYEAR: ")
    if year_value == "":
        year_value = today.year
    else:
         year_value = int(year_value)
    # create the query
    payout_query = """SELECT
	                   account,
	                   SUM(amount) AS amount_spent
                     FROM transactions
                     WHERE EXTRACT(YEAR FROM transaction_date) = {}
	                    AND EXTRACT(MONTH FROM transaction_date) = {}
                     GROUP BY account;""".format(year_value, month_value)
    results = pd.read_sql(payout_query, db)
    print(dash_line)
    print(results)

def check_repeat():
    print("\nPress enter to repeat this command or type any key to go back.")
    n = input("\nREPEAT? ").lower()
    if n == "" or n == "y":
        return True
    else:
        return False

today = dt.today()

print("{}Welcome to the SHARED BUDGET!\n".format(solid_line))

while True:
    print(solid_line)
    command = parse_command()
    repeat_loop = True
    # insert --------
    if command[0] == "insert":
        while repeat_loop:
            insert(command[1])
            repeat_loop = check_repeat()
    # delete -------
    if command[0] == "delete":
        while repeat_loop:
            delete_row(command[1])
            repeat_loop = check_repeat()

    # update ------
    if command[0] == "update":
        while repeat_loop:
            update_query(command[1])
            repeat_loop = check_repeat()

    # view --------
    if command[0] == "view":
        while repeat_loop:
            view_query(command[1])
            repeat_loop = check_repeat()
    # balance -----
    if command[0] == "balance":
        while repeat_loop:
            budget_balance(today)
            repeat_loop = check_repeat()

    # surplus ------
    if command[0] == "surplus":
        while repeat_loop:
            budget_surplus(today)
            repeat_loop = check_repeat()

    # payout ------
    if command[0] == "payout":
        while repeat_loop:
            budget_payout(today)
            repeat_loop = check_repeat()
    # analyze -----
    if command[0] == "analyze":
        print("\nANALYZE options: BALANCE, SURPLUS, or PAYOUT\n")

    # custom
    if command[0] == "custom":
        while repeat_loop:
            custom_query()
            repeat_loop = check_repeat()
