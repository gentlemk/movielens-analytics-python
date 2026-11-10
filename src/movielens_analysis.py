from movielens_impl import Ratings, Movies, Tags, Links

if __name__ == '__main__':
    r = Ratings()
    
    print(r.movies_analytics.top_by_weighted_rating(100))
    # benchmark('r.movies.dist_by_year()', globals())
    