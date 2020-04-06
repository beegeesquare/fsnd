import psycopg2

print("Hello world !")

print('test DBAP psycopg2')

# connect to the DBAPI pscyopg2
# This connects to the default user=postgres
conn = psycopg2.connect('dbname=example')
# Open the cursor to perform the database operations
cur = conn.cursor()
# drop any table if already exists
cur.execute('DROP TABLE IF EXISTS table2')
# """ is a multi line in python
cur.execute('''
    CREATE TABLE table2 (
    id INTEGER PRIMARY KEY,
    completed BOOLEAN NOT NULL DEFAULT False
    );
''')

cur.execute('''INSERT INTO table2 (id, completed) VALUES (1, true)''');
conn.commit()
cur.close()
conn.close()
print('test')
