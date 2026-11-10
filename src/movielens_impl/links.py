import requests
from bs4 import BeautifulSoup
import re
from collections import Counter


class Links:
    """
    Analyzing data from links.csv
    """

    def __init__(self, path_to_the_file='./data/links.csv'):
        self.links = {}
        self._load_links(path_to_the_file)
        self.imdb_info = []

    def _load_links(self, path_to_the_file):
        with open(path_to_the_file, "r", encoding="utf-8") as file:
            header_line = file.readline()

            if not header_line:
                raise ValueError("CSV is empty or missing header")

            for i, line in enumerate(file):
                if i == 1000:
                    break
                movieId, _, tmdbId = line.strip().split(",")
                if not tmdbId:
                    continue

                self.links[int(movieId)] = int(tmdbId)

    def get_imdb(self, list_of_movies, list_of_fields):
        self.imdb_info = []
        self.last_fields = list(list_of_fields)
        for movieId in list_of_movies:
            tmdbId = self.links.get(movieId)
            if not tmdbId:
                continue

            url = f"https://www.themoviedb.org/movie/{tmdbId}"

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                title_block = soup.find("div", class_="title")
                title_tag = title_block.find("a") if title_block else None
                title = title_tag.get_text(strip=True) if title_tag else None

                budget_tag = soup.find("bdi", string="Budget")
                budget = None
                if budget_tag:
                    budget = budget_tag.parent.parent.get_text(" ", strip=True)

                revenue_tag = soup.find("bdi", string="Revenue")
                revenue = None
                if revenue_tag:
                    revenue = revenue_tag.parent.parent.get_text(
                        " ", strip=True)

                runtime_tag = soup.find("span", class_="runtime")
                runtime = None
                if runtime_tag:
                    runtime = runtime_tag.get_text(
                        strip=True)

                people = soup.find("ol", class_="people")
                profiles = people.find_all(
                    "li", class_="profile") if people else []
                director = None
                for profile in profiles:
                    dir_tag = profile.find("p", class_="character")
                    if dir_tag and "director" in dir_tag.get_text(strip=True).lower():
                        name_tag = profile.find("a")
                        if name_tag:
                            director = name_tag.get_text(strip=True)
                            break

                fields = {
                    "Title": title,
                    "Director": director,
                    "Budget": budget,
                    "Cumulative Worldwide Gross": revenue,
                    "Runtime": runtime
                }
                result = [fields.get(field) for field in list_of_fields]
                self.imdb_info.append(
                    [movieId] + result)

            except requests.RequestException as error:
                print(f"Не удалось загрузить фильм {movieId}: {error}")
                continue

        self.imdb_info.sort(key=lambda row: row[0], reverse=True)

        return self.imdb_info

    def _get_field_index(self, field):
        if field not in self.last_fields:
            raise ValueError(f"Field '{field}' was not requested")
        return self.last_fields.index(field) + 1

    def _extract_money(self, value):
        match = re.search(r'\$([\d,]+)', value)
        if match:
            return int(match.group(1).replace(',', ''))
        return None

    def _runtime_to_minutes(self, runtime):
        match = re.search(r'(\d+)h\s*(\d+)m', runtime)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return hours * 60 + minutes
        return None

    def top_directors(self, n):
        if n < 0:
            raise ValueError("n must be non-negative")

        director_index = self._get_field_index("Director")
        counter_directors = Counter(
            movie[director_index]
            for movie in self.imdb_info
            if movie[director_index]
        )

        directors = dict(counter_directors.most_common(n))
        return directors

    def most_expensive(self, n):
        if n < 0:
            raise ValueError("n must be non-negative")

        title_index = self._get_field_index("Title")
        budget_index = self._get_field_index("Budget")

        budgets = dict(
            (
                movie[title_index],
                budget_value
            )
            for movie in self.imdb_info
            if movie[title_index] and movie[budget_index]
            and (budget_value := self._extract_money(movie[budget_index])) is not None
        )

        budgets = dict(
            sorted(budgets.items(), key=lambda x: x[1], reverse=True)[:n])

        return budgets

    def most_profitable(self, n):
        if n < 0:
            raise ValueError("n must be non-negative")

        title_index = self._get_field_index("Title")
        budget_index = self._get_field_index("Budget")
        revenue_index = self._get_field_index(
            "Cumulative Worldwide Gross")

        profits = dict(
            (
                movie[title_index],
                (revenue_value - budget_value)
            )
            for movie in self.imdb_info
            if movie[title_index] and movie[budget_index] and movie[revenue_index]
            and (budget_value := self._extract_money(movie[budget_index])) is not None
            and (revenue_value := self._extract_money(movie[revenue_index])) is not None
        )

        profits = dict(
            sorted(profits.items(), key=lambda x: x[1], reverse=True)[:n])

        return profits

    def longest(self, n):
        if n < 0:
            raise ValueError("n must be non-negative")

        title_index = self._get_field_index("Title")
        runtime_index = self._get_field_index("Runtime")

        runtimes = dict(
            (
                movie[title_index],
                total_minutes
            )
            for movie in self.imdb_info
            if movie[title_index] and movie[runtime_index] and (total_minutes := self._runtime_to_minutes(movie[runtime_index])) is not None
        )

        runtimes = dict(
            sorted(runtimes.items(), key=lambda x: x[1], reverse=True)[:n])

        return runtimes

    def top_cost_per_minute(self, n):
        if n < 0:
            raise ValueError("n must be non-negative")

        title_index = self._get_field_index("Title")
        budget_index = self._get_field_index("Budget")
        runtime_index = self._get_field_index("Runtime")

        costs = dict(
            (
                movie[title_index],
                round(budget_value / total_minutes, 2)
            )
            for movie in self.imdb_info
            if movie[title_index] and movie[budget_index] and movie[runtime_index]
            and (budget_value := self._extract_money(movie[budget_index])) is not None
            and (total_minutes := self._runtime_to_minutes(movie[runtime_index])) is not None
            and total_minutes > 0
        )

        costs = dict(
            sorted(costs.items(), key=lambda x: x[1], reverse=True)[:n]
        )

        return costs

    def longest_by_director(self):
        director_runtimes = Counter()

        title_index = self._get_field_index("Title")
        director_index = self._get_field_index("Director")
        runtime_index = self._get_field_index("Runtime")

        for movie in self.imdb_info:
            title = movie[title_index]
            director = movie[director_index]
            runtime_str = movie[runtime_index]

            if title and director and runtime_str:
                total_minutes = self._runtime_to_minutes(runtime_str)
                if total_minutes is not None:
                    director_runtimes[director] += total_minutes

        longest_movies_by_director = dict(
            sorted(director_runtimes.items(), key=lambda x: x[1], reverse=True))

        return longest_movies_by_director


if __name__ == "__main__":
    links = Links()
    print(len(links.links))
    print(list(links.links.items())[:5])
    print('result of get_imdb')
    print(links.get_imdb([1, 2, 3, 4, 5, 6, 7, 12, 345, 567, 234, 887, 453, 895, 434, 456, 566], ["Title", "Runtime",
          "Budget", "Cumulative Worldwide Gross", "Director"]))
    print('result of top_directors')
    print(links.top_directors(3))
    print('result of most_expensive')
    print(links.most_expensive(20))
    print('result of most_profitable')
    print(links.most_profitable(20))
    print('result of longest')
    print(links.longest(20))
    print('result of top_cost_per_minute')
    print(links.top_cost_per_minute(20))
    print('result of longest_by_director')
    print(links.longest_by_director())
