def config():
    return {
        "title": "The Midnight Museum",
        "theme": "museum",
        "occasion": "Birthday",
        "difficulty": "medium",
        "duration_minutes": 30,
        "puzzle_count": 6,
        "random_seed": 42,
        "player_alias": "Aarav",
        "final_message": "Happy Birthday, Aarav!",
    }


def test_create_list_update_delete(client):
    response = client.post("/api/v1/projects", json=config())
    assert response.status_code == 201
    project = response.json()
    assert project["status"] == "draft"
    assert project["player_alias"] == "Aarav"
    assert len(client.get("/api/v1/projects").json()) == 1
    response = client.patch(f"/api/v1/projects/{project['id']}", json={"title": "Museum After Dark"})
    assert response.status_code == 200
    assert response.json()["title"] == "Museum After Dark"
    assert client.delete(f"/api/v1/projects/{project['id']}").status_code == 204
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 404


def test_rejects_invalid_input_and_unauthorized_request(client):
    response = client.post("/api/v1/projects", json={**config(), "puzzle_count": 100})
    assert response.status_code == 422
    response = client.get("/api/v1/projects", headers={"Authorization": "Bearer wrong"})
    assert response.status_code == 401
    assert client.post("/api/v1/projects", content=b"x" * 65537).status_code == 413


def test_duplicate_preserves_puzzles_but_requires_new_validation(client):
    original = client.post("/api/v1/projects", json=config()).json()
    client.post(f"/api/v1/projects/{original['id']}/generate")
    client.post(f"/api/v1/projects/{original['id']}/validate")
    duplicate = client.post(f"/api/v1/projects/{original['id']}/duplicate").json()
    assert duplicate["title"].endswith("(copy)")
    assert duplicate["status"] == "generated"
    puzzles = client.get(f"/api/v1/projects/{duplicate['id']}/puzzles").json()
    assert len(puzzles) == 6
    assert client.post(f"/api/v1/projects/{duplicate['id']}/validate").json()["passed"]
