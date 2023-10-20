from flask import Flask, request, jsonify,session

import mysql.connector
from flask_cors import CORS



app = Flask(__name__)
CORS(app)
app.secret_key = 'loginsecret'


# MySQL Configuration

db_config = {

    'host': 'localhost',

    'user': 'root',

    'password': '',

    'database': 'serve',

}

 

# Initialize the MySQL connection

mysql = mysql.connector.connect(**db_config)

 

@app.route('/register', methods=['POST'])

def register():

    try:

        # Get data from the POST request as JSON

        data = request.get_json()

        name = data.get('name')

        email = data.get('email')

        password = data.get('password')

       

        cursor = mysql.cursor()

        cursor.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (name, email, password))

 

        # Commit the transaction and close the cursor

        mysql.commit()

        cursor.close()

       

        return jsonify({"message": "You have successfully registered!"}), 201

   

    except Exception as e:

        return jsonify({"error": str(e)}), 500

 

 

 

@app.route('/login', methods=['POST'])

def login():

    try:

        if 'user_id' in session:

            return jsonify({"message": "User is already logged in!"}), 200

 

        data = request.get_json()

        email = data.get('email')

        password = data.get('password')

 

        cursor = mysql.cursor()

        cursor.execute('SELECT user_id, email, password,name FROM user WHERE email = %s', (email,))

        user = cursor.fetchone()

        cursor.close()

 

        if user and user[2] == password:

            # Store user ID in the session to mark the user as logged in

            session['user_id'] = user[0]
            session['user_name'] = user[3]

          


            return jsonify({"message": "Logged in successfully!",'username':session['user_name']}), 200

        else:

            return jsonify({"error": "Invalid email or password"}), 401

 

    except Exception as e:

        return jsonify({"error": str(e)}), 500

 

@app.route('/logout', methods=['POST'])

def logout():

    try:

        # Check if the user is logged in

        if 'user_id' in session:

            # Remove user session information

            session.pop('user_id', None)
            session.pop('user_name', None)


            return jsonify({"message": "Logged out successfully"}), 200

        else:

            return jsonify({"message": "User is not logged in"}), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 500
 

 

 


 

 

 

@app.route('/cities', methods=['GET'])

def get_cities():

    cursor = mysql.cursor()

 

    cursor.execute('SELECT name FROM cities')

 

    cities = cursor.fetchall()

 

    cursor.close()

 

    city_list = [city[0] for city in cities]

   

    return jsonify({"cities": city_list}), 200

 

@app.route('/city/<city_name>', methods=['GET'])

def get_city_by_name(city_name):

    cursor = mysql.cursor()

 

    cursor.execute('SELECT name FROM cities WHERE LOWER(name) = LOWER(%s)', (city_name,))

 

    city = cursor.fetchone()

 

    cursor.close()

 

    if city:

        return jsonify({"city": city[0]}), 200

    else:

        return jsonify({"error": "City not found"}), 404
    

@app.route('/services/<string:city_name>', methods=['GET'])

def handle_services(city_name):

    try:

        cursor = mysql.cursor(dictionary=True)

        cursor.execute('SELECT s.services_id, s.name FROM services s JOIN cities c ON s.city_id = c.cities_id WHERE c.name = %s', (city_name,))

        services = cursor.fetchall()

        cursor.close()

 

        return jsonify({"services": services}), 200

 

    except Exception as e:

        return jsonify({"error": str(e)}), 500
 


@app.route('/subcategories/<int:service_id>', methods=['GET'])

def handle_subcategories(service_id):

    try:
          # Fetch subcategories using service_id
        cursor = mysql.cursor(dictionary=True)

        cursor.execute('SELECT * FROM subcategories WHERE service_id = %s', (service_id,))
        subcategories_list = cursor.fetchall()
        cursor.close()
        if subcategories_list:
            return jsonify({"subcategories": subcategories_list}), 200

        else:
            return jsonify({"message": "No subcategories found"}), 404

 

    except Exception as e:

        return jsonify({"error": str(e)}), 500
    


@app.route('/session', methods=['GET'])
def get_session_data():
    try:
        # Check if the user is logged in
        if 'user_id' in session:
            # Create a dictionary to store session data
            session_data = {
                'user_id': session['user_id'],
                'user_name': session.get('user_name', None),  # Handle the case where user_name may not exist
            }
            return jsonify(session_data), 200
        else:
            return jsonify({"message": "User is not logged in"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":

 

    app.run(debug=True)