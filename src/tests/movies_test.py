from movielens_impl.movies import Movies
import pytest


def test_get_name(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        '1,Toy Story (1995),Adventure|Animation|Children\n'
        '2,"American President, The (1995)",Comedy|Drama\n',
        encoding="utf-8"
    )

    movies = Movies(str(file))

    assert movies.get_name(1) == "Toy Story (1995)"
    assert movies.get_name(2) == "American President, The (1995)"


def test_dist_by_release(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        "1,Toy Story (1995),Animation|Comedy\n"
        "2,Jumanji (1995),Adventure|Fantasy\n"
        "3,Heat (1995),Action|Crime\n"
        "4,Titanic (1997),Drama|Romance\n"
        "5,Alien (1979),Horror|Sci-Fi\n",
        encoding="utf-8"
    )

    movies = Movies(str(file))
    result = movies.dist_by_release()

    assert isinstance(result, dict)
    assert all(isinstance(year, int) for year in result)
    assert all(isinstance(count, int) for count in result.values())

    assert result == {
        1995: 3,
        1997: 1,
        1979: 1
    }


def test_dist_by_genres(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        "1,Toy Story (1995),Animation|Comedy\n"
        "2,Jumanji (1995),Adventure|Fantasy\n"
        "3,Heat (1995),Action|Crime\n"
        "4,Titanic (1997),Drama|Romance\n"
        "5,Alien (1979),Horror|Sci-Fi\n"
        "6,Comedy Movie (2000),Comedy|Drama\n",
        encoding="utf-8"
    )

    movies = Movies(str(file))
    result = movies.dist_by_genres()

    assert isinstance(result, dict)
    assert all(isinstance(genre, str) for genre in result)
    assert all(isinstance(count, int) for count in result.values())
    counts = list(result.values())
    assert counts == sorted(counts, reverse=True)

    assert result == {
        "Comedy": 2,
        "Drama": 2,
        "Animation": 1,
        "Adventure": 1,
        "Fantasy": 1,
        "Action": 1,
        "Crime": 1,
        "Romance": 1,
        "Horror": 1,
        "Sci-Fi": 1
    }


def test_most_genres(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        "1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy\n"
        "2,Jumanji (1995),Adventure|Children|Fantasy\n"
        "3,Heat (1995),Action|Crime|Thriller\n"
        "4,Titanic (1997),Drama|Romance\n",
        encoding="utf-8"
    )

    movies = Movies(str(file))
    result = movies.most_genres(2)

    assert isinstance(result, dict)
    assert len(result) == 2
    assert all(isinstance(title, str) for title in result)
    assert all(isinstance(count, int) for count in result.values())
    assert movies.most_genres(0) == {}
    with pytest.raises(ValueError):
        movies.most_genres(-1)

    assert result == {
        "Toy Story (1995)": 5,
        "Jumanji (1995)": 3
    }


def test_search_by_genre(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        "1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy\n"
        "2,Jumanji (1995),Adventure|Children|Fantasy\n"
        "3,Heat (1995),Action|Crime|Thriller\n"
        "4,Titanic (1997),Drama|Romance\n",
        encoding="utf-8"
    )

    movies = Movies(str(file))

    result = movies.search_by_genre("Fantasy")
    assert isinstance(result, list)
    assert all(isinstance(title, str) for title in result)
    assert result == [
        "Toy Story (1995)",
        "Jumanji (1995)"
    ]

    assert movies.search_by_genre("Western") == []


def test_most_genres_sorted_descending(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        "1,Movie A (2000),Comedy\n"
        "2,Movie B (2001),Action|Drama|Comedy\n"
        "3,Movie C (2002),Drama|Romance\n"
        "4,Movie D (2003),Action|Drama|Comedy|Horror\n",
        encoding="utf-8"
    )

    movies = Movies(str(file))
    result = movies.most_genres(4)

    counts = list(result.values())

    assert counts == sorted(counts, reverse=True)


def test_dist_by_genres_types(tmp_path):
    file = tmp_path / "movies.csv"
    file.write_text(
        "movieId,title,genres\n"
        "1,Toy Story (1995),Adventure|Animation\n"
        "2,Jumanji (1995),Adventure|Fantasy\n",
        encoding="utf-8"
    )

    movies = Movies(str(file))
    result = movies.dist_by_genres()

    assert isinstance(result, dict)
    assert all(isinstance(genre, str) for genre in result.keys())
    assert all(isinstance(count, int) for count in result.values())


def test_load_movies_empty_file_raises_error(tmp_path):
    file_path = tmp_path / "empty_movies.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV is empty or missing header"):
        Movies(str(file_path))
