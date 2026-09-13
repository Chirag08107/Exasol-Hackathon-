from database.exasol import get_connection

connection = get_connection()

print("Connected to Exasol successfully!")

stmt = connection.execute("SELECT 1")

print("SELECT 1 result:")
print(stmt.fetchall())

stmt = connection.execute("""
    SELECT COUNT(*) AS form_count
    FROM FORM_KB.FORM
""")

print("FORM count:")
print(stmt.fetchall())

connection.close()

print("Connection closed.")