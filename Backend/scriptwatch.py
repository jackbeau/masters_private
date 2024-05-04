# from fuzzysearch import find_near_matches

# matches = find_near_matches('Hello, how are you feeling today sir', 'Hello, how are you feeling today', max_l_dist=25)

# print(matches)

from thefuzz import fuzz
import time

def search_with_similarity(text, target_string):
    start_time = time.time()
    lines = text.split('\n')  # Split text into lines, adjust as needed

    best_score = 0
    match = ""

    for line in lines:
        similarity_score = fuzz.partial_ratio(line.lower(), target_string.lower())

        if similarity_score > best_score:
            best_score = similarity_score
            match = line
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Time elapsed: {elapsed_time} seconds')
        
    print(f"Best match: '{match.strip()}' (Similarity: {best_score}%)")

text = open('script.txt', 'r')

large_text = text.read()

target_string = " tribe died. The weight commuters is worked for thousands of years, is that sure, you may have disliked a neighbour, but because you lived close to each other, you also rooted for the same space."

search_with_similarity(large_text, target_string)