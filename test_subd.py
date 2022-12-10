import psycopg2


def execute_query(conn, query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
        print("Query executed successfully")
    except Exception as e:
        print(f"The error '{e}' occurred")


def execute_read_query(conn, query):
    cur = conn.cursor()
    res = None
    try:
        cur.execute(query)
        res = cur.fetchall()
        print("Query executed successfully")
        return res
    except Exception as e:
        print(f"The error '{e}' occurred")


def create_db(conn):
    create_client_table = """
    CREATE TABLE IF NOT EXISTS client (
        id SERIAL PRIMARY KEY,
        firstname VARCHAR(60) NOT NULL,
        lastname VARCHAR(60) NOT NULL,
        email TEXT UNIQUE NOT NULL
    );
    """
    create_phone_table = """
    CREATE TABLE IF NOT EXISTS phone (
        id SERIAL PRIMARY KEY,
        phone_number VARCHAR(40) NOT NULL,
        client_id INTEGER REFERENCES client(id)
    );
    """

    execute_query(conn, create_client_table)
    execute_query(conn, create_phone_table)


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO client (firstname, lastname, email) VALUES {first_name, last_name, email};"
        )
        res = find_client_id(conn, email=email)
        lst = str(phones)
        if phones:
            for i in range(len(lst.split())):
                cur.execute(
                    f"INSERT INTO phone (phone_number, client_id) VALUES {phones[i], res[0]}"
                )
        conn.commit()


def add_phone(conn, client_id, phone):
    add_phone_client = (
        f"INSERT INTO phone (phone_number, client_id) VALUES {phone, client_id}"
    )
    execute_query(conn, add_phone_client)


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                UPDATE client SET firstname=%s WHERE id=%s;
            """, (first_name, client_id,))

        if last_name:
            cur.execute("""
                UPDATE client SET lastname=%s WHERE id=%s;
            """, (last_name, client_id,))

        if email:
            cur.execute("""
                UPDATE client SET email=%s WHERE id=%s;
            """, (email, client_id,))

        if phones:
            cur.execute(
                f"SELECT COUNT(id) FROM phone WHERE client_id={client_id}"
            )
            res = cur.fetchone()
            lst = str(phones)
            if res[0] == 0:
                if len(lst.split()) > 1:
                    for i in range(len(lst.split())):
                        add_phone(conn, client_id, phones[i])
                else:
                    add_phone(conn, client_id, phones)
            elif res[0] >= 1:
                if len(lst.split()) == 1:
                    cur.execute(
                        f"UPDATE phone SET phone_number={phones} WHERE client_id={client_id}"
                    )
                else:
                    cur.execute(
                        f"DELETE FROM phone WHERE client_id={client_id}"
                    )
                    for i in range(len(lst.split())):
                        add_phone(conn, client_id, phones[i])


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone WHERE client_id=%s AND phone_number=%s;
        """, (client_id, phone,))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone WHERE client_id=%s;
        """, (client_id,))
        conn.commit()
        cur.execute("""
            DELETE FROM client WHERE id=%s;
        """, (client_id,))


def find_client_id(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                SELECT id FROM client WHERE firstname=%s;
            """, (first_name,))
            res = cur.fetchone()
            return res[0]

        if last_name:
            cur.execute("""
                SELECT id FROM client WHERE lastname=%s;
            """, (last_name,))
            res = cur.fetchone()
            return res[0]

        if email:
            cur.execute("""
                SELECT id FROM client WHERE email=%s;
            """, (email,))
            res = cur.fetchone()
            return res[0]

        if phone:
            cur.execute(
                """SELECT client_id FROM phone WHERE phone_number=%s;
            """, (phone,))
            res = cur.fetchone()
            return res[0]


with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as connection:
    # change_client(connection, 94, phones=('000111', '111000', '111111'))
    # change_client(connection, 95, email='BigFoot@mail.com')
    # add_client(connection, "Fred", "Olfsonson", "Freddy@miel.com", phones=('12345678', '7861251'))
    # add_client(connection, "Fred", "Olfsonson", "Freddy@miel.com", phones='7861251')
    # add_client(connection, "Fred", "Olfsonson", "Freddy@miel.com")
    create_db(connection)
    # delete_client(connection, 7)
    # res = find_client_id(connection, 'alfi')
    # print(res)
    # add_phone(connection, 9, '12345678')
    # add_phone(connection, 9, '87654321')
    # print(find_client_id(connection, first_name='BigFoot'))
    # delete_phone(connection, 9, '87654321')
    # delete_client(connection, 94)

connection.close()