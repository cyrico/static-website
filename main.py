# STEPS TO RUN 
# navigate to the directory in the terminal
# create the virtual enviroment: python -m venv .venv
# trigger the virtual enviroment: .venv\Scripts\activate
# install the requirements needed on the ve: pip install -r requirements.txt
# run the site: python main.py 
# if there is a problem running the VE, just install the requirements directly 

from flask import Flask, render_template, request, session
import sqlite3
app = Flask(__name__)
app.secret_key = 'pokemon'

def create_database():
    with sqlite3.connect('pokemon_orders.db') as conn:
        c = conn.cursor()
        c.execute('''        
            CREATE TABLE IF NOT EXISTS Trainers (
                trainerID text NOT NULL,
                password TEXT NOT NULL,
                PRIMARY KEY(trainerID)
            );
        ''')
        c.execute('''        
         CREATE TABLE IF NOT EXISTS Orders (
                trainerID text NOT NULL,
                first_name TEXT NOT NULL, 
                last_name TEXT NOT NULL, 
                town TEXT NOT NULL, 
                pokemon TEXT NOT NULL,
                FOREIGN KEY(trainerID) REFERENCES Trainers(trainerID)
            );
         ''')
        conn.commit()
        # creates the admin account with the database
        selectQuery =  "SELECT password FROM Trainers WHERE trainerID = 'admin'"
        c.execute(selectQuery)
        result = c.fetchall()
        # checks to see if admin already exists 
        if result:
            pass
        else:
            query = "INSERT into Trainers (trainerID, password) VALUES('admin', 'admin')"
            c.execute(query)
            conn.commit()

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/order/')
def order():
    return render_template('order.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/login/')
def login():
    # it shouldn't need this extra check here but just in case it sees if there a current session
    if 'trainerID' not in session:
        return render_template('login.html')
    else:
        return render_template('order.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/order_submit', methods=["POST", "GET"])
def order_submit():
    fName = request.form.get("fname")
    lName = request.form.get('lname')
    town = request.form.get('town')
    pokemon = request.form.get('pokemon')
    query = "SELECT pokemon FROM Orders WHERE trainerID = ?"

    # inserting the order into the database
    with sqlite3.connect('pokemon_orders.db') as conn:
        try:
            c = conn.cursor()
            # checking if the current trainer already has an order in the database
            c.execute(query, (session['trainerID'],))
            result = c.fetchall()
            if result:
                return render_template('errorcode.html', errorMessage = "This account already has a Pokemon request")
            c.execute('''
                    INSERT INTO Orders (trainerID, first_name, last_name, town, pokemon)
                    VALUES (?, ?, ?, ?, ?)''',
            (session['trainerID'], fName, lName, town, pokemon))
            conn.commit()
        # catch all errors
        except sqlite3.Error as e:
            return render_template('errorcode.html', errorMessage = f"An unknown error occured{e}")
    return render_template('errorcode.html', errorMessage = "Pokemon request has been sent!")

@app.route('/account_login', methods=["POST", "GET"])
def account_login():
    # if there is already a current session, skip the login and go to the order page
    if 'trainerID' not in session:
        account_type = request.form.get('action')
        # registering a new account with the database
        if account_type == "Create Account":
            trainerID = request.form.get('ID')
            password = request.form.get('password')
            try:
                with sqlite3.connect('pokemon_orders.db') as conn:
                    c = conn.cursor()
                    c.execute('''
                    INSERT INTO Trainers (trainerID, password)
                        VALUES (?, ?)''',
                    (trainerID, password))
            except sqlite3.IntegrityError:
                return render_template('errorcode.html', errorMessage = "This Trainer ID already exists!")
            except sqlite3.Error as e:
                return render_template('errorcode.html', errorMessage = "An unknown error occured.")
            conn.commit()
            return render_template('errorcode.html', errorMessage = "Account registered.")
        else: 
            # logging in to an existing account 
            ID = request.form.get('ID')
            query = "SELECT password FROM Trainers WHERE trainerID = ?"
            password = request.form.get('password')
            try:
                with sqlite3.connect('pokemon_orders.db') as conn:
                    c = conn.cursor()
                    c.execute(query, (ID,))
                    result = c.fetchone()
                # trainerID not found, should register
                if result is None:
                    return render_template('errorcode.html', errorMessage = "Trainer ID not found! Check the spelling or register this ID.")
                enteredPassword = result[0]
                if enteredPassword != password:
                     return render_template('errorcode.html', errorMessage = "Password does not match for this account!")
                else:
                    # adding the user to the session
                    session['trainerID'] = ID
                    if ID == 'admin':
                        return render_template('admin.html')
                    else:
                        return render_template('order.html')
            # catch errors, the main ones are the unfound user and invalid password
            except sqlite3.Error as e:
                return render_template('errorcode.html', errorMessage = "An unknown error occured.")
    #shouldn't need this part, handled already
    else:
        return render_template('order.html')

@app.route('/logout', methods=["POST"]) 
def logout(): 
    session.pop('trainerID', None)
    return render_template('errorcode.html', errorMessage = "You have been logged out.")

# not the best way to handle the admin dashboard
@app.route('/select_query', methods=["POST", "GET"])
def select_query():
    columns = request.form.get('columns')
    where = request.form.get('WHERE')
    search = request.form.get('search')
    table = request.form.get('table')

    #where was filled in
    if where:
        query = f"SELECT {columns} FROM {table} WHERE {search}"
    #where was not filled in
    else:
        query = f"SELECT {columns} FROM {table}"
    try:
        with sqlite3.connect('pokemon_orders.db') as conn:
            c = conn.cursor()
            c.execute(query)
            data = c.fetchall()
            return render_template('adminresults.html', data=data)
    except sqlite3.Error as e:
        return render_template('adminresults.html', errorMessage = "error - check queries")

@app.route('/delete_query', methods=["POST", "GET"])
def delete_query():
    table =  request.form.get('table')
    search = request.form.get('search')
    where = request.form.get('WHERE')
    if where:
        query = f"DELETE FROM {table} WHERE {search}"
    #where was not filled in
    else:
        query = f"DELETE FROM {table}"
    try:
        with sqlite3.connect('pokemon_orders.db') as conn:
            c = conn.cursor()
            c.execute(query)
            conn.commit()
            return render_template('adminresults.html', data=query)
    except sqlite3.Error as e:
        return render_template('adminresults.html', errorMessage = "error - check queries")
   
if __name__ == '__main__':
    create_database()
    app.run(debug=True)
    
