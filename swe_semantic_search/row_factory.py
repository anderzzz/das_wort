"""Simple row factory for sqlite3."""


def dict_factory(cursor, row):
    """Convert the database row to a dictionary

    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
