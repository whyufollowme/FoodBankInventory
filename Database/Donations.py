from Database.Database import get_connection


# ============================================================
# DONORS
# ============================================================

def add_donor(
    name,
    contact_name=None,
    phone=None,
    email=None,
    notes=None,
):
    """Add a new donor."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO donors (
                name,
                contact_name,
                phone,
                email,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                contact_name,
                phone,
                email,
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


def get_donor(donor_id):
    """Get a donor by database ID."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT *
            FROM donors
            WHERE id = ?
            """,
            (donor_id,),
        ).fetchone()

    finally:
        connection.close()


def search_donors(search_term):
    """Search donors by name, contact name, phone, or email."""

    connection = get_connection()

    try:
        search = f"%{search_term}%"

        return connection.execute(
            """
            SELECT *
            FROM donors
            WHERE active = 1
              AND (
                    name LIKE ?
                    OR contact_name LIKE ?
                    OR phone LIKE ?
                    OR email LIKE ?
                  )
            ORDER BY name
            """,
            (
                search,
                search,
                search,
                search,
            ),
        ).fetchall()

    finally:
        connection.close()


def get_all_donors():
    """Return all active donors."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT *
            FROM donors
            WHERE active = 1
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()


# ============================================================
# DONATIONS
# ============================================================

def create_donation(
    donor_id=None,
    donation_date=None,
    notes=None,
):
    """Create a new donation."""

    connection = get_connection()

    try:
        if donation_date is None:
            cursor = connection.execute(
                """
                INSERT INTO donations (
                    donor_id,
                    notes
                )
                VALUES (?, ?)
                """,
                (
                    donor_id,
                    notes,
                ),
            )

        else:
            cursor = connection.execute(
                """
                INSERT INTO donations (
                    donor_id,
                    donation_date,
                    notes
                )
                VALUES (?, ?, ?)
                """,
                (
                    donor_id,
                    donation_date,
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


def add_donation_item(
    donation_id,
    item_id,
    quantity,
    expiry_date=None,
    storage_location=None,
):
    """Add an item to a donation."""

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO donation_items (
                donation_id,
                item_id,
                quantity,
                expiry_date,
                storage_location
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                donation_id,
                item_id,
                quantity,
                expiry_date,
                storage_location,
            ),
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_donation(donation_id):
    """Get a donation and donor information."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                donations.*,
                donors.name AS donor_name
            FROM donations
            LEFT JOIN donors
                ON donations.donor_id = donors.id
            WHERE donations.id = ?
            """,
            (donation_id,),
        ).fetchone()

    finally:
        connection.close()


def get_donation_items(donation_id):
    """Get all items belonging to a donation."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                donation_items.*,
                items.name AS item_name,
                items.barcode,
                items.unit
            FROM donation_items
            JOIN items
                ON donation_items.item_id = items.id
            WHERE donation_items.donation_id = ?
            ORDER BY items.name
            """,
            (donation_id,),
        ).fetchall()

    finally:
        connection.close()


def complete_donation(donation_id):
    """
    Complete a donation and add all of its items
    to inventory.

    The entire operation happens inside one transaction.
    """

    connection = get_connection()

    try:
        # Make sure the donation exists
        donation = connection.execute(
            """
            SELECT *
            FROM donations
            WHERE id = ?
            """,
            (donation_id,),
        ).fetchone()

        if donation is None:
            raise ValueError("Donation does not exist.")

        # Get all donation items
        donation_items = connection.execute(
            """
            SELECT *
            FROM donation_items
            WHERE donation_id = ?
            """,
            (donation_id,),
        ).fetchall()

        if not donation_items:
            raise ValueError(
                "Cannot complete a donation with no items."
            )

        # Add every donation item to inventory
        for item in donation_items:

            connection.execute(
                """
                INSERT INTO inventory (
                    item_id,
                    quantity,
                    expiry_date,
                    storage_location
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    item["item_id"],
                    item["quantity"],
                    item["expiry_date"],
                    item["storage_location"],
                ),
            )

        connection.commit()

        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()