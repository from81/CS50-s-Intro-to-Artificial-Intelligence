import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}
# names[row["name"].lower()] = {row["id"]}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}
# people[row["id"]] = {
#     "name": row["name"],
#     "birth": row["birth"],
#     "movies": set()
# }

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}
# movies[row["id"]] = {
#     "title": row["title"],
#     "year": row["year"],
#     "stars": set()
# }


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.

    Args:
        source: str of id
        target: str of id
    """

    """
    1. get all neighbors of source
    2. for each neighbor, check their neighbors
    3. repeat until target is found
    """

    queue = QueueFrontier()
    explored = set()

    neighbors = neighbors_for_person(source)
    # (movie_id, person_id)

    for neighbor in neighbors:
        node = Node(state=neighbor[1], action=neighbor[0], parent=source)

        if node not in explored:
            explored.add(node)
            queue.add(node)

        if node.state == target:
            # target found
            return [neighbor]


    while queue:
        node = queue.remove()
        neighbors = neighbors_for_person(node.state)

        for neighbor in neighbors:
            new_node = Node(state=neighbor[1], action=neighbor[0], parent=node)

            if new_node not in explored:
                explored.add(new_node)
                queue.add(new_node)

            if new_node.state == target:
                # target found
                degrees = []
                while type(new_node.parent) != str:
                    degrees.insert(0, (new_node.action, new_node.state))
                    new_node = new_node.parent

                import pdb; pdb.set_trace()
                return degrees
    return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
