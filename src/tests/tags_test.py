import pytest

from movielens_impl import Tags

CSV_WITH_EMPTY_LINES = """\
userId,movieId,tag,timestamp

1,3578,Epic,1528152469
       
1,3578,history,1528152467


1,3578,imdb top 250,1528152498
2,3578,revenge,1528152496
2,3578,Rome,1528152463

2,3578,Russell Crowe,1528152465



"""

CSV_EMPTY_FILE = ""

CSV_ONLY_HEADER = "\
userId,movieId,tag,timestamp\n"

CSV_READ_SMALL = """\
userId,movieId,tag,timestamp
1,1,funny,1445714994
2,2,epic,1445714996
3,3,classic,1445714992
"""

CSV_TAGS_WORDS = """\
userId,movieId,tag,timestamp
1,1,one,1000000000
1,2,two words,1000000000
1,3,three words here,1000000000
1,4,four words are here,1000000000
"""

CSV_TAGS_LENGTHS = """\
userId,movieId,tag,timestamp
1,1,a,1000000000
1,2,abc,1000000000
1,3,abcde,1000000000
1,4,abcdefg,1000000000
"""

CSV_TAGS_INTERSECTION = """\
userId,movieId,tag,timestamp
1,1,aa,1000000000
1,2,bb cc,1000000000
1,3,dd ee ff,1000000000
1,4,gg hh ii jj,1000000000
"""

CSV_TAGS_POPULAR = """\
userId,movieId,tag,timestamp
1,1,alpha,1000000000
2,1,alpha,1000000000
3,1,beta,1000000000
4,1,beta,1000000000
5,1,beta,1000000000
6,1,gamma,1000000000
"""

CSV_TAGS_WITH = """\
userId,movieId,tag,timestamp
1,1,Alpha,1000000000
1,2,alphabet,1000000000
1,3,BETA,1000000000
1,4,beta ray,1000000000
1,5,gamma,1000000000
"""

CSV_TAGS_DUPLICATES = """\
userId,movieId,tag,timestamp
1,1,funny,1000000000
2,1,funny,1000000000
3,1,Funny,1000000000
1,2,epic,1000000000
"""

@pytest.fixture
def make_tags(tmp_path):
    def _create(content, count=1000):
        file_path = tmp_path / "test_tags.csv"
        file_path.write_text(content, encoding='utf-8')
        return Tags(str(file_path))
    return _create


class TestTags:
    def test_read_valid_file(self, make_tags):
        result = make_tags(CSV_READ_SMALL).data

        assert isinstance(result, list)
        assert len(result) == 3
        assert isinstance(result[0], dict)

        first = result[0]
        last = result[-1]
        assert set(first.keys()) == {"userId", "movieId", "tag", "timestamp"}

        assert isinstance(first["userId"], int)
        assert isinstance(first["movieId"], int)
        assert isinstance(first["tag"], str)
        assert isinstance(first["timestamp"], int)

        assert first == {
            "userId": 1, "movieId": 1, "tag": "funny", "timestamp": 1445714994,
        }
        assert last == {
            "userId": 3, "movieId": 3, "tag": "classic", "timestamp": 1445714992,
        }

    def test_read_with_empty_lines(self, make_tags):
        result = make_tags(CSV_WITH_EMPTY_LINES).data
        assert len(result) == 6
        assert result[0]["tag"] == "Epic"
        assert result[-1]["tag"] == "Russell Crowe"

    @pytest.mark.parametrize(
        "content",
        [
            pytest.param(CSV_EMPTY_FILE, id="empty_file"),
            pytest.param(CSV_ONLY_HEADER, id="only_header"),
        ],
    )
    def test_read_no_data_rows(self, make_tags, content):
        result = make_tags(content).data
        assert result == []

    class TestValidationData:
        class TestIsValidUserId:
            @pytest.mark.parametrize("value, expected", [
                pytest.param(1, True, id="positive"),
                pytest.param(0, False, id="zero"),
                pytest.param(-1, False, id="negative"),
            ])
            def test_is_valid_user_id(self, value, expected):
                assert Tags._is_valid_user_id(value) is expected

        class TestIsValidMovieId:
            @pytest.mark.parametrize("value, expected", [
                pytest.param(1, True, id="positive"),
                pytest.param(0, False, id="zero"),
                pytest.param(-1, False, id="negative"),
            ])
            def test_is_valid_movie_id(self, value, expected):
                assert Tags._is_valid_movie_id(value) is expected

        class TestIsValidTag:
            @pytest.mark.parametrize("value, expected", [
                pytest.param("funny", True, id="non_empty"),
                pytest.param(" ", True, id="space_only"),
                pytest.param("", False, id="empty"),
            ])
            def test_is_valid_tag(self, value, expected):
                assert Tags._is_valid_tag(value) is expected

        class TestIsValidTimestamp:
            def test_past_is_valid(self):
                assert Tags._is_correct_timestamp(1_000_000_000) is True

            def test_future_is_invalid(self):
                assert Tags._is_correct_timestamp(4_102_444_800) is False  # 2100

        class TestValidationDataCombined:
            def test_all_valid_returns_true(self):
                assert Tags._validation_data([1, 1, "funny", 1_000_000_000]) is True

            @pytest.mark.parametrize("values", [
                pytest.param([-1, 1, "funny", 1_000_000_000], id="bad_user"),
                pytest.param([1, -1, "funny", 1_000_000_000], id="bad_movie"),
                pytest.param([1, 1, "", 1_000_000_000], id="bad_tag"),
                pytest.param([1, 1, "funny", 4_102_444_800], id="bad_ts"),
            ])
            def test_invalid_raises(self, values):
                with pytest.raises(ValueError):
                    Tags._validation_data(values)
    
    class TestMostWords:
        def test_returns_dict(self, make_tags):
            result = make_tags(CSV_TAGS_WORDS).most_words(2)
            assert isinstance(result, dict)

        def test_key_value_types(self, make_tags):
            result = make_tags(CSV_TAGS_WORDS).most_words(4)
            assert len(result) > 0
            for tag, count in result.items():
                assert isinstance(tag, str)
                assert isinstance(count, int)

        def test_correct_counts(self, make_tags):
            result = make_tags(CSV_TAGS_WORDS).most_words(4)
            assert result == {
                "four words are here": 4,
                "three words here": 3,
                "two words": 2,
                "one": 1,
            }

        @pytest.mark.parametrize("n, expected_len", [
            pytest.param(1, 1, id="n1"),
            pytest.param(2, 2, id="n2"),
            pytest.param(10, 4, id="n_more"),
        ])
        def test_limits_to_n(self, make_tags, n, expected_len):
            assert len(make_tags(CSV_TAGS_WORDS).most_words(n)) == expected_len

        def test_n_zero(self, make_tags):
            assert make_tags(CSV_TAGS_WORDS).most_words(0) == {}

        def test_n_negative(self, make_tags):
            with pytest.raises(ValueError):
                make_tags(CSV_TAGS_WORDS).most_words(-1)

        @pytest.mark.parametrize("content", [
            pytest.param(CSV_EMPTY_FILE, id="empty_file"),
            pytest.param(CSV_ONLY_HEADER, id="only_header"),
        ])
        def test_no_data(self, make_tags, content):
            assert make_tags(content).most_words(5) == {}

        def test_drops_duplicates(self, make_tags):
            result = make_tags(CSV_TAGS_DUPLICATES).most_words(10)
            assert set(result) == {"funny", "Funny", "epic"}
    
    class TestLongest:
        def test_returns_list(self, make_tags):
            result = make_tags(CSV_TAGS_LENGTHS).longest(2)
            assert isinstance(result, list)
            assert all(isinstance(t, str) for t in result)

        def test_correct_values(self, make_tags):
            result = make_tags(CSV_TAGS_LENGTHS).longest(4)
            assert result == ["abcdefg", "abcde", "abc", "a"]

        @pytest.mark.parametrize("n, expected_len", [
            pytest.param(1, 1, id="n1"),
            pytest.param(2, 2, id="n2"),
            pytest.param(10, 4, id="n_more"),
        ])
        def test_limits_to_n(self, make_tags, n, expected_len):
            assert len(make_tags(CSV_TAGS_LENGTHS).longest(n)) == expected_len

        def test_n_zero(self, make_tags):
            assert make_tags(CSV_TAGS_LENGTHS).longest(0) == []

        def test_n_negative(self, make_tags):
            with pytest.raises(ValueError):
                make_tags(CSV_TAGS_LENGTHS).longest(-1)

        @pytest.mark.parametrize("content", [
            pytest.param(CSV_EMPTY_FILE, id="empty_file"),
            pytest.param(CSV_ONLY_HEADER, id="only_header"),
        ])
        def test_no_data(self, make_tags, content):
            assert make_tags(content).longest(5) == []

        def test_drops_duplicates(self, make_tags):
            result = make_tags(CSV_TAGS_DUPLICATES).longest(10)
            assert sorted(result) == sorted(["funny", "Funny", "epic"])
    
    class TestMostWordsAndLongest:
        def test_returns_set(self, make_tags):
            result = make_tags(CSV_TAGS_INTERSECTION).most_words_and_longest(2)
            assert isinstance(result, set)

        def test_correct_intersection(self, make_tags):
            result = make_tags(CSV_TAGS_INTERSECTION).most_words_and_longest(2)
            assert result == {"dd ee ff", "gg hh ii jj"}

        def test_no_intersection(self, make_tags):
            content = "".join([
                "userId,movieId,tag,timestamp\n"
                "1,1,aa,1000000000\n"          
                "1,2,bbbbbbbb,1000000000\n"    
            ])
            result = make_tags(content).most_words_and_longest(1)
            assert result == set()  

        def test_n_zero(self, make_tags):
            assert make_tags(CSV_TAGS_INTERSECTION).most_words_and_longest(0) == set()

        def test_n_negative(self, make_tags):
            with pytest.raises(ValueError):
                make_tags(CSV_TAGS_INTERSECTION).most_words_and_longest(-1)
    
    class TestMostPopular:
        def test_returns_dict(self, make_tags):
            result = make_tags(CSV_TAGS_POPULAR).most_popular(2)
            assert isinstance(result, dict)

        def test_key_value_types(self, make_tags):
            result = make_tags(CSV_TAGS_POPULAR).most_popular(3)
            for tag, count in result.items():
                assert isinstance(tag, str)
                assert isinstance(count, int)

        def test_correct_counts(self, make_tags):
            result = make_tags(CSV_TAGS_POPULAR).most_popular(3)
            assert result == {"beta": 3, "alpha": 2, "gamma": 1}

        @pytest.mark.parametrize("n, expected_len", [
            pytest.param(1, 1, id="n1"),
            pytest.param(2, 2, id="n2"),
            pytest.param(10, 3, id="n_more"),
        ])
        def test_limits_to_n(self, make_tags, n, expected_len):
            assert len(make_tags(CSV_TAGS_POPULAR).most_popular(n)) == expected_len

        def test_n_zero(self, make_tags):
            assert make_tags(CSV_TAGS_POPULAR).most_popular(0) == {}

        def test_n_negative(self, make_tags):
            with pytest.raises(ValueError):
                make_tags(CSV_TAGS_POPULAR).most_popular(-1)

        @pytest.mark.parametrize("content", [
            pytest.param(CSV_EMPTY_FILE, id="empty_file"),
            pytest.param(CSV_ONLY_HEADER, id="only_header"),
        ])
        def test_no_data(self, make_tags, content):
            assert make_tags(content).most_popular(5) == {}

        def test_drops_duplicates_counted(self, make_tags):
            result = make_tags(CSV_TAGS_DUPLICATES).most_popular(10)
            assert result == {"funny": 2, "Funny": 1, "epic": 1}
    
    class TestTagsWith:
        def test_returns_list(self, make_tags):
            result = make_tags(CSV_TAGS_WITH).tags_with("alpha")
            assert isinstance(result, list)
            assert all(isinstance(t, str) for t in result)

        def test_case_insensitive(self, make_tags):
            result = make_tags(CSV_TAGS_WITH).tags_with("ALPHA")
            assert result == ["Alpha", "alphabet"]

        def test_substring_match(self, make_tags):
            result = make_tags(CSV_TAGS_WITH).tags_with("beta")
            assert result == ["BETA", "beta ray"]

        def test_sorted_alphabetically(self, make_tags):
            result = make_tags(CSV_TAGS_WITH).tags_with("a")
            assert result == sorted(result)

        def test_no_matches(self, make_tags):
            assert make_tags(CSV_TAGS_WITH).tags_with("zzz") == []

        def test_drops_duplicates(self, make_tags):
            content = (
                "userId,movieId,tag,timestamp\n"
                "1,1,alpha,1000000000\n"
                "2,1,alpha,1000000000\n"
                "3,1,alphabet,1000000000\n"
            )
            result = make_tags(content).tags_with("alpha")
            assert result == ["alpha", "alphabet"]  # alpha один раз

        @pytest.mark.parametrize("word", [
            pytest.param(None, id="none"),
            pytest.param("", id="empty"),
            pytest.param("   ", id="spaces"),
            pytest.param(123, id="int"),
        ])
        def test_invalid_word_raises(self, make_tags, word):
            with pytest.raises(ValueError):
                make_tags(CSV_TAGS_WITH).tags_with(word)
        
    
    
    
    
    
    
    
    