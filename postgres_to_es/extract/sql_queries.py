MODIFIED_OBJECTS_SQL = """
    SELECT id, modified
    FROM content.{table_name}
    WHERE modified > '{modified}'
    ORDER BY modified
    LIMIT {batch_size};
"""

FILMWORK_IDS_BY_RELATED_MODIFIED_SQL = """
    SELECT fw.id
    FROM content.film_work fw
    LEFT JOIN content.{table_name}_film_work tfw ON tfw.film_work_id = fw.id
    WHERE tfw.{table_name}_id IN {modified_ids}
    ORDER BY fw.modified;
"""


FILMWORK_BY_IDS_SQL = """
    SELECT
        fw.id as fw_id,
        fw.title,
        fw.description,
        fw.rating,
        pfw.role,
        p.full_name,
        p.id,
        g.name
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.id IN {filmworks_ids};
"""
