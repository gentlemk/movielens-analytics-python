import pytest

from datetime import datetime, timezone
from movielens_impl import Ratings

# =============================================
# fixture
# =============================================
CSV_VALID_RATINGS = """\
userId,movieId,rating,timestamp
1,1,4.0,964982703
1,3,4.0,964981247
1,6,4.0,964982224
1,47,5.0,964983815
1,50,5.0,964982931
2,112552,4.0,1445714882
2,114060,2.0,1445715276
2,115713,3.5,1445714854
2,122882,5.0,1445715272
3,3949,0.5,1306464245
3,4518,5.0,1306463770
3,5048,0.5,1306464284
3,5181,5.0,1306463718
3,5746,5.0,1306463708
4,162,5.0,945078571
4,171,3.0,945078428
4,176,5.0,964622565
4,190,2.0,945079259
4,215,5.0,945079078
5,34,4.0,847434881
5,36,4.0,847435292
5,39,3.0,847434961
5,50,4.0,847434881
5,58,5.0,847435238
"""

CSV_WITH_EMPTY_LINES = """\
userId,movieId,rating,timestamp
1,1,4.0,964982703

1,47,5.0,964983815

1,50,5.0,964982931
       
2,115713,3.5,1445714854

2,122882,5.0,1445715272
      

"""

CSV_EMPTY_FILE = ""

CSV_ONLY_HEADER = "\
userId,movieId,rating,timestamp\n"

CSV_SINGLE_USER = """\
userId,movieId,rating,timestamp
7,1,4.0,1498889573
7,2,3.5,1530484737
7,3,5.0,1440839586
7,4,2.5,1498727232
7,5,1.0,1498868843
"""

CSV_SINGLE_MOVIE = """\
userId,movieId,rating,timestamp
1,1,4.0,1498889573
2,1,3.5,1530484737
3,1,5.0,1440839586
4,1,2.5,1498727232
5,1,1.0,1498868843
"""

CSV_SINGLE_RATINGS = """\
userId,movieId,rating,timestamp
1,1,4.0,1498889573
1,2,4.0,1530484737
2,1,4.0,1440839586
2,2,4.0,1498727232
2,3,4.0,1498868843
"""

CSV_WEIGHTED_SMOOTHING = """\
userId,movieId,rating,timestamp
1,1,5.0,1000000000
2,1,5.0,1000000000
3,1,5.0,1000000000
1,2,5.0,1000000000
2,2,5.0,1000000000
1,3,1.0,1000000000
2,3,1.0,1000000000
3,3,1.0,1000000000
4,3,1.0,1000000000
5,3,1.0,1000000000
"""

CSV_SINGLE_TIMESTAMP = """\
userId,movieId,rating,timestamp
1,1,4.0,1498880000
1,2,4.5,1498880000
2,1,2.5,1498880000
2,2,5.0,1498880000
2,3,1.0,1498880000
"""

CSV_WRONG_COLUMNS = """\
userId,movieId,rating,timestamp
4,176,5.0,
4,190,,945079259
4,,5.0,945079078
,34,4.0,847434881
5,36,4.0,847435292,1
5,39,3.0,847434961,asd
5,50,4.0,847434881,-1,BC,12.5
7,2,3.5,1530484737
7,3,5.0,1440839586
"""

CSV_ONE_PER_YEAR = """\
userId,movieId,rating,timestamp
1,1,4.0,1483228800
1,2,4.0,1514764800
1,3,4.0,1546300800
"""

CSV_YEAR_BOUNDARIES_UTC = """\
userId,movieId,rating,timestamp
1,1,4.0,1514764799
1,2,4.0,1514764800
"""

CSV_MULTI_PER_YEAR = """\
userId,movieId,rating,timestamp
1,1,4.0,1483228800
1,2,4.0,1483228801
1,3,4.0,1483228802
1,4,4.0,1514764800
"""

CSV_MIN_MAX_RATING = """\
userId,movieId,rating,timestamp
1,1,0.5,1498867200
1,2,5.0,1498867200
1,3,5.0,1498867200
"""

CSV_RATING_UNSORTED_INPUT = """\
userId,movieId,rating,timestamp
1,1,5.0,1498867200
1,2,0.5,1498867200
1,3,3.0,1498867200
"""

CSV_RATING_MULTI = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
1,2,4.0,1498867200
1,3,4.0,1498867200
1,4,1.0,1498867200
"""

CSV_TOP_COUNTS = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
2,1,3.0,1498867200
3,1,5.0,1498867200
1,2,4.0,1498867200
2,2,2.0,1498867200
1,3,1.0,1498867200
"""

CSV_TOP_TIES = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
1,2,4.0,1498867200
1,3,4.0,1498867200
"""

CSV_TOP_UNSORTED_COUNTS = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
1,2,4.0,1498867200
2,2,4.0,1498867200
3,2,4.0,1498867200
1,3,4.0,1498867200
2,3,4.0,1498867200
"""

CSV_TOP_BY_RATINGS_AVG = """\
userId,movieId,rating,timestamp
1,1,5.0,1498867200
2,1,3.0,1498867200
1,2,4.0,1498867200
2,2,4.0,1498867200
1,3,2.0,1498867200
2,3,3.0,1498867200
"""

CSV_TOP_BY_RATINGS_MEDIAN = """\
userId,movieId,rating,timestamp
1,1,5.0,1498867200
2,1,1.0,1498867200
3,1,3.0,1498867200
1,2,2.0,1498867200
2,2,4.0,1498867200
1,3,1.0,1498867200
"""

CSV_TOP_BY_RATINGS_DEFAULT_METRIC = """\
userId,movieId,rating,timestamp
1,1,5.0,1498867200
2,1,1.0,1498867200
3,1,1.0,1498867200
"""

CSV_TOP_BY_RATINGS_ROUNDING = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
2,1,4.0,1498867200
3,1,5.0,1498867200
"""

CSV_TOP_BY_RATINGS_UNSORTED = """\
userId,movieId,rating,timestamp
1,1,2.0,1498867200
1,2,5.0,1498867200
1,3,3.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_VALUES = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
2,1,5.0,1498867200
1,2,3.0,1498867200
2,2,3.0,1498867200
1,3,2.0,1498867200
2,3,4.0,1498867200
3,3,3.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_ROUNDING = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
2,1,2.0,1498867200
3,1,4.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_IDENTICAL = """\
userId,movieId,rating,timestamp
1,1,3.0,1498867200
2,1,3.0,1498867200
3,1,3.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_TIES = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
2,1,5.0,1498867200
1,2,1.0,1498867200
2,2,5.0,1498867200
1,3,1.0,1498867200
2,3,5.0,1498867200
"""

CSV_DIST_BY_NUM_COUNTS = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
1,2,3.0,1498867200
1,3,5.0,1498867200
2,1,4.0,1498867200
2,2,2.0,1498867200
3,1,1.0,1498867200
"""

CSV_DIST_BY_NUM_TIES = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
2,1,4.0,1498867200
3,1,4.0,1498867200
"""

CSV_DIST_BY_NUM_SINGLE_USER = """\
userId,movieId,rating,timestamp
7,1,4.0,1498867200
7,2,3.0,1498867200
7,3,5.0,1498867200
"""

CSV_DIST_BY_RATINGS_AVG = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
1,2,2.0,1498867200
2,1,1.0,1498867200
2,2,5.0,1498867200
2,3,5.0,1498867200
3,1,5.0,1498867200
"""

CSV_DIST_BY_RATINGS_MEDIAN = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
1,2,5.0,1498867200
2,1,1.0,1498867200
2,2,3.0,1498867200
2,3,5.0,1498867200
"""

CSV_DIST_BY_RATINGS_AVG_NE_MEDIAN = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
1,2,5.0,1498867200
1,3,5.0,1498867200
"""

CSV_DIST_BY_RATINGS_ROUNDING = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
1,2,4.0,1498867200
1,3,5.0,1498867200
"""

CSV_DIST_BY_RATING_FOR_METRIC_UNSORTED = """\
userId,movieId,rating,timestamp
3,1,4.0,1498867200
1,1,4.0,1498867200
2,1,4.0,1498867200
"""

CSV_DIST_BY_RATING_FOR_METRIC_SUMS = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
1,2,2.0,1498867200
1,3,3.0,1498867200
2,1,4.0,1498867200
2,2,5.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_USERS_VALUES = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
1,2,5.0,1498867200
2,1,3.0,1498867200
2,2,3.0,1498867200
3,1,2.0,1498867200
3,2,4.0,1498867200
3,3,3.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_USERS_ROUNDING = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
1,2,2.0,1498867200
1,3,4.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_USERS_SINGLE = """\
userId,movieId,rating,timestamp
1,1,4.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_USERS_IDENTICAL = """\
userId,movieId,rating,timestamp
1,1,3.0,1498867200
1,2,3.0,1498867200
1,3,3.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_USERS_TIES = """\
userId,movieId,rating,timestamp
1,1,1.0,1498867200
1,2,5.0,1498867200
2,1,1.0,1498867200
2,2,5.0,1498867200
3,1,1.0,1498867200
3,2,5.0,1498867200
"""

CSV_TOP_CONTROVERSIAL_USERS_UNSORTED = """\
userId,movieId,rating,timestamp
1,1,3.0,1498867200
1,2,3.0,1498867200
2,1,1.0,1498867200
2,2,5.0,1498867200
3,1,1.0,1498867200
3,2,3.0,1498867200
"""

def make_invalid_csv(column, bad_value):
    """Создает некорректный csv файл

    Args:
        column (str): наименование колонки
        bad_value (int|float): Желаемое некорректное значение колонки

    Returns:
        str: Строку в виде готового файла
    """
    header = "userId,movieId,rating,timestamp\n"
    row = {"userId": 1, "movieId": 1, "rating": 1.0, "timestamp": 1530403215}
    row[column] = bad_value
    return header + f"{row['userId']},{row['movieId']},{row['rating']},{row['timestamp']}\n"


@pytest.fixture
def make_ratings(tmp_path):
    def _make(content) -> Ratings:
        filename="test_ratings.csv"
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return Ratings(str(path))
    return _make


class TestRatings:
    class TestReadData:
        def test_read_valid_file(self, make_ratings):
            
            ratings = make_ratings(CSV_VALID_RATINGS)
            
            assert isinstance(ratings.data, list)
            assert len(ratings.data) == 24
            assert isinstance(ratings.data[0], dict)
            
            first = ratings.data[0]
            assert isinstance(first['userId'], int)
            assert isinstance(first['movieId'], int)
            assert isinstance(first['rating'], float)
            assert isinstance(first['timestamp'], int)
            
            assert first == {
                "userId": 1,
                "movieId": 1,
                "rating": 4.0,
                "timestamp": 964982703,
                'title': 'Toy Story (1995)',
            }
            
            last = ratings.data[-1]
            assert isinstance(last['userId'], int)
            assert isinstance(last['movieId'], int)
            assert isinstance(last['rating'], float)
            assert isinstance(last['timestamp'], int)
            
            assert last == {
                "userId": 5,
                "movieId": 58,
                "rating": 5.0,
                "timestamp": 847435238,
                'title': 'Postman, The (Postino, Il) (1994)',
            }
            

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ]
        )
        def test_read_no_data_rows(self, make_ratings, content):
            ratings = make_ratings(content)
            assert ratings.data == []


        def test_read_with_empty_lines(self, make_ratings):
            ratings = make_ratings(CSV_WITH_EMPTY_LINES)
            
            assert len(ratings.data) == 5
            first = ratings.data[0]
            assert first == {
                "userId": 1,
                "movieId": 1,
                "rating": 4.0,
                "timestamp": 964982703,
                'title': 'Toy Story (1995)',
            }
            last = ratings.data[-1]
            assert last == {
                "userId": 2,
                "movieId": 122882,
                "rating": 5.0,
                "timestamp": 1445715272,
                'title': 'Mad Max: Fury Road (2015)',
            }

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(make_invalid_csv('userId', -10), id='negative_user_id'),
                pytest.param(make_invalid_csv('userId', 'abc'), id='str_user_id'),
                pytest.param(make_invalid_csv('movieId', 13.2), id='float_movie_id'),
                pytest.param(make_invalid_csv('movieId', 'abc'), id='str_movie_id'),
                pytest.param(make_invalid_csv('rating', 0), id='zero_rating'),
                pytest.param(make_invalid_csv('rating', -10), id='negative_rating'),
                pytest.param(make_invalid_csv('rating', 14), id='big_rating'),
                pytest.param(make_invalid_csv('rating', 3.2), id='invalid_rating'),
                pytest.param(make_invalid_csv('timestamp', int(datetime.now(timezone.utc).timestamp()) + 100000), id='future_time'),
                pytest.param(make_invalid_csv('timestamp', 13.5), id='float_time'),
                pytest.param(make_invalid_csv('timestamp', 'abc'), id='str_time'),
            ]
        )
        def test_read_with_broken_data(self, make_ratings, content):
            ratings = make_ratings(content)
            assert ratings.data == []
            


        def test_read_wrong_columns_count(self, make_ratings):
            ratings = make_ratings(CSV_WRONG_COLUMNS)
            
            assert len(ratings.data) == 2
            first = ratings.data[0]
            assert first == {
                "userId": 7,
                "movieId": 2,
                "rating": 3.5,
                "timestamp": 1530484737,
                'title': 'Jumanji (1995)',
            }
            
            last = ratings.data[-1]
            assert last == {
                "userId": 7,
                "movieId": 3,
                "rating": 5.0,
                "timestamp": 1440839586,
                'title': 'Grumpier Old Men (1995)',
            }


        def test_read_nonexistent_file(self):
            ratings = Ratings("not_file.csv")
            assert ratings.data == []

    
    class TestValidationData:
        class TestIsValidUserId:
            @pytest.mark.parametrize("user_id", [1, 2, 100, 1000])
            def test_valid_user_id(self, user_id):
                assert Ratings._is_valid_user_id(user_id) is True

            @pytest.mark.parametrize("user_id", [0, -1, -100])
            def test_invalid_user_id(self, user_id):
                assert Ratings._is_valid_user_id(user_id) is False

        class TestIsValidMovieId:
            @pytest.mark.parametrize("movie_id", [1, 2, 100, 1000])
            def test_valid_movie_id(self, movie_id):
                assert Ratings._is_valid_movie_id(movie_id) is True

            @pytest.mark.parametrize("movie_id", [0, -1, -100])
            def test_invalid_movie_id(self, movie_id):
                assert Ratings._is_valid_movie_id(movie_id) is False

        class TestIsValidrating:
            @pytest.mark.parametrize("rating", [0.5, 1.0, 2.5, 4.5, 5.0])
            def test_valid_rating(self, rating):
                assert Ratings._is_valid_rating(rating) is True

            @pytest.mark.parametrize("rating", [0, 0.4, 5.1, -1, 6])
            def test_invalid_rating(self, rating):
                assert Ratings._is_valid_rating(rating) is False

        class TestIsValidTimestamp:

            def test_valid_timestamp(self):
                timestamp = int(datetime.now(timezone.utc).timestamp()) - 100
                assert Ratings._is_valid_timestamp(timestamp) is True

            @pytest.mark.parametrize("timestamp", [-1, -100])
            def test_invalid_negative_timestamp(self, timestamp):
                assert Ratings._is_valid_timestamp(timestamp) is True

            def test_future_timestamp(self):
                timestamp = int(datetime.now(timezone.utc).timestamp()) + 100000
                assert Ratings._is_valid_timestamp(timestamp) is False
        
        @pytest.mark.parametrize(
            "values",
            [
                [1, 1, 0.5, 1000000000],
                [10, 20, 3.5, 1500000000],
                [100, 200, 5.0, 1600000000],
            ],
        )
        def test_valid_data(self, values):
            assert Ratings._validation_data(values) is True

        @pytest.mark.parametrize(
            "values",
            [
                [0, 1, 3.5, 1500000000],       # некорректный userId
                [1, 0, 3.5, 1500000000],       # некорректный movieId
                [1, 1, 0.0, 1500000000],       # рейтинг ниже допустимого
                [1, 1, 5.5, 1500000000],       # рейтинг выше допустимого
                [1, 1, 3.5, int(datetime.now(timezone.utc).timestamp()) + 100000],# timestamp в будущем
            ],
        )
        def test_invalid_data(self, values):
            with pytest.raises(ValueError):
                Ratings._validation_data(values)
        
class TestMoviesAnalytics:
    class TestGetAverage:
        @pytest.mark.parametrize(
            "values, expected",
            [
                pytest.param([1., 2., 3., 4.], 2.5, id="even_four_elements_float"),
                pytest.param([4, 1, 3, 2], 2.5, id="even_four_elements_int"),
                pytest.param([5, 5, 5, 5], 5.0, id="identical_values_even_int"),
                pytest.param([0.5, 0.5, 0.5], 0.5, id="identical_values_odd_float"),
                pytest.param([4], 4, id="single_element_int"),
                pytest.param([4.2], 4.2, id="single_element_float"),
            ],
        )
        def test_get_median(self, values, expected):
            assert Ratings.MoviesAnalytics._get_median(values) == expected
            
        def test_get_average_empty(self):
            with pytest.raises(ValueError):
                Ratings.MoviesAnalytics._get_average([])
                
    class TestGetMedian:
        @pytest.mark.parametrize(
            "values, expected",
            [
                pytest.param([1, 3, 2], 2.0, id="odd_three_elements"),
                pytest.param([7, 1, 5, 3, 9], 5, id="odd_five_elements"),
                pytest.param([4, 1, 3, 2], 2.5, id="even_four_elements"),
                pytest.param([1, 3, 2], 2.0, id="even_two_elements"),
                pytest.param([2, 1], 1.5, id="even_two_elements"),
                pytest.param([5, 5, 5, 5], 5.0, id="identical_values_even"),
                pytest.param([0.5, 0.5, 0.5], 0.5, id="identical_values_odd"),
                pytest.param([4.2], 4.2, id="single_element"),
            ],
        )
        def test_get_median(self, values, expected):
            assert Ratings.MoviesAnalytics._get_median(values) == expected
            
        def test_median_empty_list(self):
            with pytest.raises(ValueError):
                Ratings.MoviesAnalytics._get_median([])

    class TestGetVariance:
        def test_get_variance_empty_raises(self):
            with pytest.raises(ValueError):
                Ratings.MoviesAnalytics._get_variance([])
        
        @pytest.mark.parametrize(
            "values, expected",
            [
                pytest.param([1, 2, 3], pytest.approx(0.6667), id='test_1'),
                pytest.param([1.0, 2.0, 3.0], pytest.approx(0.6667), id='test_2'),
                pytest.param([1, 2, 3, 4], pytest.approx(1.25), id='test_3'),
                pytest.param([1.0, 2.0, 3.0, 4.0], pytest.approx(1.25), id='test_4'),
                pytest.param([4.0], pytest.approx(0), id='test_'),
                pytest.param([5.0, 5.0, 5.0], pytest.approx(0.0), id='test_5'),
                pytest.param([3, 3, 3, 3], pytest.approx(0.0), id='test_6'),
                pytest.param([1.0, 5.0], pytest.approx(4.0), id='test_7'),
                pytest.param([0.0, 2.0], pytest.approx(1.0), id='test_8'),
                pytest.param([0.5, 5.0], pytest.approx(5.0625), id='test_9'),
                pytest.param([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], pytest.approx(8.25), id='test_10'),
                pytest.param([2.5, 2.5, 2.5, 2.5], pytest.approx(0.0), id='test_11'),
            ]
        )
        def test_get_variance_valid(self, values, expected):
            result = Ratings.MoviesAnalytics._get_variance(values)
            assert isinstance(result, float)
            assert round(result, 4) == expected
            
    class TestCheckN:
        @pytest.mark.parametrize("n", [-1, True, False, 1.5, "odin", "2", None])
        def test_check_n_invalid_values(self, n):
            with pytest.raises(ValueError):
                Ratings.MoviesAnalytics._check_n(n)
            
        @pytest.mark.parametrize("n", [0, 1, 100])
        def test_check_n_valid_values(self, n):
            assert Ratings.MoviesAnalytics._check_n(n) is None

    class TestDistByYear:
        def test_dist_by_year_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_year()
            assert isinstance(result, dict)
        
        def test_dist_by_year_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_year()
            
            assert len(result) > 0
            for year, count in result.items():
                assert isinstance(year, int)
                assert isinstance(count, int)
        
        def test_dist_by_year_sorted(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_year()
            
            assert len(result) > 0
            assert list(result.keys()) == sorted(list(result.keys()))
        
        def test_dist_by_year_correct_counts(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_year()
            
            assert result == {
                1996: 5,
                1999: 4,
                2000: 6,
                2011: 5,
                2015: 4,
            }
        
        @pytest.mark.parametrize(
            "content, expected",
            [
                pytest.param(CSV_ONE_PER_YEAR, {2017: 1, 2018: 1, 2019: 1}, id="one_per_year"),
                pytest.param(CSV_MULTI_PER_YEAR, {2017: 3, 2018: 1}, id="multi_per_year"),
            ],
        )
        def test_dist_by_year_counts(self, make_ratings, content, expected):
            result = make_ratings(content).movies_analytics.dist_by_year()
            assert result == expected
        
        def test_dist_by_year_utc_boundaries(self, make_ratings):
            # 1514764799 = 2017-12-31 23:59:59 UTC, 1514764800 = 2018-01-01 00:00:00 UTC
            result = make_ratings(CSV_YEAR_BOUNDARIES_UTC).movies_analytics.dist_by_year()
            assert result == {2017: 1, 2018: 1}
        
        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_dist_by_year_no_data(self, make_ratings, content):
            result = make_ratings(content).movies_analytics.dist_by_year()
            assert result == {}
            
    class TestDistByRating:
        def test_dist_by_rating_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_rating()
            assert isinstance(result, dict)
            
            
        def test_dist_by_rating_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_rating()
            
            assert len(result) > 0
            for rating, count in result.items():
                assert isinstance(rating, float)
                assert isinstance(count, int)
                
                
        def test_dist_by_rating_sorted(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_rating()
            
            assert len(result) > 0
            keys = list(result.keys())
            assert keys == sorted(keys)
            

        def test_dist_by_rating_correct_counts(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.dist_by_rating()
            
            assert result == {
                0.5: 2, 
                2.0: 2,
                3.0: 2,
                3.5: 1,
                4.0: 7,
                5.0: 10,
            }
            
            
        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_dist_by_rating_no_data(self, make_ratings, content):
            result = make_ratings(content).movies_analytics.dist_by_rating()
            assert result == {}


        def test_dist_by_rating_sum_invariant(self, make_ratings):
            ratings = make_ratings(CSV_VALID_RATINGS)
            result = ratings.movies_analytics.dist_by_rating()

            assert len(result) > 0
            assert sum(result.values()) == len(ratings.data)
            for count in result.values():
                assert count > 0


        @pytest.mark.parametrize(
            "content, expected",
            [
                pytest.param(CSV_MIN_MAX_RATING, {0.5: 1, 5.0: 2}, id="min_max"),
                pytest.param(CSV_RATING_MULTI, {1.0: 1, 4.0: 3}, id="multi_same_rating"),
            ],
        )
        def test_dist_by_rating_counts(self, make_ratings, content, expected):
            result = make_ratings(content).movies_analytics.dist_by_rating()
            assert result == expected
            
            
        def test_dist_by_rating_sorted_with_unsorted_input(self, make_ratings):
            result = make_ratings(CSV_RATING_UNSORTED_INPUT).movies_analytics.dist_by_rating()
            assert list(result.keys()) == [0.5, 3.0, 5.0]  

    class TestTopByNumOfRatings:
        TITLE_1 = 'Toy Story (1995)'
        TITLE_2 = 'Jumanji (1995)'
        TITLE_3 = 'Grumpier Old Men (1995)'
        TITLE_4 = 'Waiting to Exhale (1995)'
        TITLE_5 = 'Father of the Bride Part II (1995)'
        def test_top_by_num_of_ratings_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_by_num_of_ratings(3)
            assert isinstance(result, dict)

        def test_top_by_num_of_ratings_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_by_num_of_ratings(3)

            assert len(result) > 0
            for movie_title, count in result.items():
                assert isinstance(movie_title, str | None)
                assert isinstance(count, int)

        @pytest.mark.parametrize(
            "content, n, expected",
            [
                pytest.param(CSV_TOP_COUNTS, 3, {TITLE_1: 3, TITLE_2: 2, TITLE_3: 1}, id="counts_all"),
                pytest.param(CSV_TOP_COUNTS, 2, {TITLE_1: 3, TITLE_2: 2}, id="counts_top2"),
                pytest.param(CSV_TOP_COUNTS, 1, {TITLE_1: 3}, id="counts_top1"),
                pytest.param(CSV_TOP_TIES, 3, {TITLE_1: 1, TITLE_2: 1, TITLE_3: 1}, id="ties_all"),
                pytest.param(CSV_TOP_TIES, 2, None, id="ties_top2"),
                pytest.param(CSV_TOP_UNSORTED_COUNTS, 3, {TITLE_2: 3, TITLE_3: 2, TITLE_1: 1}, id="unsorted_input"),
            ],
        )
        def test_top_by_num_of_ratings_counts(self, make_ratings, content, n, expected):
            result = make_ratings(content).movies_analytics.top_by_num_of_ratings(n)
            if expected is None:
                assert len(result) >= 1
                assert all(count == 1 for count in result.values())
            else:
                assert result == expected

        def test_top_by_num_of_ratings_sorted_descending(self, make_ratings):
            result = make_ratings(CSV_TOP_UNSORTED_COUNTS).movies_analytics.top_by_num_of_ratings(10)

            values = list(result.values())
            assert values == sorted(values, reverse=True)

        @pytest.mark.parametrize(
            "n, expected_len",
            [
                pytest.param(1, 1, id="n1"),
                pytest.param(2, 2, id="n2"),
                pytest.param(3, 3, id="n3"),
            ],
        )
        def test_top_by_num_of_ratings_limits_to_n(self, make_ratings, n, expected_len):
            result = make_ratings(CSV_TOP_COUNTS).movies_analytics.top_by_num_of_ratings(n)
            assert len(result) == expected_len

        def test_top_by_num_of_ratings_n_zero(self, make_ratings):
            result = make_ratings(CSV_TOP_COUNTS).movies_analytics.top_by_num_of_ratings(0)
            assert result == {}

        def test_top_by_num_of_ratings_n_negative(self, make_ratings):
            with pytest.raises(ValueError):
                make_ratings(CSV_TOP_COUNTS).movies_analytics.top_by_num_of_ratings(-1)

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_top_by_num_of_ratings_no_data(self, make_ratings, content):
            result = make_ratings(content).movies_analytics.top_by_num_of_ratings(5)
            assert result == {}

        def test_top_by_num_of_ratings_sum_invariant_all_movies(self, make_ratings):
            ratings = make_ratings(CSV_VALID_RATINGS)
            result = ratings.movies_analytics.top_by_num_of_ratings(len(ratings.data))
            assert sum(result.values()) == len(ratings.data)

        def test_top_by_num_of_ratings_sum_less_when_n_small(self, make_ratings):
            ratings = make_ratings(CSV_TOP_COUNTS)
            result = ratings.movies_analytics.top_by_num_of_ratings(1)
            assert sum(result.values()) < len(ratings.data)
            
    class TestTopByRatings:
        def test_top_by_ratings_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_by_ratings(3)
            assert isinstance(result, dict)


        def test_top_by_ratings_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_by_ratings(3)

            assert len(result) > 0
            for movie_title, value in result.items():
                assert isinstance(movie_title, str | None)
                assert isinstance(value, float)


        @pytest.mark.parametrize(
            "content, metric, expected",
            [
                pytest.param(
                    CSV_TOP_BY_RATINGS_AVG, "average",
                    {
                        'Toy Story (1995)': 4.0, 
                        'Jumanji (1995)': 4.0, 
                        'Grumpier Old Men (1995)': 2.5
                    },
                    id="average",
                ),
                pytest.param(
                    CSV_TOP_BY_RATINGS_MEDIAN, "median",
                    {
                        'Toy Story (1995)': 3.0, 
                        'Jumanji (1995)': 3.0, 
                        'Grumpier Old Men (1995)': 1.0
                    },
                    id="median",
                ),
            ],
        )
        def test_top_by_ratings_correct_values(self, make_ratings, content, metric, expected):
            result = make_ratings(content).movies_analytics.top_by_ratings(3, metric=metric)
            assert result == expected


        def test_top_by_ratings_default_metric_is_average(self, make_ratings):
            ratings = make_ratings(CSV_TOP_BY_RATINGS_DEFAULT_METRIC)

            default_result = ratings.movies_analytics.top_by_ratings(10)
            average_result = ratings.movies_analytics.top_by_ratings(10, metric="average")
            median_result = ratings.movies_analytics.top_by_ratings(10, metric="median")

            assert default_result == average_result
            assert default_result != median_result  


        def test_top_by_ratings_sorted_descending(self, make_ratings):
            result = make_ratings(CSV_TOP_BY_RATINGS_UNSORTED).movies_analytics.top_by_ratings(10, metric="average")

            values = list(result.values())
            assert values == sorted(values, reverse=True)


        @pytest.mark.parametrize(
            "n, expected_len",
            [
                pytest.param(1, 1, id="n1"),
                pytest.param(2, 2, id="n2"),
                pytest.param(3, 3, id="n3"),
            ],
        )
        def test_top_by_ratings_limits_to_n(self, make_ratings, n, expected_len):
            result = make_ratings(CSV_TOP_BY_RATINGS_AVG).movies_analytics.top_by_ratings(n, metric="average")
            assert len(result) == expected_len


        def test_top_by_ratings_n_larger_than_movies(self, make_ratings):
            ratings = make_ratings(CSV_TOP_BY_RATINGS_AVG)
            total_movies = len({r["movieId"] for r in ratings.data})
            result = ratings.movies_analytics.top_by_ratings(total_movies + 100)

            assert len(result) == total_movies


        def test_top_by_ratings_n_zero(self, make_ratings):
            result = make_ratings(CSV_TOP_BY_RATINGS_AVG).movies_analytics.top_by_ratings(0)
            assert result == {}


        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_top_by_ratings_no_data(self, make_ratings, content):
            result = make_ratings(content).movies_analytics.top_by_ratings(5)
            assert result == {}


        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
                pytest.param(CSV_TOP_BY_RATINGS_AVG, id="with_data"),
            ],
        )
        def test_top_by_ratings_invalid_metric(self, make_ratings, content):
            with pytest.raises(ValueError):
                make_ratings(content).movies_analytics.top_by_ratings(5, metric="invalid")
                
    class TestTopByControversial:
        def test_top_controversial_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(3)
            assert isinstance(result, dict)

        def test_top_controversial_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(3)

            assert len(result) > 0
            for movie_id, variance in result.items():
                assert isinstance(movie_id, str | None)
                assert isinstance(variance, float)

        def test_top_controversial_sorted_descending(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(10)

            values = list(result.values())
            assert values == sorted(values, reverse=True)

        @pytest.mark.parametrize(
            "n, expected_len",
            [
                pytest.param(1, 1, id="n1"),
                pytest.param(2, 2, id="n2"),
                pytest.param(3, 3, id="n3"),
            ],
        )
        def test_top_controversial_limits_to_n(self, make_ratings, n, expected_len):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(n)
            assert len(result) == expected_len


        def test_top_controversial_n_zero(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(0)
            assert result == {}

        def test_top_controversial_n_negative(self, make_ratings):
            with pytest.raises(ValueError):
                make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(-1)

        def test_top_controversial_correct_values(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_VALUES).movies_analytics.top_controversial(3)
            assert result == {
                'Toy Story (1995)': 4.0, 
                'Grumpier Old Men (1995)': 0.67,
                'Jumanji (1995)': 0, 
            }

        def test_top_controversial_rounds_to_two_decimals(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_ROUNDING).movies_analytics.top_controversial(1)
            assert result['Toy Story (1995)'] == 1.56

        def test_top_controversial_single_rating_zero_variance(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_controversial(30)
            assert result['Heat (1995)'] == 0.0

        def test_top_controversial_identical_ratings_zero_variance(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_IDENTICAL).movies_analytics.top_controversial(1)
            assert result == {'Toy Story (1995)': 0.0}

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_top_controversial_no_data(self, make_ratings, content):
            result = make_ratings(content).movies_analytics.top_controversial(5)
            assert result == {}

        def test_top_controversial_ties_all_present(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_TIES).movies_analytics.top_controversial(3)
            assert result == {
                'Toy Story (1995)': 4.0, 
                'Jumanji (1995)': 4.0, 
                'Grumpier Old Men (1995)': 4.0
            }

    class TestTopByWeightedRating:
        def test_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).movies_analytics.top_by_weighted_rating(5, min_count_ratings=10)
            assert isinstance(result, dict)

        def test_sorted_descending(self, make_ratings):
            result = make_ratings(CSV_WEIGHTED_SMOOTHING).movies_analytics.top_by_weighted_rating(2, min_count_ratings=3)
            values = list(result.values())
            assert values == sorted(values, reverse=True)

        @pytest.mark.parametrize(
            "n, min_count, expected_len",
            [
                pytest.param(1, 3, 1, id="limit_to_1"),
                pytest.param(2, 3, 2, id="limit_to_2"),
                pytest.param(10, 3, 2, id="more_than_available"),
                pytest.param(5, 5, 1, id="high_threshold"),
            ],
        )
        def test_limits_and_threshold(self, make_ratings, n, min_count, expected_len):
            result = make_ratings(CSV_WEIGHTED_SMOOTHING).movies_analytics.top_by_weighted_rating(n, min_count_ratings=min_count)
            assert len(result) == expected_len

        def test_n_zero(self, make_ratings):
            result = make_ratings(CSV_WEIGHTED_SMOOTHING).movies_analytics.top_by_weighted_rating(0, min_count_ratings=3)
            assert result == {}

        def test_n_negative_raises(self, make_ratings):
            with pytest.raises(ValueError):
                make_ratings(CSV_WEIGHTED_SMOOTHING).movies_analytics.top_by_weighted_rating(-1, min_count_ratings=3)

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_no_data(self, make_ratings, content):
            result = make_ratings(content).movies_analytics.top_by_weighted_rating(5)
            assert result == {}


class TestUsers:
    class TestDistByNumOfRatings:
        def test_dist_by_num_of_ratings_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_num_of_ratings()
            assert isinstance(result, dict)

        def test_dist_by_num_of_ratings_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_num_of_ratings()

            assert len(result) > 0
            for user_id, count in result.items():
                assert isinstance(user_id, int)
                assert isinstance(count, int)

        def test_dist_by_num_of_ratings_all_users_present(self, make_ratings):
            ratings = make_ratings(CSV_VALID_RATINGS)
            result = ratings.users.dist_by_num_of_ratings()

            expected_users = {r["userId"] for r in ratings.data}
            assert set(result.keys()) == expected_users

        def test_dist_by_num_of_ratings_correct_counts(self, make_ratings):
            # CSV_VALID_RATINGS: user 1 → 5, user 2 → 4, user 3 → 5, user 4 → 5, user 5 → 5
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_num_of_ratings()
            assert result == {2: 4, 1: 5, 3: 5, 4: 5, 5: 5}

        def test_dist_by_num_of_ratings_sorted_ascending(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_num_of_ratings()

            values = list(result.values())
            assert values == sorted(values)

        @pytest.mark.parametrize(
            "content, expected",
            [
                pytest.param(CSV_DIST_BY_NUM_COUNTS, {3: 1, 2: 2, 1: 3}, id="counts"),
                pytest.param(CSV_DIST_BY_NUM_TIES, {1: 1, 2: 1, 3: 1}, id="ties"),
                pytest.param(CSV_DIST_BY_NUM_SINGLE_USER, {7: 3}, id="single_user"),
            ],
        )
        def test_dist_by_num_of_ratings_counts(self, make_ratings, content, expected):
            result = make_ratings(content).users.dist_by_num_of_ratings()
            assert result == expected

        def test_dist_by_num_of_ratings_sum_invariant(self, make_ratings):
            ratings = make_ratings(CSV_VALID_RATINGS)
            result = ratings.users.dist_by_num_of_ratings()

            assert sum(result.values()) == len(ratings.data)

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_dist_by_num_of_ratings_no_data(self, make_ratings, content):
            result = make_ratings(content).users.dist_by_num_of_ratings()
            assert result == {}
            
    class TestDistByRatings:
        def test_dist_by_ratings_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_ratings()
            assert isinstance(result, dict)

        def test_dist_by_ratings_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_ratings()

            assert len(result) > 0
            for user_id, value in result.items():
                assert isinstance(user_id, int)
                assert isinstance(value, float)

        def test_dist_by_ratings_all_users_present(self, make_ratings):
            ratings = make_ratings(CSV_VALID_RATINGS)
            result = ratings.users.dist_by_ratings()

            expected_users = {r["userId"] for r in ratings.data}
            assert set(result.keys()) == expected_users

        @pytest.mark.parametrize(
            "content, metric, expected",
            [
                pytest.param(
                    CSV_DIST_BY_RATINGS_AVG, "average",
                    {1: 3.0, 2: 3.67, 3: 5.0},
                    id="average",
                ),
                pytest.param(
                    CSV_DIST_BY_RATINGS_MEDIAN, "median",
                    {1: 3.0, 2: 3.0},
                    id="median",
                ),
            ],
        )
        def test_dist_by_ratings_correct_values(self, make_ratings, content, metric, expected):
            result = make_ratings(content).users.dist_by_ratings(metric=metric)
            assert result == expected

        def test_dist_by_ratings_default_metric_is_average(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATINGS_AVG_NE_MEDIAN)

            default_result = ratings.users.dist_by_ratings()
            average_result = ratings.users.dist_by_ratings(metric="average")
            median_result = ratings.users.dist_by_ratings(metric="median")

            assert default_result == average_result
            assert default_result != median_result   # иначе тест не различает метрики

        def test_dist_by_ratings_sorted_by_user_id(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.dist_by_ratings()

            keys = list(result.keys())
            assert keys == sorted(keys)

        def test_dist_by_ratings_rounds_to_two_decimals(self, make_ratings):
            result = make_ratings(CSV_DIST_BY_RATINGS_ROUNDING).users.dist_by_ratings(metric="average")
            assert result[1] == 4.33

        def test_dist_by_ratings_single_rating(self, make_ratings):
            result = make_ratings(CSV_DIST_BY_NUM_SINGLE_USER).users.dist_by_ratings()
            assert result == {7: 4.0}

        def test_dist_by_ratings_sum_invariant(self, make_ratings):
            ratings = make_ratings(CSV_VALID_RATINGS)
            result = ratings.users.dist_by_ratings()

            assert len(result) == len({r["userId"] for r in ratings.data})

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_dist_by_ratings_no_data(self, make_ratings, content):
            result = make_ratings(content).users.dist_by_ratings()
            assert result == {}

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
                pytest.param(CSV_DIST_BY_RATINGS_AVG, id="with_data"),
            ],
        )
        def test_dist_by_ratings_invalid_metric(self, make_ratings, content):
            with pytest.raises(ValueError):
                make_ratings(content).users.dist_by_ratings(metric="invalid")
    
    class TestGetDistByRatingForMetric:
        def test_returns_dict(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_SUMS)
            result = ratings.users._get_dist_by_rating_for_metric(len)
            assert isinstance(result, dict)

        def test_key_value_types(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_SUMS)
            result = ratings.users._get_dist_by_rating_for_metric(len)

            assert len(result) > 0
            for user_id, value in result.items():
                assert isinstance(user_id, int)
                assert isinstance(value, int)   # round(len, 2) возвращает int? см. ниже

        def test_uses_metric_func_per_user(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_SUMS)
            result = ratings.users._get_dist_by_rating_for_metric(sum)
            assert result == {1: 6.0, 2: 9.0}

        def test_sorted_by_user_id(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_UNSORTED)
            result = ratings.users._get_dist_by_rating_for_metric(len)
            assert list(result.keys()) == [1, 2, 3]

        def test_rounds_to_two_decimals(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_SUMS)
            result = ratings.users._get_dist_by_rating_for_metric(lambda xs: 1.5555)
            assert result == {1: 1.56, 2: 1.56}

        def test_empty_data(self, make_ratings):
            ratings = make_ratings(CSV_ONLY_HEADER)
            result = ratings.users._get_dist_by_rating_for_metric(len)
            assert result == {}

        def test_metric_func_called_once_per_user(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_SUMS)
            calls = []
            def metric(xs):
                calls.append(list(xs))
                return len(xs)
            ratings.users._get_dist_by_rating_for_metric(metric)

            assert sorted(calls, key=lambda xs: xs[0]) == [
                [1.0, 2.0, 3.0],   # user 1
                [4.0, 5.0],        # user 2
            ]

        def test_metric_func_receives_user_ratings_only(self, make_ratings):
            ratings = make_ratings(CSV_DIST_BY_RATING_FOR_METRIC_SUMS)
            seen = {}
            def metric(xs):
                seen[len(seen)] = sorted(xs)
                return len(xs)
            ratings.users._get_dist_by_rating_for_metric(metric)
            assert sorted(seen.values()) == [[1.0, 2.0, 3.0], [4.0, 5.0]]
    
    class TestTopControversialUsers:
        def test_top_controversial_returns_dict(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.top_controversial(3)
            assert isinstance(result, dict)

        def test_top_controversial_key_value_types(self, make_ratings):
            result = make_ratings(CSV_VALID_RATINGS).users.top_controversial(3)

            assert len(result) > 0
            for user_id, variance in result.items():
                assert isinstance(user_id, int)
                assert isinstance(variance, float)

        def test_top_controversial_sorted_descending(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_UNSORTED).users.top_controversial(10)

            values = list(result.values())
            assert values == sorted(values, reverse=True)

        @pytest.mark.parametrize(
            "n, expected_len",
            [
                pytest.param(1, 1, id="n1"),
                pytest.param(2, 2, id="n2"),
                pytest.param(3, 3, id="n3"),
            ],
        )
        def test_top_controversial_limits_to_n(self, make_ratings, n, expected_len):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_VALUES).users.top_controversial(n)
            assert len(result) == expected_len

        def test_top_controversial_n_larger_than_users(self, make_ratings):
            ratings = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_VALUES)
            total_users = len({r["userId"] for r in ratings.data})
            result = ratings.users.top_controversial(total_users + 100)

            assert len(result) == total_users

        def test_top_controversial_n_zero(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_VALUES).users.top_controversial(0)
            assert result == {}

        def test_top_controversial_n_negative(self, make_ratings):
            with pytest.raises(ValueError):
                make_ratings(CSV_TOP_CONTROVERSIAL_USERS_VALUES).users.top_controversial(-1)

        def test_top_controversial_correct_values(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_VALUES).users.top_controversial(3)
            assert result == {1: 4.0, 3: 0.67, 2: 0.0}

        def test_top_controversial_rounds_to_two_decimals(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_ROUNDING).users.top_controversial(1)
            assert result[1] == 1.56

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_TOP_CONTROVERSIAL_USERS_SINGLE, id="single_rating"),
                pytest.param(CSV_TOP_CONTROVERSIAL_USERS_IDENTICAL, id="identical_ratings"),
            ],
        )
        def test_top_controversial_zero_variance(self, make_ratings, content):
            result = make_ratings(content).users.top_controversial(1)
            assert result == {1: 0.0}

        @pytest.mark.parametrize(
            "content",
            [
                pytest.param(CSV_EMPTY_FILE, id="empty_file"),
                pytest.param(CSV_ONLY_HEADER, id="only_header"),
            ],
        )
        def test_top_controversial_no_data(self, make_ratings, content):
            result = make_ratings(content).users.top_controversial(5)
            assert result == {}

        def test_top_controversial_ties_limited_to_n(self, make_ratings):
            result = make_ratings(CSV_TOP_CONTROVERSIAL_USERS_TIES).users.top_controversial(2)
            assert len(result) == 2
            assert all(v == 4.0 for v in result.values())
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            