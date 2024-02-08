from collections import defaultdict


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

    def transform(self, filmworks: list[dict[str, None]]):
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
        filmworks: list[dict[str, None]],
    ):
        """
        Собирает данные в коллектор класса.

        :param filmworks: данные о фильмах
        """

        for filmwork in filmworks:
            uuid = filmwork[0]
            self.collector[uuid]["uuid"] = uuid
            self.collector[uuid]["title"] = filmwork[1]
            self.collector[uuid]["description"] = filmwork[2]
            self.collector[uuid]["imdb_rate"] = filmwork[3]
            self.collector[uuid]["p_info"].add(
                (
                    filmwork[4],
                    filmwork[5],
                    filmwork[6],
                ),
            )
            self.collector[uuid]["genre_name"].add(filmwork[7])

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
