from movielens_impl.movies import Movies
from datetime import datetime, timezone
from collections import Counter, defaultdict

class Ratings:
    """
    Analyzing data from ratings.csv
    """
    def __init__(self, 
        path_to_the_file='./data/ratings.csv', 
        movies=Movies(),
    ):
        self.data: list[dict[str, int|float]] = self._read_data(movies, path_to_the_file)
        self.movies_analytics = self.MoviesAnalytics(self.data)
        self.users = self.Users(self.data)
        
    
    def _read_data(self, movies, path_to_the_file: str) -> list[dict[str,int|float]]:
        try:
            with open(path_to_the_file, "r", encoding='utf-8') as file:
                data = self._process_data(file, movies)
            return data                                    
        except (FileNotFoundError, PermissionError) as e:
            print(f'file access error {path_to_the_file}: {e}')
        except Exception as e:
            print(f'unexpected error: {e}')
        
        return []
            
        
    def _process_data(self, file, movies):
        data = []
        header = file.readline().strip().split(',')
        if header != ['userId','movieId','rating','timestamp']:
            return []
        count = 0
        keys = header + ['title']
        for line in file:
            if not line:
                print(f'Managed to read {len(data)} of {count} lines from the file')
                break
            
            record = line.strip().split(',')
            if len(record) != 4:
                # print(f'Пропущена битая строка: {record}')
                continue
            
            try:
                values = [int(record[0]), int(record[1]), float(record[2]), int(record[3])]
                self._validation_data(values)
                values.append(movies.movies[values[1]][0])
                data.append(dict(zip(keys, values)))
                count += 1
            except ValueError:
                # print(f'Пропущена битая строка: {line.strip()}')
                continue
        return data
    
    
    @staticmethod
    def _validation_data(values):
        if Ratings._is_valid_user_id(values[0]) \
            and Ratings._is_valid_movie_id(values[1]) \
            and Ratings._is_valid_rating(values[2]) \
            and Ratings._is_valid_timestamp(values[3]):
                return True
        else:
            raise ValueError(f"Incorrect values {values}")
        
        
    @staticmethod
    def _is_valid_user_id(user_id):
        return user_id > 0
        
    @staticmethod
    def _is_valid_movie_id(movie_id):
        return movie_id > 0
        
    @staticmethod
    def _is_valid_rating(rating):
        return rating in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    
    @staticmethod
    def _is_valid_timestamp(timestamp):
        now_utc = datetime.now(timezone.utc)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc) <= now_utc
    
       
    class MoviesAnalytics:
        def __init__(self, data: list[dict[str, int | float]]):
            self.data: list[dict[str, int | float]] = data
            
        
        def dist_by_year(self) -> dict[int, int]:
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sorted by years ascendingly. You need to extract years from timestamps.
            """
            years = Counter(
                [datetime.fromtimestamp(record['timestamp'], tz=timezone.utc).year 
                for record in self.data]
            )
            return dict(sorted(years.items()))
        
        
        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
            Sorted by ratings ascendingly.
            """
            ratings = Counter(
                record['rating'] 
                for record in self.data
            )
            return dict(sorted(ratings.items()))
            
        
        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
            Sorted by numbers descendingly.
            """
            self._check_n(n)
            
            movie_titles = [record['title'] for record in self.data]
            count = Counter(movie_titles)
            return dict(count.most_common(n))
        
        
        def top_by_ratings(self, n, metric='average'):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sorted by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            self._check_n(n)
                        
            if metric == 'average':
                metric_func = self._get_average
            elif metric == 'median':
                metric_func = self._get_median
            else:
                raise ValueError(f"metric must be 'average' or 'median', not {metric}")

            return self._top_by_metric(n, metric_func)
        
        
        def top_controversial(self, n):
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
            Sorted by variance descendingly.
            The values should be rounded to 2 decimals.
            """
            
            self._check_n(n)
            return self._top_by_metric(n, self._get_variance)            
        

        def _top_by_metric(self, n, metric_func):
            ratings_by_movie = defaultdict(list)
            
            for record in self.data:
                ratings_by_movie[record['title']].append(record['rating'])
                
            movie_metrics = {
                title: metric_func(ratings)
                for title, ratings in ratings_by_movie.items()
            }
            top = sorted(movie_metrics.items(), key=lambda item: item[1], reverse=True)[:n]
            
            return {title: round(rat, 2) for title, rat in top}
        
        # доп метод
        def top_by_weighted_rating(self, n, min_count_ratings=10, metric='average'):
            """
            Returns the top-n movies by a weighted average of their ratings.

            Uses a Bayesian-like smoothing to prevent movies with very few ratings 
            but high average scores from dominating the top list. The movie's average 
            is pulled towards the global dataset average until it accumulates 
            at least `min_count_ratings`.

            Args:
                n (int): The number of top movies to return.
                min_count_ratings (int): The minimum number of ratings required 
                                        for a movie to be considered, and the weight 
                                        parameter for smoothing.

            Returns:
                dict[str, float]: A dictionary of movie titles and their weighted 
                                ratings (rounded to 2 decimals), sorted in 
                                descending order.
            """
            
            self._check_n(n)
            if not self.data:
                return {}
            
            if metric not in ('average', 'median', 'variance'):
                raise ValueError(f"metric must be 'average', 'median', or 'variance', not {metric!r}")
            
            ratings_by_movie = defaultdict(list)
            for record in self.data:
                ratings_by_movie[record['title']].append(record['rating'])
            
            avg_all_movies = sum(record['rating'] for record in self.data) / len(self.data)
            
            weighted_movies = {}
            for title, ratings in ratings_by_movie.items():
                count_ratings = len(ratings)
                
                # пропускаем фильмы с малым количеством оценок
                if count_ratings < min_count_ratings:
                    continue
                if metric == 'average':
                    avg = self._get_average(ratings)
                    weighted_avg_movie = (count_ratings / (count_ratings + min_count_ratings)) * avg
                    weighted_avg_all_movies = (min_count_ratings / (count_ratings + min_count_ratings)) * avg_all_movies
                    score = weighted_avg_movie + weighted_avg_all_movies
                elif metric == 'median':
                    score = self._get_median(ratings)
                elif metric == 'variance':
                    score = self._get_variance(ratings)
                    
                weighted_movies[title] = round(score, 2)
            
            top = sorted(weighted_movies.items(), key=lambda item: (-item[1],item[0]))[:n]
            return dict(top)

                
        @staticmethod
        def _get_average(ratings):
            if not ratings:
                raise ValueError('incorrect ratings')
            return sum(ratings) / len(ratings)
                    
                    
        @staticmethod
        def _get_median(ratings):
            if not ratings:
                raise ValueError('incorrect ratings')
            sorted_ratings = sorted(ratings)
            mid = len(sorted_ratings) // 2
            if len(sorted_ratings) % 2 == 0:
                value = (sorted_ratings[mid - 1] + sorted_ratings[mid]) / 2
            else:
                value = sorted_ratings[mid]
            return value
                    
                    
        @staticmethod
        def _get_variance(ratings):
            if not ratings:
                raise ValueError('incorrect ratings')
            mean = Ratings.MoviesAnalytics._get_average(ratings)
            variance = sum((x - mean) ** 2 for x in ratings) / len(ratings)
            return variance
        
        
        @staticmethod
        def _check_n(n):
            if isinstance(n, bool) or not isinstance(n, int) or n < 0:
                raise ValueError(f"Incorrect param n: {n!r}")
            

        
    class Users(MoviesAnalytics):
        """
        In this class, three methods should work. 
        The 1st returns the distribution of users by the number of ratings made by them.
        The 2nd returns the distribution of users by average or median ratings made by them.
        The 3rd returns top-n users with the biggest variance of their ratings.
        Inherit from the class Movies. Several methods are similar to the methods from it.
        """
        
        def dist_by_num_of_ratings(self):
            """
            The method returns the distribution of users by the number of ratings made by them.
            This is a dictionary where the keys are userId and the values ​​are the number of ratings.
            Sorted by ratings ascendingly.
            """
            ratings = Counter(
                record['userId'] 
                for record in self.data
            )
            return dict(sorted(ratings.items(), key=lambda item: (item[1], item[0])))
        
        
        def dist_by_ratings(self, metric='average'):
            """
            The method returns the distribution of users by average or median ratings made by them.
            This is a dictionary where the keys are userId and the values ​​are metric values.
            Sorted by ratings ascendingly.
            """
            if metric == 'average':
                metric_func = self._get_average
            elif metric == 'median':
                metric_func = self._get_median
            else:
                raise ValueError(f"Incorrect param metric: {metric!r}")
            
            return self._get_dist_by_rating_for_metric(metric_func)
        
        
        def _get_dist_by_rating_for_metric(self, metric_func):
            ratings_by_user = defaultdict(list)
            for record in self.data:
                ratings_by_user[record['userId']].append(record['rating'])
                
            users_metric = {
                user_id: metric_func(ratings)
                for user_id, ratings in ratings_by_user.items()
            }
            
            result = sorted(users_metric.items())
            return {user_id: round(metric, 2) for user_id, metric in result}
        
        
        def top_controversial(self, n):
            """
            The 3rd returns top-n users with the biggest variance of their ratings.
            This is a dictionary where the keys are userIDs and the values are variances.
            Sorted by variance in descending order.
            """
            self._check_n(n)
            users_metric = self._get_dist_by_rating_for_metric(self._get_variance)
            result = sorted(users_metric.items(), key=lambda item: item[1], reverse=True)[:n]
            return dict(result)
            
            
        
        