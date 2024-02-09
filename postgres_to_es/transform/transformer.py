from collections import defaultdict

from models import FilmWork


class DataTransfromer:
    """
    Класс для трансформации данных в формат,
    необходимый для загрузки в Elasticsearch.
    """

    def __init__(self) -> None:
        self.collector = defaultdict(
            lambda: {
                "uuid": None,
                "title": None,
                "description": None,
                "imdb_rate": None,
                "p_info": set(),
                "genre_name": set(),
            },
        )

    def transform(self, filmworks: list[FilmWork]):
        """
        Запускает процесс трансформации данных.

        :param filmworks: необходимые для трансформирования данные о фильмах
        :return: подготовленные для загрузки в ES данные о фильмах
        """
        self._collect_data(filmworks)
        merged_filmworks = self._merge_data()
        return self._format_data(merged_filmworks)

    def _collect_data(
        self,
        filmworks: list[FilmWork],
    ):
        """
        Собирает данные в коллектор класса.

        :param filmworks: данные о фильмах
        """

        for filmwork in filmworks:
            uuid = filmwork.fw_id
            self.collector[uuid]["uuid"] = uuid
            self.collector[uuid]["title"] = filmwork.title
            self.collector[uuid]["description"] = filmwork.description
            self.collector[uuid]["imdb_rate"] = filmwork.rating
            self.collector[uuid]["p_info"].add(
                (
                    filmwork.role,
                    filmwork.full_name,
                    filmwork.id,
                ),
            )
            self.collector[uuid]["genre_name"].add(filmwork.name)

    def _merge_data(self) -> list[dict[str, None]]:
        """
        Преобразует собранные в коллектор данные в список.

        :param filmworks: данные о фильмах
        :return: смёрженный список с данными о фильмах
        """
        return [
            {
                "uuid": filmwork.get("uuid"),
                "title": filmwork.get("title"),
                "description": filmwork.get("description"),
                "imdb_rate": filmwork.get("imdb_rate"),
                "p_info": tuple(filmwork.get("p_info")),
                "genre_name": tuple(filmwork.get("genre_name")),
            }
            for filmwork in self.collector.values()
        ]

    def _format_data(
        self, merged_filmworks: list[dict[str, None]],
    ) -> list[dict[str, None]]:
        """
        Трансформирует смёрженные данные в формат,
        необходимый для загрузки в индекс

        :param merged_filmworks: смёрженный список с данными о фильмах
        :return: подготовленные для загрузки в ES данные о фильмах
        """

        transformed_data = []
        for filmwork in merged_filmworks:
            es_index = {
                "index": {
                    "_index": "movies",
                    "_id": filmwork["uuid"],
                },
            }

            persons_info = {
                "actor": None,
                "writer": None,
            }
            for role in persons_info:
                names = [
                    p_info[1]
                    for p_info in filmwork.get("p_info")
                    if p_info[0] == role
                ]
                objects = [
                    {"id": p_info[2], "name": p_info[1]}
                    for p_info in filmwork["p_info"]
                    if p_info[0] == role
                ]
                persons_info[role] = [names, objects]

            director= next(
                    (
                        p_info[1]
                        for p_info in filmwork["p_info"]
                        if p_info[0] == "director"
                    ),
                    "",
                )

            transformed_filmwork = {
                "id": filmwork["uuid"],
                "imdb_rating": filmwork["imdb_rate"],
                "genre": list(filmwork["genre_name"]),
                "title": filmwork["title"],
                "description": filmwork["description"],
                "director": director,
                "actors_names": persons_info["actor"][0],
                "writers_names": persons_info["writer"][0],
                "actors": persons_info["actor"][1],
                "writers": persons_info["writer"][1],
            }
            transformed_data.extend([es_index, transformed_filmwork])
        return transformed_data
