from Database.Database import get_connection


# ============================================================
# DISTRIBUTIONS
# ============================================================

def create_distribution(client_id, notes=None):
    """
    Create a new food distribution for a client.

    Returns:
        The new distribution ID.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO distributions (
                client_id,
                notes
            )
            VALUES (?, ?)
            """,
            (
                client_id,
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


def get_distribution(distribution_id):
    """
    Get a single distribution with client information.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distributions.*,

                clients.client_number,
                clients.first_name,
                clients.last_name

            FROM distributions

            JOIN clients
                ON distributions.client_id = clients.id

            WHERE distributions.id = ?
            """,
            (distribution_id,),
        ).fetchone()

    finally:
        connection.close()


def get_all_distributions():
    """
    Get all distributions with client information.

    Most recent distributions are returned first.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distributions.*,

                clients.client_number,
                clients.first_name,
                clients.last_name

            FROM distributions

            JOIN clients
                ON distributions.client_id = clients.id

            ORDER BY
                distributions.distribution_date DESC,
                distributions.id DESC
            """
        ).fetchall()

    finally:
        connection.close()


# ============================================================
# CLIENT DISTRIBUTION HISTORY
# ============================================================

def get_client_distribution_history(client_id):
    """
    Get the complete food distribution history for a client.

    Each row contains:
        - Distribution information
        - Food item information
        - Quantity given

    Results are ordered with the newest visit first.

    This is used by the Staff History window.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distributions.id AS distribution_id,
                distributions.client_id,
                distributions.distribution_date,
                distributions.notes,

                distribution_items.id AS distribution_item_id,
                distribution_items.item_id,
                distribution_items.quantity,

                items.name AS item_name,
                items.barcode,
                items.unit

            FROM distributions

            JOIN distribution_items
                ON distributions.id =
                   distribution_items.distribution_id

            JOIN items
                ON distribution_items.item_id =
                   items.id

            WHERE distributions.client_id = ?

            ORDER BY
                distributions.distribution_date DESC,
                distributions.id DESC,
                items.name ASC
            """,
            (client_id,),
        ).fetchall()

    finally:
        connection.close()


def get_client_distribution_summary(client_id):
    """
    Get a summary of every distribution/visit for a client.

    Returns one row per visit.

    Each row includes:
        - Distribution ID
        - Client ID
        - Visit/distribution date
        - Notes
        - Number of different item types
        - Total quantity distributed

    Results are ordered newest first.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distributions.id AS distribution_id,
                distributions.client_id,
                distributions.distribution_date,
                distributions.notes,

                COUNT(distribution_items.id)
                    AS item_types,

                COALESCE(
                    SUM(distribution_items.quantity),
                    0
                ) AS total_quantity

            FROM distributions

            LEFT JOIN distribution_items
                ON distributions.id =
                   distribution_items.distribution_id

            WHERE distributions.client_id = ?

            GROUP BY
                distributions.id,
                distributions.client_id,
                distributions.distribution_date,
                distributions.notes

            ORDER BY
                distributions.distribution_date DESC,
                distributions.id DESC
            """,
            (client_id,),
        ).fetchall()

    finally:
        connection.close()


def get_client_latest_distribution(client_id):
    """
    Get the client's most recent food distribution.

    This is intended for the Client History view when displaying
    the client's latest visit prominently.

    Returns:
        One row containing:
            - distribution_id
            - client_id
            - distribution_date
            - notes
            - item_types
            - total_quantity

        Returns None if the client has never received a distribution.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distributions.id AS distribution_id,
                distributions.client_id,
                distributions.distribution_date,
                distributions.notes,

                COUNT(distribution_items.id)
                    AS item_types,

                COALESCE(
                    SUM(distribution_items.quantity),
                    0
                ) AS total_quantity

            FROM distributions

            LEFT JOIN distribution_items
                ON distributions.id =
                   distribution_items.distribution_id

            WHERE distributions.client_id = ?

            GROUP BY
                distributions.id,
                distributions.client_id,
                distributions.distribution_date,
                distributions.notes

            ORDER BY
                distributions.distribution_date DESC,
                distributions.id DESC

            LIMIT 1
            """,
            (client_id,),
        ).fetchone()

    finally:
        connection.close()


def get_client_last_distribution_date(client_id):
    """
    Get only the date of the client's most recent distribution.

    Returns:
        The latest distribution date, or None if the client has
        never received food.
    """

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT
                distribution_date

            FROM distributions

            WHERE client_id = ?

            ORDER BY
                distribution_date DESC,
                id DESC

            LIMIT 1
            """,
            (client_id,),
        ).fetchone()

        if result:
            return result["distribution_date"]

        return None

    finally:
        connection.close()


# ============================================================
# DISTRIBUTION ITEMS
# ============================================================

def add_distribution_item(
    distribution_id,
    item_id,
    quantity,
):
    """
    Add a food item to a distribution.

    This does NOT remove inventory.

    Inventory removal should happen through remove_stock()
    or create_complete_distribution() when the distribution
    is completed.
    """

    if quantity <= 0:
        raise ValueError(
            "Quantity must be greater than zero."
        )

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO distribution_items (
                distribution_id,
                item_id,
                quantity
            )
            VALUES (?, ?, ?)
            """,
            (
                distribution_id,
                item_id,
                quantity,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_distribution_items(distribution_id):
    """
    Get all food items included in a distribution.

    This is used when viewing the exact food given during
    a particular client visit.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distribution_items.*,

                items.name AS item_name,
                items.barcode,
                items.unit

            FROM distribution_items

            JOIN items
                ON distribution_items.item_id =
                   items.id

            WHERE distribution_items.distribution_id = ?

            ORDER BY
                items.name ASC
            """,
            (distribution_id,),
        ).fetchall()

    finally:
        connection.close()


# ============================================================
# GET EXACT FOOD GIVEN ON A CLIENT VISIT
# ============================================================

def get_client_distribution_items(
    client_id,
    distribution_id,
):
    """
    Get the exact food given to a client during a specific visit.

    The distribution must belong to the supplied client.

    This provides an additional safety check so that a distribution
    belonging to another client cannot accidentally be displayed.

    Returns:
        All food items from that distribution.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                distribution_items.id AS distribution_item_id,
                distribution_items.distribution_id,
                distribution_items.item_id,
                distribution_items.quantity,

                items.name AS item_name,
                items.barcode,
                items.unit

            FROM distribution_items

            JOIN distributions
                ON distribution_items.distribution_id =
                   distributions.id

            JOIN items
                ON distribution_items.item_id =
                   items.id

            WHERE distributions.client_id = ?
              AND distributions.id = ?

            ORDER BY
                items.name ASC
            """,
            (
                client_id,
                distribution_id,
            ),
        ).fetchall()

    finally:
        connection.close()


# ============================================================
# COMPLETE DISTRIBUTION
# ============================================================

def create_complete_distribution(
    client_id,
    items,
    notes=None,
):
    """
    Create a complete food distribution.

    `items` should be a list of dictionaries:

        [
            {
                "item_id": 5,
                "quantity": 2
            },
            {
                "item_id": 8,
                "quantity": 1
            }
        ]

    Inventory is removed using FEFO
    (First Expiring, First Out).

    The entire operation occurs inside one database transaction.

    If anything fails, the distribution and inventory changes
    are rolled back.

    Returns:
        distribution_id
    """

    if not items:
        raise ValueError(
            "A distribution must contain at least one item."
        )

    connection = get_connection()

    try:

        # ----------------------------------------------------
        # Create distribution
        # ----------------------------------------------------

        cursor = connection.execute(
            """
            INSERT INTO distributions (
                client_id,
                notes
            )
            VALUES (?, ?)
            """,
            (
                client_id,
                notes,
            ),
        )

        distribution_id = cursor.lastrowid

        # ----------------------------------------------------
        # Add each item
        # ----------------------------------------------------

        for item in items:

            item_id = item["item_id"]
            quantity = item["quantity"]

            if quantity <= 0:
                raise ValueError(
                    "Distribution quantities must be greater than zero."
                )

            # ------------------------------------------------
            # Check stock
            # ------------------------------------------------

            result = connection.execute(
                """
                SELECT
                    COALESCE(
                        SUM(quantity),
                        0
                    ) AS total

                FROM inventory

                WHERE item_id = ?
                """,
                (item_id,),
            ).fetchone()

            available = result["total"]

            if available < quantity:

                item_info = connection.execute(
                    """
                    SELECT
                        name,
                        unit

                    FROM items

                    WHERE id = ?
                    """,
                    (item_id,),
                ).fetchone()

                item_name = (
                    item_info["name"]
                    if item_info
                    else f"Item #{item_id}"
                )

                raise ValueError(
                    f"Not enough stock for {item_name}.\n\n"
                    f"Requested: {quantity}\n"
                    f"Available: {available}"
                )

            # ------------------------------------------------
            # Add distribution record
            # ------------------------------------------------

            connection.execute(
                """
                INSERT INTO distribution_items (
                    distribution_id,
                    item_id,
                    quantity
                )
                VALUES (?, ?, ?)
                """,
                (
                    distribution_id,
                    item_id,
                    quantity,
                ),
            )

            # ------------------------------------------------
            # Remove inventory using FEFO
            # ------------------------------------------------

            remaining = quantity

            batches = connection.execute(
                """
                SELECT *
                FROM inventory

                WHERE item_id = ?
                  AND quantity > 0

                ORDER BY

                    CASE
                        WHEN expiry_date IS NULL THEN 1
                        ELSE 0
                    END,

                    expiry_date,
                    id
                """,
                (item_id,),
            ).fetchall()

            for batch in batches:

                if remaining <= 0:
                    break

                amount = min(
                    batch["quantity"],
                    remaining,
                )

                new_quantity = (
                    batch["quantity"] - amount
                )

                connection.execute(
                    """
                    UPDATE inventory

                    SET
                        quantity = ?,
                        updated_at = CURRENT_TIMESTAMP

                    WHERE id = ?
                    """,
                    (
                        new_quantity,
                        batch["id"],
                    ),
                )

                remaining -= amount

        connection.commit()

        return distribution_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# DELETE / VOID DISTRIBUTION
# ============================================================

def delete_distribution(distribution_id):
    """
    Delete a distribution record.

    WARNING:
    This does NOT restore inventory.

    Use this only for correcting an accidental/empty
    distribution record.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM distributions
            WHERE id = ?
            """,
            (distribution_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# STATISTICS
# ============================================================

def get_client_distribution_count(client_id):
    """
    Return the number of times a client has received food.
    """

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT
                COUNT(*) AS total

            FROM distributions

            WHERE client_id = ?
            """,
            (client_id,),
        ).fetchone()

        return result["total"]

    finally:
        connection.close()


def get_distribution_item_count(distribution_id):
    """
    Return the number of different food items in a distribution.
    """

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT
                COUNT(*) AS total

            FROM distribution_items

            WHERE distribution_id = ?
            """,
            (distribution_id,),
        ).fetchone()

        return result["total"]

    finally:
        connection.close()