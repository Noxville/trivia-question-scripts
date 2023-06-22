from itertools import combinations
from functools import lru_cache
from collections import defaultdict
import csv
from scipy.stats import gmean
  

class Performance:
    def __init__(self, line):
        assert len(line) == 7
        self.actor = line[0]
        self.actor_id = line[1]

        self.film = line[2]
        self.film_id = line[6]

        self.year = int(line[3])
        self.votes = int(line[4])
        self.rating = float(line[5])


def overlap(f1, f2):
    if f2 > f1:
        return overlap_ordered(f2, f1)
    return overlap_ordered(f1, f2)
    

@lru_cache(maxsize=None)
def overlap_ordered(f1, f2):
    assert f1 in movie_actors
    assert f2 in movie_actors
    return [o for o in movie_actors[f1] if o in movie_actors[f2]]


film_id_map, actor_id_map = {}, {}
actor_movies = defaultdict(list)
movie_actors = defaultdict(list)
vote_map = {}

with open('actorfilms.csv') as film_file:
    reader = csv.reader(film_file, delimiter=',', quotechar='"')
    next(reader) # skip header
    performances = [Performance(row) for row in reader]
    for p in performances:
        film_id_map[p.film_id] = p.film
        actor_id_map[p.actor_id] = p.actor
        actor_movies[p.actor_id].append(p)
        movie_actors[p.film_id].append(p.actor_id)
        vote_map[p.film_id] = p.votes

def print_review(rev):
    film_names = ", ".join([film_id_map[f] for f in rev[1]])
    print(f"Given {actor_id_map[rev[0]]}, actors common between films: {film_names} | actors: {rev[2]} | score: {rev[3]} ")

def evaluate_actor(actor_id):
    their_movies = [f.film_id for f in actor_movies[actor_id]]
    for films in combinations(their_movies, 3):
        common_ab = overlap(films[0], films[1]) 
        common_ac = overlap(films[0], films[2]) 
        common_bc = overlap(films[1], films[2]) 

        if len(common_ab) == 2 and len(common_ac) == 2 and len(common_bc) == 2: # There's another connection beyond the answer
            common_names = []
            for pair in [common_ab, common_ac, common_bc]:
                common_names.append([actor_id_map[p] for p in pair if p != actor_id][0])
            if len(set(common_names)) == 3:
                #print(f"Actors common between films: {film_id_map[films[0]]}, {film_id_map[films[1]]}, {film_id_map[films[2]]} = {common_names}")
                score = gmean([vote_map[f] for f in films])
                yield (actor_id, films, common_names, score)


reviews = []
valid_answers = [actor_id for actor_id, films in actor_movies.items() if len([f for f in films if f.year > 1980 and f.rating > 6.3]) >= 8]
print(f"{len(valid_answers)} valid center-answers")

for idx, actor in enumerate(valid_answers):
    print(f"{1 + idx} / {len(valid_answers)}")
    for review in evaluate_actor(actor):
        reviews.append(review)
reviews = sorted(reviews, key=lambda r: r[-1], reverse=True)

for r in reviews[:50]:
    print_review(r)

