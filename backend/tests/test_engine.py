from copy import deepcopy

from app.engine import caesar, generate, logic_candidates, normalize, number_candidates, order_candidates, validate_game, validate_puzzle

from test_projects import config
from app.db import get_db
from app.models import Puzzle


def test_all_four_families_are_generated_and_valid():
    specs = generate(config())
    assert len(specs) == 6
    assert {spec["type"] for spec in specs} == {"cipher", "number_lock", "logic_grid", "sequence"}
    assert specs == generate(config())
    assert all(validate_puzzle(spec) == [] for spec in specs)


def test_many_seeds_keep_unique_solutions():
    for theme in ("museum", "agent", "library"):
        for count in (4, 6, 8):
            for seed in range(5):
                specs = generate({"theme": theme, "difficulty": "hard", "puzzle_count": count, "random_seed": seed})
                puzzles = [{**spec, "id": str(index), "dependencies": [] if index == 0 else [str(index - 1)]}
                    for index, spec in enumerate(specs)]
                assert validate_game(puzzles) == []


def test_cipher_and_number_solvers_detect_invalid_answers():
    cipher, number = generate(config())[:2]
    assert caesar(cipher["parameters"]["ciphertext"], -cipher["parameters"]["shift"]) == cipher["solution"]["answer"]
    assert normalize("  north  ") == "NORTH"
    assert number_candidates(number["parameters"]) == [number["solution"]["answer"]]
    number["solution"]["answer"] = "999"
    assert validate_puzzle(number)[0]["code"] == "INVALID_ANSWER"


def test_logic_and_sequence_uniqueness():
    _, _, logic, sequence = generate(config())[:4]
    assert len(logic_candidates(logic["parameters"]["clues"])) == 1
    assert order_candidates(sequence["parameters"]["items"], sequence["parameters"]["edges"]) == [sequence["solution"]["order"]]
    ambiguous = deepcopy(sequence)
    ambiguous["parameters"]["edges"] = []
    assert validate_puzzle(ambiguous)[0]["code"] == "MULTIPLE_SOLUTIONS"


def test_hints_story_and_visible_lock_clues_are_checked():
    cipher, number = generate(config())[:2]
    cipher["hints"][1] = "Move each letter back by 1 place."
    assert any(error["code"] == "INVALID_HINT" for error in validate_puzzle(cipher))
    cipher = generate(config())[0]
    cipher["parameters"]["story"] = f"The answer is {cipher['solution']['answer']}."
    assert any(error["code"] == "STORY_CONSTRAINT_MISMATCH" for error in validate_puzzle(cipher))
    number["parameters"]["prompt"] = "Guess a code."
    assert any(error["code"] == "MISSING_CLUE" for error in validate_puzzle(number))
    assert validate_puzzle({"type": "cipher"})[0]["code"] == "INVALID_SCHEMA"
    assert validate_game([{"type": "cipher"}])[0]["code"] == "INVALID_SCHEMA"


def test_graph_detects_cycle_and_missing_dependency():
    specs = generate(config())[:2]
    first, second = ({**spec, "id": str(index), "dependencies": []} for index, spec in enumerate(specs))
    second["dependencies"] = ["0"]
    assert validate_game([first, second]) == []
    first["dependencies"] = ["1"]
    assert any(error["code"] == "CIRCULAR_DEPENDENCY" for error in validate_game([first, second]))
    first["dependencies"] = ["missing"]
    assert any(error["code"] == "MISSING_CLUE" for error in validate_game([first, second]))


def test_api_generate_validate_and_edit(client):
    project_id = client.post("/api/v1/projects", json=config()).json()["id"]
    result = client.post(f"/api/v1/projects/{project_id}/generate")
    assert result.status_code == 200
    puzzles = result.json()["puzzles"]
    assert len(puzzles) == 6
    assert all(puzzles[index]["dependencies"] == [puzzles[index - 1]["id"]] for index in range(1, 6))
    validation = client.post(f"/api/v1/projects/{project_id}/validate")
    assert validation.status_code == 200
    assert validation.json()["passed"] is True
    edited = client.patch(f"/api/v1/puzzles/{puzzles[0]['id']}", json={"title": "New inscription"})
    assert edited.status_code == 200
    assert client.get(f"/api/v1/projects/{project_id}").json()["status"] == "generated"
    assert client.post(f"/api/v1/projects/{project_id}/validate").json()["passed"] is True


def test_bounded_repair_preserves_unaffected_puzzles(client):
    project_id = client.post("/api/v1/projects", json=config()).json()["id"]
    original = client.post(f"/api/v1/projects/{project_id}/generate").json()["puzzles"]
    damaged_id = original[1]["id"]
    session_generator = client.app.dependency_overrides[get_db]()
    session = next(session_generator)
    damaged = session.get(Puzzle, damaged_id)
    damaged.solution_json = {"answer": "999"}
    session.commit()
    session_generator.close()
    assert not client.post(f"/api/v1/projects/{project_id}/validate").json()["passed"]
    repaired = client.post(f"/api/v1/projects/{project_id}/repair").json()
    assert repaired["passed"] is True
    assert repaired["repaired_puzzle_ids"] == [damaged_id]
    after = client.get(f"/api/v1/projects/{project_id}/puzzles").json()
    assert after[0]["solution"] == original[0]["solution"]
    assert after[2]["solution"] == original[2]["solution"]
    assert after[1]["solution"]["answer"] != "999"
