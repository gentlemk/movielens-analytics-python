from movielens_impl.links import Links
import pytest
import requests


def test_load_links(tmp_path):
    file_path = tmp_path / "links.csv"
    file_path.write_text(
        "movieId,imdbId,tmdbId\n"
        "1,0114709,862\n"
        "2,0113497,\n"
        "3,0113228,15602\n",
        encoding="utf-8"
    )

    links = Links(str(file_path))

    assert links.links == {
        1: 862,
        3: 15602
    }


def test_load_links_header_only(tmp_path):
    file_path = tmp_path / "links.csv"
    file_path.write_text(
        "movieId,imdbId,tmdbId\n",
        encoding="utf-8"
    )

    links = Links(str(file_path))

    assert links.links == {}


def test_load_links_empty_file(tmp_path):
    file_path = tmp_path / "links.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(StopIteration):
        Links(str(file_path))


def test_load_links_empty_file(tmp_path):
    file_path = tmp_path / "empty_links.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV is empty or missing header"):
        Links(str(file_path))


def test_get_imdb_success(monkeypatch):
    links = Links()
    links.links = {1: 862}

    html = """
    <section class="header poster">
        <div class="title">
            <h2>
                <a>Toy Story</a>
                <span class="tag release_date">(1995)</span>
            </h2>
        </div>
    </section>

    <section class="facts left_column">
        <p><strong><bdi>Budget</bdi></strong> $30,000,000</p>
        <p><strong><bdi>Revenue</bdi></strong> $401,157,969</p>
    </section>

    <div class="facts">
        <span class="runtime">1h 21m</span>
    </div>

    <div class="header_info">
        <ol class="people no_image">
            <li class="profile">
                <p><a>John Lasseter</a></p>
                <p class="character">Director</p>
            </li>
            <li class="profile">
                <p><a>Alec Sokolow</a></p>
                <p class="character">Screenplay</p>
            </li>
        </ol>
    </div>
    """

    class MockResponse:
        text = html

        def raise_for_status(self):
            pass

    def mock_get(url, timeout):
        assert url == "https://www.themoviedb.org/movie/862"
        assert timeout == 10
        return MockResponse()

    monkeypatch.setattr("movielens_impl.links.requests.get", mock_get)

    result = links.get_imdb(
        [1],
        ["Title", "Director", "Budget",
         "Cumulative Worldwide Gross", "Runtime"]
    )

    assert result == [
        [1, "Toy Story", "John Lasseter", "Budget $30,000,000",
         "Revenue $401,157,969", "1h 21m"]
    ]


def test_get_imdb_request_error(monkeypatch):
    links = Links()
    links.links = {1: 862}

    def mock_get(url, timeout):
        raise requests.RequestException("Connection error")

    monkeypatch.setattr("movielens_impl.links.requests.get", mock_get)

    result = links.get_imdb([1], ["Title", "Director"])

    assert result == []


def test_get_imdb_missing_fields(monkeypatch):
    links = Links()
    links.links = {1: 862}

    html = """
    <div class="title">
        <a>Toy Story</a>
    </div>
    <span class="runtime">1h 21m</span>
    """

    class MockResponse:
        text = html

        def raise_for_status(self):
            pass

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr("movielens_impl.links.requests.get", mock_get)

    result = links.get_imdb(
        [1],
        ["Title", "Director", "Budget",
         "Cumulative Worldwide Gross", "Runtime"]
    )

    assert result == [[1, "Toy Story", None, None, None, "1h 21m"]]


def test_get_imdb_sorting(monkeypatch):
    links = Links()
    links.links = {1: 862, 2: 8844}

    html_by_id = {
        862: '<div class="title"><a>Toy Story</a></div>',
        8844: '<div class="title"><a>Jumanji</a></div>'
    }

    class MockResponse:
        def __init__(self, html):
            self.text = html

        def raise_for_status(self):
            pass

    def mock_get(url, timeout):
        tmdb_id = int(url.rsplit("/", 1)[-1])
        return MockResponse(html_by_id[tmdb_id])

    monkeypatch.setattr("movielens_impl.links.requests.get", mock_get)

    result = links.get_imdb([1, 2], ["Title"])

    assert result == [
        [2, "Jumanji"],
        [1, "Toy Story"]
    ]


def test_top_directors():
    links = Links()
    links.last_fields = ["Title", "Director"]
    links.imdb_info = [
        [1, "Toy Story", "John Lasseter"],
        [2, "Jumanji", "Joe Johnston"],
        [3, "Cars", "John Lasseter"],
        [4, "A Bug's Life", "John Lasseter"],
        [5, "The Rock", "Michael Bay"]
    ]

    result = links.top_directors(2)

    assert result == {
        "John Lasseter": 3,
        "Joe Johnston": 1
    }


def test_top_directors_skip_missing():
    links = Links()
    links.last_fields = ["Title", "Director"]
    links.imdb_info = [
        [1, "Toy Story", "John Lasseter"],
        [2, "Unknown Movie", None],
        [3, "Cars", "John Lasseter"],
        [4, "Jumanji", "Joe Johnston"]
    ]

    result = links.top_directors(3)

    assert result == {
        "John Lasseter": 2,
        "Joe Johnston": 1
    }


def test_top_directors_more_than_available():
    links = Links()
    links.last_fields = ["Title", "Director"]
    links.imdb_info = [
        [1, "Toy Story", "John Lasseter"],
        [2, "Jumanji", "Joe Johnston"]
    ]

    result = links.top_directors(10)

    assert result == {
        "John Lasseter": 1,
        "Joe Johnston": 1
    }


def test_top_directors_negative_n():
    links = Links()
    links.last_fields = ["Title", "Director"]
    links.imdb_info = [[1, "Toy Story", "John Lasseter"]]

    with pytest.raises(ValueError):
        links.top_directors(-1)


def test_most_expensive():
    links = Links()
    links.last_fields = ["Title", "Budget"]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000"],
        [2, "Jumanji", "$65,000,000"],
        [3, "The Rock", "$75,000,000"],
        [4, "Cars", "$120,000,000"]
    ]

    result = links.most_expensive(2)

    assert result == {
        "Cars": 120000000,
        "The Rock": 75000000
    }


def test_most_expensive_skip_missing():
    links = Links()
    links.last_fields = ["Title", "Budget"]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000"],
        [2, "Jumanji", None],
        [3, None, "$75,000,000"],
        [4, "Cars", "$120,000,000"]
    ]

    result = links.most_expensive(3)

    assert result == {
        "Cars": 120000000,
        "Toy Story": 30000000
    }


def test_most_expensive_negative_n():
    links = Links()
    links.last_fields = ["Title", "Budget"]
    links.imdb_info = [[1, "Toy Story", "$30,000,000"]]

    with pytest.raises(ValueError):
        links.most_expensive(-1)


def test_most_profitable():
    links = Links()
    links.last_fields = [
        "Title", "Budget", "Cumulative Worldwide Gross"
    ]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "$401,157,969"],
        [2, "Jumanji", "$65,000,000", "$262,821,940"],
        [3, "The Rock", "$75,000,000", "$335,062,621"],
        [4, "Cars", "$120,000,000", "$462,216,280"]
    ]

    result = links.most_profitable(2)

    assert result == {
        "Toy Story": 371157969,
        "Cars": 342216280
    }


def test_most_profitable_skip_missing():
    links = Links()
    links.last_fields = [
        "Title", "Budget", "Cumulative Worldwide Gross"
    ]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "$401,157,969"],
        [2, "Jumanji", None, "$262,821,940"],
        [3, "The Rock", "$75,000,000", None],
        [4, None, "$120,000,000", "$462,216,280"]
    ]

    result = links.most_profitable(3)

    assert result == {
        "Toy Story": 371157969
    }


def test_most_profitable_more_than_available():
    links = Links()
    links.last_fields = [
        "Title", "Budget", "Cumulative Worldwide Gross"
    ]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "$401,157,969"],
        [2, "Jumanji", "$65,000,000", "$262,821,940"]
    ]

    result = links.most_profitable(10)

    assert result == {
        "Toy Story": 371157969,
        "Jumanji": 197821940
    }


def test_most_profitable_negative_n():
    links = Links()
    links.last_fields = [
        "Title", "Budget", "Cumulative Worldwide Gross"
    ]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "$401,157,969"]
    ]

    with pytest.raises(ValueError):
        links.most_profitable(-1)


def test_longest():
    links = Links()
    links.last_fields = ["Title", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "1h 21m"],
        [2, "Jumanji", "1h 44m"],
        [3, "The Rock", "2h 16m"],
        [4, "Cars", "1h 57m"]
    ]

    result = links.longest(2)

    assert result == {
        "The Rock": 136,
        "Cars": 117
    }


def test_longest_skip_missing():
    links = Links()
    links.last_fields = ["Title", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "1h 21m"],
        [2, "Jumanji", None],
        [3, None, "2h 16m"],
        [4, "Cars", "Unknown"]
    ]

    result = links.longest(3)

    assert result == {
        "Toy Story": 81
    }


def test_longest_more_than_available():
    links = Links()
    links.last_fields = ["Title", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "1h 21m"],
        [2, "Jumanji", "1h 44m"]
    ]

    result = links.longest(10)

    assert result == {
        "Jumanji": 104,
        "Toy Story": 81
    }


def test_longest_negative_n():
    links = Links()
    links.last_fields = ["Title", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "1h 21m"]
    ]

    with pytest.raises(ValueError):
        links.longest(-1)


def test_top_cost_per_minute():
    links = Links()
    links.last_fields = ["Title", "Budget", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "1h 30m"],
        [2, "Jumanji", "$65,000,000", "1h 40m"],
        [3, "The Rock", "$75,000,000", "2h 00m"],
        [4, "Cars", "$120,000,000", "2h 00m"]
    ]

    result = links.top_cost_per_minute(2)

    assert result == {
        "Cars": 1000000.0,
        "Jumanji": 650000.0
    }


def test_top_cost_per_minute_skip_missing():
    links = Links()
    links.last_fields = ["Title", "Budget", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "1h 30m"],
        [2, "Jumanji", None, "1h 40m"],
        [3, "The Rock", "$75,000,000", None],
        [4, None, "$120,000,000", "2h 00m"],
        [5, "Cars", "$120,000,000", "Unknown"]
    ]

    result = links.top_cost_per_minute(5)

    assert result == {
        "Toy Story": 333333.33
    }


def test_top_cost_per_minute_negative_n():
    links = Links()
    links.last_fields = ["Title", "Budget", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "1h 30m"]
    ]

    with pytest.raises(ValueError):
        links.top_cost_per_minute(-1)


def test_top_cost_per_minute_zero_runtime():
    links = Links()
    links.last_fields = ["Title", "Budget", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "$30,000,000", "0h 0m"],
        [2, "Jumanji", "$65,000,000", "1h 40m"]
    ]

    result = links.top_cost_per_minute(2)

    assert result == {
        "Jumanji": 650000.0
    }


def test_longest_by_director():
    links = Links()
    links.last_fields = ["Title", "Director", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "John Lasseter", "1h 30m"],
        [2, "Jumanji", "Joe Johnston", "2h 00m"],
        [3, "Cars", "John Lasseter", "1h 40m"],
        [4, "A Bug's Life", "John Lasseter", "1h 20m"],
        [5, "The Rock", "Michael Bay", "2h 10m"]
    ]

    result = links.longest_by_director()

    assert result == {
        "John Lasseter": 270,
        "Michael Bay": 130,
        "Joe Johnston": 120
    }


def test_longest_by_director_skip_missing():
    links = Links()
    links.last_fields = ["Title", "Director", "Runtime"]
    links.imdb_info = [
        [1, "Toy Story", "John Lasseter", "1h 30m"],
        [2, None, "Joe Johnston", "2h 00m"],
        [3, "Cars", "John Lasseter", None],
        [4, "Jumanji", "Joe Johnston", "Unknown"],
        [5, "The Rock", "Michael Bay", "2h 10m"]
    ]

    result = links.longest_by_director()

    assert result == {
        "Michael Bay": 130,
        "John Lasseter": 90
    }


def test_get_imdb_types(monkeypatch):
    links = Links()
    links.links = {1: 862}

    html = """
    <div class="title"><a>Toy Story</a></div>
    <p><strong><bdi>Budget</bdi></strong> $30,000,000</p>
    <p><strong><bdi>Revenue</bdi></strong> $401,157,969</p>
    <span class="runtime">1h 21m</span>
    <ol class="people">
        <li class="profile">
            <p><a>John Lasseter</a></p>
            <p class="character">Director</p>
        </li>
    </ol>
    """

    class MockResponse:
        text = html

        def raise_for_status(self):
            pass

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr("movielens_impl.links.requests.get", mock_get)

    result = links.get_imdb(
        [1],
        ["Title", "Director", "Budget",
         "Cumulative Worldwide Gross", "Runtime"]
    )

    assert isinstance(result, list)
    assert all(isinstance(movie, list) for movie in result)

    for movie in result:
        assert isinstance(movie[0], int)
        assert all(
            isinstance(value, (str, type(None)))
            for value in movie[1:]
        )


def test_analytical_methods_types():
    links = Links()

    links.last_fields = [
        "Title", "Director", "Budget",
        "Cumulative Worldwide Gross", "Runtime"
    ]

    links.imdb_info = [
        [1, "Toy Story", "John Lasseter",
         "$30,000,000", "$401,157,969", "1h 21m"],
        [2, "Jumanji", "Joe Johnston",
         "$65,000,000", "$262,821,940", "1h 44m"],
        [3, "Cars", "John Lasseter",
         "$120,000,000", "$462,216,280", "1h 57m"],
        [4, "The Rock", "Michael Bay",
         "$75,000,000", "$335,062,621", "2h 16m"]
    ]

    results = [
        (links.top_directors(3), int),
        (links.most_expensive(3), int),
        (links.most_profitable(3), int),
        (links.longest(3), int),
        (links.top_cost_per_minute(3), float),
        (links.longest_by_director(), int)
    ]

    for result, value_type in results:
        assert isinstance(result, dict)
        assert all(isinstance(key, str) for key in result)
        assert all(isinstance(value, value_type)
                   for value in result.values())
