# Budget script for CLI
# Version 2

# import modules
import sys
import psycopg2
import pandas as pd

# connect to database
db = psycopg2.connect("dbname=budget_database user=postgres password=smile")
cur = db.cursor()

# for pretty printing
solid_line = "_______________________________________________________________\n\n"
dash_line = "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n\n"


def request_command():
    # get input from the command line
    n = input("INPUT: ").lower()
    items = n.split()
    return items


def get_action(items):
    # looks for executable action in the command
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

    elif "payout" in items:
        return "payout"

    elif "analyze" in items:
        return "analyze"

    elif "else" in items or "custom" in items:
        return "custom"

    else:
        return "unknown"


def get_table(items):
    # looks for known table in the command
    if "exit" in items:
        print("Exiting the budget... \nGoodbye")
        sys.exit(0)

    if "budget" in items:
        return "budget"

    elif "income" in items:
        return "income"

    elif "expense" in items:
        return "expense"

    elif "payout" in items:
        return "payout"

    elif "else" in items or "custom" in items \
        or "analyze" in items or "surplus" in items \
            or "payout" in items or "balance" in items:
                return None

    else:
        return "unknown"


def parse_command():
    # get understandable command from the user
    to_do_list = request_command()
    action = get_action(to_do_list)
    sql_table = get_table(to_do_list)

    while action == "unknown":
        print("""{}Please select an ACTION:\n \nINSERT, DELETE, UPDATE, VIEW, ANALYZE, EXIT \n
                Or ELSE for custom queries. \n""".format(solid_line))
        to_do_list = request_command()
        action = get_action(to_do_list)

    while sql_table == "unknown":
        print("{}Please select a TABLE for your {}: ".format(dash_line, action.upper()),
              "\n \nbudget, income, expense, payout \n")
        to_do_list = request_command()
        sql_table = get_table(to_do_list)

    return [action, sql_table]


def check_repeat():
    # repeat action or go back to main menu
    n = input("\nRepeat command? ").lower()
    if n == "" or n == "y" or n == "yes":
        return True
    else:
        return False


def validate_entry():
    # asks user if change should be made
    print("\nCommit change?\n")
    entry = input("[y]/n: ").lower()

    if entry != "n" and entry != "no":
        return True

    else:
        return False


def use_funds(category_value, amount_value):
    # get current amount from budget
    query = "SELECT funds FROM budget WHERE category = %s;"
    # execute statement and fetch the results
    cur.execute(query, (category_value,))
    results = cur.fetchone()
    # calculate new amount and update the table
    new_amount = float(results[0]) - amount_value
    update_query = "UPDATE budget SET funds = %s WHERE category = %s"
    cur.execute(update_query, (new_amount, category_value))


def add_funds(amount_value):
    # to be done after adding an item to the income table
    update_query = '''WITH current AS (
                        SELECT category, proportion, funds
                        FROM budget
                        )
                        UPDATE budget 
                        SET funds = (current.funds + (current.proportion * %s))
                        FROM current
                        WHERE budget.category = current.category;
                   '''
    cur.execute(update_query, [amount_value])


def balance_budget(sep):
    # resolve budget proportions to add up to 1
    # necessary after adding or removing any item from the budget
    current_budget = pd.read_sql("SELECT category, proportion FROM budget;", db)
    total_p = current_budget['proportion'].sum()
    # ask user to change proportions until total_p is 1
    while total_p != 1:
        print(sep, "Budget needs balancing!\n")
        print(current_budget, '\n')
        print("Total: ", total_p)
        edit_cat = input("Choose a category to adjust: ")
        # if user does not enter a category in the budget, ask again
        while not any(current_budget.category == edit_cat):
            edit_cat = input("Unrecognized category. Try again: ")
        # get new proportion
        new_p = float(input("Enter new proportion: "))
        # update the budget table
        update_query = "UPDATE budget SET proportion = %s WHERE category = %s;"
        cur.execute(update_query, (new_p, edit_cat))
        # re-calculate total_p
        current_budget = pd.read_sql("SELECT category, proportion FROM budget;", db)
        total_p = current_budget['proportion'].sum()


def get_values(xtable, update=False, row_id=None):
    # get values for new row from the user.
    # update=True adds option to import existing values
    # row_id necessary if update=True
    new_row = {}
    # get values for the new row
    if xtable == "expense":
        # expense_date
        new_row['expense_date'] = input("\ndate (YYYY/MM/DD): ")
        if update and new_row['expense_date'] == "":
            new_row['expense_date'] = get_one(xtable, "expense_date", row_id)
        # category
        new_row['category'] = input("\ncategory: ").lower()
        if update and new_row['category'] == "":
            new_row['category'] = get_one(xtable, "category", row_id)
        else:
            # validate new entry: category must be defined in budget
            categories = pd.read_sql("SELECT category FROM budget;",
                                     db)['category'].tolist()
            while new_row['category'] not in categories:
                # if category is not defined, print categories and ask again
                print("\nDefined categories include: ", categories)
                new_row['category'] = input("\ncategory: ").lower()
        # payee
        new_row['payee'] = input("\npayee: ").title()
        if update and new_row['payee'] == "":
            new_row['payee'] = get_one(xtable, "payee", row_id)
        # amount
        new_row['amount'] = float(input("\namount: "))
        if update and new_row['amount'] == "":
            new_row['amount'] = get_one(xtable, "amount", row_id)
        # account
        new_row['account'] = input("\naccount: ")
        if update and new_row['account'] == "":
            new_row['account'] = get_one(xtable, "account", row_id)

    elif xtable == "budget":
        # category
        new_row['category'] = input("\ncategory: ")
        if update and new_row['category'] == "":
            new_row['category'] = get_one(xtable, "category", row_id)
        # proportion
        new_row['proportion'] = float(input("\nproportion: "))
        if update and new_row['category'] == "":
            new_row['category'] = get_one(xtable, "category", row_id)
        # funds
        if update:
            new_row['funds'] = float(input("\nfunds (manual update not recommended): "))
            if new_row['funds'] == "":
                new_row['funds'] = get_one(xtable, "funds", row_id)
        else:
            # funds added to budget categories when income added
            new_row['funds'] = 0

    elif xtable == "income":
        # income_date
        new_row['income_date'] = input("\ndate (YYYY/MM/DD): ")
        if update and new_row['income_date'] == "":
            new_row['income_date'] = get_one(xtable, "income_date", row_id)
        # contributor
        new_row['contributor'] = input("\ncontributor: ")
        if update and new_row['contributor'] == "":
            new_row['contributor'] = get_one(xtable, "contributor", row_id)
        # amount
        new_row['amount'] = float(input("\namount: "))
        if update and new_row['amount'] == "":
            new_row['amount'] = get_one(xtable, "amount", row_id)

    elif xtable == "payout":
        # payout_date
        new_row['payout_date'] = input("\ndate (YYYY/MM/DD): ")
        if update and new_row['payout_date'] == "":
            new_row['payout_date'] = get_one(xtable, "payout_date", row_id)
        # account
        new_row['account'] = input("\naccount: ")
        if update and new_row['account'] == "":
            new_row['account'] = get_one(xtable, "account", row_id)
        # amount
        new_row['amount'] = float(input("\namount: "))
        if update and new_row['amount'] == "":
            new_row['amount'] = get_one(xtable, "amount", row_id)

    return new_row


def insert_row(xtable, sep1=solid_line, sep2=dash_line):
    # add a row to a table
    # check if table is payout, if so call the new_payout function
    if xtable == 'payout':
        new_payout()

    else:
        print("{}INSERT INTO {}: ".format(sep1, xtable))
        # get values for the new row
        new_row = get_values(xtable)

        # print new row and ask if it should be added
        print("{}New {} item:\n".format(sep2, xtable))
        print(new_row)
        commit_change = validate_entry()

        # insert new row into the database:
        if commit_change:

            if xtable == "expense":
                # first add the row to the expense table
                insert_query = """INSERT INTO expense
                                    (expense_date, category, payee, amount, account)
                                  VALUES (%s, %s, %s, %s, %s);"""
                cur.execute(insert_query, (new_row['expense_date'],
                                           new_row['category'], new_row['payee'],
                                           new_row['amount'], new_row['account']))
                # next update the budget table
                use_funds(new_row['category'], new_row['amount'])

            elif xtable == "income":
                # first add the row to the income table
                insert_query = """INSERT INTO income
                                    (income_date, contributor, amount)
                                  VALUES (%s, %s, %s);"""
                cur.execute(insert_query, (new_row['income_date'],
                                           new_row['contributor'], new_row['amount']))
                # next update the budget table
                add_funds(new_row['amount'])

            elif xtable == "budget":
                # first add the row to the budget table
                insert_query = """INSERT INTO budget
                                    (category, proportion, funds)
                                  VALUES (%s, %s, %s);"""
                cur.execute(insert_query, (new_row['category'],
                                           new_row['proportion'], new_row['funds']))
                # next update the budget table
                balance_budget(sep=sep2)

            db.commit()
            print("\nCommitted to budget database!")

        else:
            print("\nChange discarded!")


def custom_query():
    # executes a custom query input by the user
    print("{}Custom SQL query:\n".format(solid_line))
    n = input("INPUT: ")
    # wait until ';' to signal the end of the query
    while ";" not in n:
        n += (" " + input("->  "))

    items = n.lower().split()
    # determine if results need to be returned to the console
    if "insert" in items or "delete" in items or "drop" in items or "create" in items:
        commit_change = validate_entry()
        if commit_change:
            cur.execute(n)
            db.commit()
    else:
        results = pd.read_sql(n, db)
        print(dash_line)
        print(results)


def delete_row(xtable):
    # choose and delete a row from the table
    print("{}Select a row to DELETE from {},".format(solid_line, xtable),
          "or enter 'VIEW' to see the table.\n")
    delete_id = input("INPUT: ").lower()
    # if a number is not entered
    while not delete_id.isdigit():
        # check if user wants to exit or view
        delete_id = check_row(delete_id, "DELETE", xtable)

    query = "DELETE FROM {} WHERE id = {};".format(xtable, delete_id)
    # Double check before committing change
    commit_change = validate_entry()
    if commit_change:

        # make changes to budget table if other tables edited
        if xtable == 'expense' or xtable == 'income':
            # get the amount deleted
            amount = float(get_one(xtable, 'amount', delete_id))

            if xtable == 'expense':
                # get the category value expense was in
                category = get_one(xtable, 'category', delete_id)
                # pass negative amount to add_funds add the funds back
                use_funds(amount_value=(-amount), category_value=category)
            else:
                # remove deleted income from the budget
                add_funds((-amount))

        cur.execute(query)
        # balance the budget if budget was edited
        if xtable == 'budget':
            balance_budget(sep=dash_line)

        db.commit()
        print("\nCommitted to budget database!")
    else:
        print("\nChange discarded!")


def view(xtable):
    # get filter for the table
    view_where = input("{}SELECT * FROM {}... ".format(solid_line, xtable))
    # create query
    query = "SELECT * FROM {} {};".format(xtable, view_where)
    # execute statement and fetch the results
    results = pd.read_sql(query, db)
    print(dash_line)
    print(results)


def get_one(xtable, column, id_row):
    # get current value, for use in the update or delete row function
    query = "SELECT {} FROM {} WHERE id = {};".format(column, xtable, id_row)
    cur.execute(query)
    return cur.fetchone()[0]


def check_row(entry, action_text, xtable, sep=dash_line):
    # check user input for exit or view command when expecting an id
    if "exit" in entry:
        print("Exiting the budget... \nGoodbye")
        sys.exit(0)
    if "view" in entry:
        view(xtable)
        print(sep)
    new_row = input("{} WHERE id = ".format(action_text)).lower()
    return new_row


def update_row(xtable, sep1=solid_line, sep2=dash_line):
    # Update an existing row in a table with new data
    # Get the row to update
    print("{}Enter a row to UPDATE from {},".format(sep1, xtable),
          "or enter 'VIEW' to see the table.\n")
    update_id = input("INPUT: ").lower()
    while not update_id.isdigit():
        # check for exit or view commands
        update_id = check_row(update_id, "UPDATE", xtable)
    # ask user to enter the new values
    print("\nEnter new values, or press enter to keep old value")
    new_row = get_values(xtable, update=True, row_id=update_id)
    # print the updated row
    print("{}Updated {} item:\n".format(sep2, xtable))
    print(new_row)
    # ask if change should be made
    commit_change = validate_entry()
    if commit_change:
        if xtable == 'expense' or xtable == 'income':
            # first get difference in amounts
            prev_amount = float(get_one(xtable, 'amount', update_id))
            amount_delta = new_row['amount'] - prev_amount

            if xtable == 'expense':
                prev_category = get_one(xtable, 'category', update_id)
                update_query = """UPDATE expense
                                    SET
                                        expense_date = %s,
                                        category = %s,
                                        payee = %s,
                                        amount = %s,
                                        account = %s
                                    WHERE id = %s;
                                    """
                cur.execute(update_query, (new_row['expense_date'],
                                           new_row['category'], new_row['payee'],
                                           new_row['amount'], new_row['account'],
                                           update_id))
                # update the amounts in the budget table
                use_funds(amount_value=amount_delta, category_value=prev_category)

            else:
                update_query = """UPDATE income
                                    SET
                                        income_date = %s,
                                        contributor = %s,
                                        amount = %s
                                    WHERE id = %s;
                                    """
                cur.execute(update_query, (new_row['income_date'],
                                           new_row['contributor'],
                                           new_row['amount'], update_id))
                # update the amounts in the budget table
                add_funds(amount_delta)

        elif xtable == 'budget':
            update_query = """UPDATE budget
                                SET
                                    category = %s,
                                    proportion = %s,
                                    funds = %s
                                WHERE id = %s;
                                """
            cur.execute(update_query, (new_row['category'],
                                       new_row['proportion'],
                                       new_row['funds'], update_id))
            # balance the budget
            balance_budget(sep=dash_line)

        else:
            update_query = """UPDATE payout
                                SET
                                    payout_date = %s,
                                    account = %s,
                                    amount = %s
                                WHERE id = %s;
                                """
            cur.execute(update_query, (new_row['payout_date'],
                                       new_row['account'],
                                       new_row['amount'], update_id))

        db.commit()
        print("\nCommitted to budget database!")

    else:
        print("\nChange discarded!")


def new_payout(sep=dash_line):
    # repay expenses made from individual accounts
    # Calculate amount to payout
    payout_amounts = '''SELECT 	e.account
		                        ,(SUM(e.amount) - COALESCE(SUM(p.amount), 0)) AS to_payout
                        FROM 	expense AS e
                        LEFT JOIN payout AS p
		                    ON e.account = p.account 	
                        GROUP BY e.account
                        ;'''
    results = pd.read_sql(payout_amounts, db)
    print(dash_line, results, '\n', dash_line)
    # ask if user would like to add a payout
    n = input('Payout now? [y]/n:').lower()
    if n != "n" and n != "no":
        new_row = get_values('payout')

        # print new row and ask if it should be added
        print("{}New payout item:\n".format(sep))
        print(new_row)
        commit_change = validate_entry()
        # make change
        if commit_change:
            insert_query = """INSERT INTO payout
                                    (payout_date, account, amount)
                                  VALUES (%s, %s, %s);"""
            cur.execute(insert_query, (new_row['payout_date'],
                                       new_row['account'], new_row['amount']))
            db.commit()
            print("\nCommitted to budget database!")

        else:
            print("\nChange discarded!")


print("{}Welcome to the SHARED BUDGET!\n".format(solid_line))

while True:
    print(solid_line)
    command = parse_command()
    repeat_loop = True
    # insert --------
    if command[0] == "insert":
        while repeat_loop:
            insert_row(command[1])
            repeat_loop = check_repeat()
    # custom ---------
    if command[0] == "custom":
        while repeat_loop:
            custom_query()
            repeat_loop = check_repeat()
    # delete -------
    if command[0] == "delete":
        while repeat_loop:
            delete_row(command[1])
            repeat_loop = check_repeat()
    # view ---------
    if command[0] == "view":
        while repeat_loop:
            view(command[1])
            repeat_loop = check_repeat()
    # update --------
    if command[0] == "update":
        while repeat_loop:
            update_row(command[1])
            repeat_loop = check_repeat()
    # payout --------
    if command[0] == "payout":
        while repeat_loop:
            new_payout()
            repeat_loop = check_repeat()