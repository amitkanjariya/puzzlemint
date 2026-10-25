"""Deterministic puzzle construction and independent, bounded validation."""

from itertools import permutations, product
from random import Random


WORDS = {
    "museum": ["NORTH", "GALLERY", "DIAMOND", "ARCHIVE", "VAULT", "STATUE"],
    "agent": ["SHADOW", "SIGNAL", "CIPHER", "MISSION", "VECTOR", "ACCESS"],
    "library": ["LANTERN", "CHAPTER", "SECRET", "PORTAL", "WISDOM", "SCROLL"],
}
PEOPLE = ["Ari", "Bea", "Cleo"]
OBJECTS = ["key", "map", "lens"]
PLACES = ["atrium", "vault", "tower"]
EVENTS = {
    "museum": ["inspect the ticket", "open the archive", "trace the curator", "enter the vault"],
    "agent": ["decode the signal", "find the contact", "disable the alarm", "secure the dossier"],
    "library": ["read the index", "find the lantern", "open the passage", "recover the book"],
}


def normalize(answer: str) -> str:
    return " ".join(answer.strip().upper().split())


def caesar(text: str, shift: int) -> str:
    return "".join(chr((ord(c) - 65 + shift) % 26 + 65) if "A" <= c <= "Z" else c for c in text.upper())


def number_candidates(params: dict) -> list[str]:
    matches = []
    for a, b, c in product(range(10), repeat=3):
        if a == 0:
            continue
        if a + b + c == params["sum"] and a - b == params["first_minus_second"] and b - c == params["second_minus_third"]:
            matches.append(f"{a}{b}{c}")
    return matches


def logic_candidates(clues: list[dict]) -> list[dict]:
    matches = []
    for object_perm in permutations(OBJECTS):
        for place_perm in permutations(PLACES):
            assignment = {person: {"object": obj, "place": place} for person, obj, place in zip(PEOPLE, object_perm, place_perm)}
            if all(_clue_holds(assignment, clue) for clue in clues):
                matches.append(assignment)
    return matches


def _clue_holds(assignment: dict, clue: dict) -> bool:
    if clue["kind"] == "person_object":
        truth = assignment[clue["person"]]["object"] == clue["object"]
    elif clue["kind"] == "person_place":
        truth = assignment[clue["person"]]["place"] == clue["place"]
    elif clue["kind"] == "object_place":
        person = next(p for p in PEOPLE if assignment[p]["object"] == clue["object"])
        truth = assignment[person]["place"] == clue["place"]
    else:
        return False
    return truth == clue["is"]


def clue_text(clue: dict) -> str:
    verb = "has" if clue["kind"] == "person_object" else "visits"
    if clue["kind"] == "object_place":
        return f"The {clue['object']} is {'in' if clue['is'] else 'not in'} the {clue['place']}."
    subject = clue["person"]
    object_name = clue.get("object", clue.get("place"))
    return f"{subject} {'does not have' if not clue['is'] and verb == 'has' else 'does not visit' if not clue['is'] else verb} the {object_name}."


def order_candidates(items: list[str], edges: list[list[str]]) -> list[list[str]]:
    if len(items) > 6 or len(set(items)) != len(items):
        return []
    return [list(order) for order in permutations(items) if all(order.index(before) < order.index(after) for before, after in edges)]


def _cipher(rng: Random, theme: str, position: int, difficulty: str) -> dict:
    word = WORDS[theme][(position + rng.randrange(len(WORDS[theme]))) % len(WORDS[theme])]
    shift = rng.choice(range(2, 6) if difficulty == "easy" else range(4, 13) if difficulty == "medium" else range(10, 25))
    return {
        "type": "cipher",
        "title": "The encoded inscription",
        "parameters": {"prompt": "Decode the inscription. It names the next lead.", "ciphertext": caesar(word, shift), "shift": shift},
        "solution": {"answer": word},
        "hints": ["Each letter has been shifted through the alphabet.", f"Move each letter back by {shift} places.", "Wrap around from A to Z when moving backward."],
    }


def _number(rng: Random, theme: str, position: int, difficulty: str) -> dict:
    a, b, c = rng.randint(2, 8), rng.randint(1, 8), rng.randint(0, 8)
    params = {"sum": a + b + c, "first_minus_second": a - b, "second_minus_third": b - c}
    params["prompt"] = "A three-digit lock guards the next room. The digits add to {sum}. The first minus the second is {first_minus_second}. The second minus the third is {second_minus_third}.".format(**params)
    return {
        "type": "number_lock",
        "title": "The three-digit lock",
        "parameters": params,
        "solution": {"answer": f"{a}{b}{c}"},
        "hints": ["Call the digits A, B, and C.", f"Use A − B = {a-b} and B − C = {b-c}.", f"Their sum is {a+b+c}; the first digit cannot be zero."],
    }


def _logic(rng: Random, theme: str, position: int, difficulty: str) -> dict:
    objects = rng.sample(OBJECTS, 3)
    places = rng.sample(PLACES, 3)
    answer = {person: {"object": obj, "place": place} for person, obj, place in zip(PEOPLE, objects, places)}
    candidates = []
    for person in PEOPLE:
        for obj in OBJECTS:
            candidates.append({"kind": "person_object", "person": person, "object": obj, "is": answer[person]["object"] == obj})
        for place in PLACES:
            candidates.append({"kind": "person_place", "person": person, "place": place, "is": answer[person]["place"] == place})
    for obj in OBJECTS:
        holder = next(person for person in PEOPLE if answer[person]["object"] == obj)
        for place in PLACES:
            candidates.append({"kind": "object_place", "object": obj, "place": place, "is": answer[holder]["place"] == place})
    rng.shuffle(candidates)
    clues = []
    for clue in candidates:
        clues.append(clue)
        if len(logic_candidates(clues)) == 1:
            break
    for clue in clues[:]:
        reduced = [other for other in clues if other is not clue]
        if len(logic_candidates(reduced)) == 1:
            clues = reduced
    featured = PEOPLE[position % 3]
    target = answer[featured]
    return {
        "type": "logic_grid",
        "title": "The witnesses' clues",
        "parameters": {"prompt": f"Three witnesses each carried one object and visited one place. Use the clues to identify {featured}'s object and place. Enter them as OBJECT, PLACE.", "people": PEOPLE, "objects": OBJECTS, "places": PLACES, "clues": clues, "featured": featured},
        "solution": {"answer": f"{target['object'].upper()}, {target['place'].upper()}", "assignment": answer},
        "hints": ["Every person, object, and place is used exactly once.", "Mark impossible pairings before selecting possible ones.", f"Focus on the clues involving {featured} and related objects."],
    }


def _sequence(rng: Random, theme: str, position: int, difficulty: str) -> dict:
    order = rng.sample(EVENTS[theme], 4)
    edges = [[order[i], order[i + 1]] for i in range(3)]
    shown = rng.sample(order, 4)
    return {
        "type": "sequence",
        "title": "The recovered timeline",
        "parameters": {"prompt": "Put the four events in the only order that satisfies every before/after clue.", "items": shown, "edges": edges},
        "solution": {"answer": " | ".join(order), "order": order},
        "hints": ["Find the event that has no earlier requirement.", "Follow the before/after arrows one step at a time.", f"The first event is: {order[0]}."],
    }


FAMILIES = [_cipher, _number, _logic, _sequence]


def generate(config: dict) -> list[dict]:
    rng = Random(config["random_seed"])
    puzzles = []
    for index in range(config["puzzle_count"]):
        puzzle = FAMILIES[index % 4](rng, config["theme"], index, config["difficulty"])
        puzzle["position"] = index
        puzzle["difficulty"] = config["difficulty"]
        puzzle["parameters"]["story"] = (
            "The trail begins here. Each solved clue unlocks the next chamber."
            if index == 0 else f"The clue from chamber {index} unlocks this chamber."
        )
        puzzles.append(puzzle)
    return puzzles


def validate_puzzle(puzzle: dict) -> list[dict]:
    errors = []
    kind, params, solution = puzzle["type"], puzzle["parameters"], puzzle["solution"]
    try:
        if kind == "cipher":
            if not 1 <= params["shift"] <= 25 or caesar(params["ciphertext"], -params["shift"]) != normalize(solution["answer"]):
                errors.append({"code": "INVALID_ANSWER", "message": "Cipher does not decode to its answer"})
        elif kind == "number_lock":
            candidates = number_candidates(params)
            if not candidates:
                errors.append({"code": "NO_VALID_SOLUTION", "message": "Lock clues have no solution"})
            elif len(candidates) > 1:
                errors.append({"code": "MULTIPLE_SOLUTIONS", "message": "Lock clues are ambiguous"})
            elif candidates[0] != solution["answer"]:
                errors.append({"code": "INVALID_ANSWER", "message": "Lock answer does not match clues"})
        elif kind == "logic_grid":
            clues = params["clues"]
            if not clues:
                errors.append({"code": "MISSING_CLUE", "message": "Logic puzzle has no clues"})
            else:
                candidates = logic_candidates(clues)
                if not candidates:
                    errors.append({"code": "NO_VALID_SOLUTION", "message": "Logic clues contradict each other"})
                elif len(candidates) > 1:
                    errors.append({"code": "MULTIPLE_SOLUTIONS", "message": "Logic clues allow several grids"})
                else:
                    featured = params["featured"]
                    target = candidates[0][featured]
                    if normalize(solution["answer"]) != f"{target['object'].upper()}, {target['place'].upper()}":
                        errors.append({"code": "INVALID_ANSWER", "message": "Logic answer does not match clues"})
        elif kind == "sequence":
            orders = order_candidates(params["items"], params["edges"])
            if not orders:
                errors.append({"code": "NO_VALID_SOLUTION", "message": "Timeline constraints are contradictory"})
            elif len(orders) > 1:
                errors.append({"code": "MULTIPLE_SOLUTIONS", "message": "Timeline has several valid orders"})
            elif orders[0] != solution["order"]:
                errors.append({"code": "INVALID_ANSWER", "message": "Timeline answer does not match clues"})
        else:
            errors.append({"code": "INVALID_TYPE", "message": "Unsupported puzzle family"})
    except (KeyError, TypeError, ValueError, StopIteration, IndexError):
        errors.append({"code": "INVALID_SCHEMA", "message": "Puzzle data is incomplete or malformed"})
    hints = puzzle.get("hints", [])
    if len(hints) != 3 or any(not isinstance(hint, str) or not hint.strip() for hint in hints):
        errors.append({"code": "INVALID_HINT", "message": "Three nonempty hints are required"})
    return errors


def validate_game(puzzles: list[dict]) -> list[dict]:
    errors = []
    ids = {puzzle["id"] for puzzle in puzzles}
    by_id = {puzzle["id"]: puzzle for puzzle in puzzles}
    if len(ids) != len(puzzles):
        errors.append({"code": "INVALID_SCHEMA", "message": "Puzzle IDs must be unique"})
    for puzzle in puzzles:
        errors.extend({**error, "puzzle_id": puzzle["id"]} for error in validate_puzzle(puzzle))
        for dependency in puzzle.get("dependencies", []):
            if dependency not in ids:
                errors.append({"code": "MISSING_CLUE", "message": "A dependency is missing", "puzzle_id": puzzle["id"]})
    if not puzzles:
        errors.append({"code": "UNREACHABLE_STAGE", "message": "Adventure contains no puzzles"})
        return errors
    # Resolve a playable order. A cycle or a missing prerequisite leaves nodes unresolved.
    completed = set()
    while True:
        ready = {p["id"] for p in puzzles if p["id"] not in completed and set(p.get("dependencies", [])) <= completed}
        if not ready:
            break
        completed |= ready
    if len(completed) < len(puzzles):
        unresolved = ids - completed
        code = "CIRCULAR_DEPENDENCY" if all(set(by_id[node].get("dependencies", [])) <= ids for node in unresolved) else "UNREACHABLE_STAGE"
        errors.append({"code": code, "message": "Some stages cannot be unlocked", "puzzle_ids": sorted(unresolved)})
    return errors
