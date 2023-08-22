import psycopg2
from decimal import Decimal
def db_connect():
    # Database connection details
    host = 'localhost'
    port = '9876'  # Default PostgreSQL port
    database = 'postgres'
    user = 'postgres'
    password = 'md-6613'

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            client_encoding = 'UTF8'
        )
        print('Connected to the database successfully!')
        cur = conn.cursor()
        name = 'မမ'
        age = 25
        cur.execute("INSERT INTO test (name,age) VALUES (%s,%s)",(name,age))
        conn.commit()
        return conn
    except psycopg2.Error as e:
        print('Error connecting to the database:', e)

db_connect()

# [('MDY - Nyaung Oo - Mya Kan Ta Man - Taung Pon Wa Chaung','SPD-23-24-002', 'U Win Aung', Decimal('1000.00'), Decimal('18386.00'), Decimal('9731.00'), Decimal('1448.00'), Decimal('1837.75'), Decimal('-389.75'), Decimal('3919.00'), Decimal('4215.72'), Decimal('-296.72'), Decimal('91313656.83'), Decimal('9731.00'), Decimal('8332.50'), Decimal('1398.50'), True)]
