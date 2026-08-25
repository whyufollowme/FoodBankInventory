from Database.Database import get_connection


def add_client(
    client_number,
    first_name,
    last_name,
    phone=None,
    email=None,
    household_size=1,
    adults=1,
    children=0,
    notes=None,
):
    """Add a new client to the database."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO clients (
                client_number,
                first_name,
                last_name,
                phone,
                email,
                household_size,
                adults,
                children,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client_number,
                first_name,
                last_name,
                phone,
                email,
                household_size,
                adults,
                children,
                notes,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_client(client_id):
    """Get a client using their database ID."""

    connection = get_connection()

    try:
        client = connection.execute(
            """
            SELECT *
            FROM clients
            WHERE id = ?
            """,
            (client_id,),
        ).fetchone()

        return client

    finally:
        connection.close()


def get_client_by_number(client_number):
    """Find a client using their client number."""

    connection = get_connection()

    try:
        client = connection.execute(
            """
            SELECT *
            FROM clients
            WHERE client_number = ?
            """,
            (client_number,),
        ).fetchone()

        return client

    finally:
        connection.close()


def search_clients(search_term):
    """Search clients by number, first name, or last name."""

    connection = get_connection()

    try:
        search = f"%{search_term}%"

        clients = connection.execute(
            """
            SELECT *
            FROM clients
            WHERE active = 1
              AND (
                    client_number LIKE ?
                    OR first_name LIKE ?
                    OR last_name LIKE ?
                  )
            ORDER BY last_name, first_name
            """,
            (search, search, search),
        ).fetchall()

        return clients

    finally:
        connection.close()


def get_all_clients(include_inactive=False):
    """Return all clients."""

    connection = get_connection()

    try:
        if include_inactive:
            clients = connection.execute(
                """
                SELECT *
                FROM clients
                ORDER BY last_name, first_name
                """
            ).fetchall()

        else:
            clients = connection.execute(
                """
                SELECT *
                FROM clients
                WHERE active = 1
                ORDER BY last_name, first_name
                """
            ).fetchall()

        return clients

    finally:
        connection.close()


def update_client(
    client_id,
    first_name,
    last_name,
    phone=None,
    email=None,
    household_size=1,
    adults=1,
    children=0,
    notes=None,
):
    """Update an existing client's information."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE clients
            SET
                first_name = ?,
                last_name = ?,
                phone = ?,
                email = ?,
                household_size = ?,
                adults = ?,
                children = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                first_name,
                last_name,
                phone,
                email,
                household_size,
                adults,
                children,
                notes,
                client_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def deactivate_client(client_id):
    """Deactivate a client without deleting their history."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE clients
            SET
                active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (client_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def reactivate_client(client_id):
    """Reactivate a previously deactivated client."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE clients
            SET
                active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (client_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()