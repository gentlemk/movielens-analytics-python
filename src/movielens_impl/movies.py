from email import header
import re
from collections import Counter


class Movies:
    """
    Analyzing data from movies.csv
    """

    def __init__(self, path_to_the_file='./data/movies.csv'):
        self.movies = self._load_movies(path_to_the_file)


    def _load_movies(self, path_to_the_file='./data/movies.csv'):
        pattern = r'(\d+),(?:"([^"]+)"|([^,]+)),(.+)'
        with open(path_to_the_file, "r", encoding="utf-8") as file:
            header = file.readline()

            if not header:
                raise ValueError("CSV is empty or missing header")
            result = {}
            for line in file:
                match = re.match(pattern, line.strip())
                if match:
                    movieId = int(match.group(1))
                    title = match.group(2) if match.group(2) else match.group(3)
                    genres = match.group(4)
                    result[movieId] = (title, genres.split("|"))
        return result


    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts.
        You need to extract years from the titles. Sort it by counts descendingly.
        """

        years_counter = Counter(
            int(match.group(1))
            for movie in self.movies.values()
            if (match := re.search(r'\((\d{4})\)', movie[0]))
        )

        release_years = dict(years_counter.most_common())

        return release_years

    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
        Sort it by counts descendingly.
        """

        genres_counter = Counter(
            genre for movie in self.movies.values()
            for genre in movie[1]
        )

        genres = dict(genres_counter.most_common())

        return genres

    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        if n < 0:
            raise ValueError("n не может быть отрицательным")

        movies = {
            movie[0]: len(movie[1])
            for movie in self.movies.values()
        }

        movies = dict(
            sorted(movies.items(), key=lambda x: x[1], reverse=True)[:n])

        return movies

    def search_by_genre(self, genre):
        """
        The method returns a list of movie titles that belong to the given genre.
        """

        result = [movie[0]
                  for movie in self.movies.values() if genre in movie[1]]

        return result
    
    def get_name(self, movieId):
        """
        The method returns the name of the movie given its movieId.
        """

        if movieId in self.movies:
            return self.movies[movieId][0]
        else:
            return movieId


