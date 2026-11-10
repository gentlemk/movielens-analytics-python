from collections import Counter
from datetime import datetime, timezone


class Tags:
    """
    Analyzing data from tags.csv
    """
    def __init__(self, path_to_the_file='./data/tags.csv'):
        self.data = self._read_data(path_to_the_file)
        
        
    def _read_data(self, path_to_the_file):
        try:
            with open(path_to_the_file, "r", encoding="utf-8") as file:
                data = self._process_data(file)
            return data
        except (FileNotFoundError, PermissionError) as e:
            print(f'file access error {path_to_the_file}: {e}')
        except Exception as e:
            print(f'unexpected error: {e}')
        
        return []

    
    
    def _process_data(self, file):
        data = []
        header = file.readline().strip().split(',')
        if header != ['userId','movieId','tag','timestamp']:
            raise ValueError("Incorrect header: '{header}'\nexpected: 'userId,movieId,tag,timestamp'\nfile: '{file}'")
        
        for line in file:
            record = line.strip().split(',')
            if len(record) != 4:
                # print(f'Пропущена битая строка: {record}')
                continue
            
            try:
                values = [int(record[0]), int(record[1]), record[2], int(record[3])]
                self._validation_data(values)
                data.append(dict(zip(header, values)))
            except ValueError as e:
                # print(f'Пропущена битая строка: {line.strip()}')
                continue
                
        return data
    
    @staticmethod
    def _validation_data(values):
        if Tags._is_valid_user_id(values[0]) and \
            Tags._is_valid_movie_id(values[1]) and \
            Tags._is_valid_tag(values[2]) and \
            Tags._is_correct_timestamp(values[3]):
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
    def _is_valid_tag(tag):
        return tag != ""
        
    @staticmethod
    def _is_correct_timestamp(timestamp):
        now_utc = datetime.now(timezone.utc)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc) <= now_utc
                
    @staticmethod
    def _check_n(n):
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError(f"Incorrect param n: {n!r}")
                          
        
    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict 
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        self._check_n(n)
        top_tags = self._get_tags_for_func(n, metric_func=lambda tag: len(tag.split()))
        return dict(top_tags)


    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        self._check_n(n)
        top_tags = self._get_tags_for_func(n, metric_func=len)
        return [tag for tag, _ in top_tags]


    def _get_tags_for_func(self, n, metric_func):
        unique_tags = self._get_unique_tags()
        count_tags = {
            tag: metric_func(tag)
            for tag in unique_tags
        }
        top_tags = sorted(
            count_tags.items(), 
            key=lambda item: (-item[1], item[0].lower())
        )[:n]
        return top_tags
    
    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and 
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        self._check_n(n)
        long_tags = self.longest(n)
        most_words_tags = self.most_words(n)
        return set(long_tags) & set(most_words_tags)
        
    def most_popular(self, n):
        """
        The method returns the most popular tags. 
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        self._check_n(n)
        tags = self._get_tags()
        counter = Counter(tags)
        return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0].lower()))[:n])
        
    
    def _check_word(self, word):
        if not isinstance(word, str) or not word.strip():
            raise ValueError("Incorrect param word: {word!r}")
        
    def _get_tags(self):
        return [record['tag'] for record in self.data]
    
    def _get_unique_tags(self):
        return set(self._get_tags())

    def tags_with(self, word: str):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        self._check_word(word)
        unique_tags = self._get_unique_tags()
        top_tags = [tag for tag in unique_tags if word.lower() in tag.lower()]
        return sorted(top_tags)
