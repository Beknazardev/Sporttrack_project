import psycopg

DB_NAME = "sporttrack"
DB_USER = "postgres"
DB_PASSWORD = "Postgres123"
DB_HOST = "localhost"
DB_PORT = 5432

print("DB_NAME:", repr(DB_NAME))
print("DB_USER:", repr(DB_USER))
print("DB_PASSWORD:", repr(DB_PASSWORD))
print("DB_HOST:", repr(DB_HOST))
print("DB_PORT:", repr(DB_PORT))

conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)

print("OK, connected")
conn.close()