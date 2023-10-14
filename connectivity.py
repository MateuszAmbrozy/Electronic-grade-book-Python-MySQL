import mysql.connector
connenction=mysql.connector.connect(user = "root",  password="password", host="localhost", database = 'python', auth_plugin='mysql_native_password')


cursor = connenction.cursor()

if connenction.is_connected():
    print("Successfully connected")




insertQuery = "INSERT INTO users(username, city) VALUES(%(username)s, %(city)s)"
insertData = {
    'username' : "Mariusz",
    'city' : "Warszawa"
}
cursor.execute(insertQuery, insertData)
connenction.commit()

query = 'SELECT id, username, city FROM users'
cursor.execute(query)
for(id, username, city) in cursor:
    print(f'{id} - {username} from {city}')

connenction.close()