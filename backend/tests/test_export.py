from io import BytesIO

from pypdf import PdfReader

from app import main
from app.export import create_html
from test_projects import config


def test_html_escapes_embedded_text():
    project = {**config(), "id": "safe", "title": "</script><script>alert(1)</script>"}
    html = create_html(project, [])
    assert html.count("</script>") == 2
    assert "<script>alert(1)</script>" not in html
    assert "\\u003c/script\\u003e" in html
    assert "https://" not in html


def test_export_requires_validation_and_produces_separate_pdfs(client, tmp_path, monkeypatch):
    monkeypatch.setattr(main, "EXPORT_ROOT", tmp_path.resolve())
    project_id = client.post("/api/v1/projects", json=config()).json()["id"]
    assert client.post(f"/api/v1/projects/{project_id}/export/html").status_code == 409
    client.post(f"/api/v1/projects/{project_id}/generate")
    assert client.post(f"/api/v1/projects/{project_id}/validate").json()["passed"]
    html_export = client.post(f"/api/v1/projects/{project_id}/export/html")
    assert html_export.status_code == 200
    html = client.get(html_export.json()["download_url"]).text
    assert "The Midnight Museum" in html
    assert "fetch(" not in html
    assert "Star Diamond" in html
    pdf_export = client.post(f"/api/v1/projects/{project_id}/export/pdf")
    assert pdf_export.status_code == 200
    body = pdf_export.json()
    handout = client.get(body["handout"]["download_url"]).content
    answer_key = client.get(body["answer_key"]["download_url"]).content
    assert handout.startswith(b"%PDF") and answer_key.startswith(b"%PDF")
    handout_text = " ".join(page.extract_text() for page in PdfReader(BytesIO(handout)).pages)
    key_text = " ".join(page.extract_text() for page in PdfReader(BytesIO(answer_key)).pages)
    assert "The Midnight Museum" in handout_text
    assert "Answer:" in key_text
    assert "Answer: " + client.get(f"/api/v1/projects/{project_id}/puzzles").json()[0]["solution"]["answer"] in key_text
