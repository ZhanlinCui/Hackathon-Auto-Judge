import httpx

BASE_URL = "http://127.0.0.1:8000/api"
_client = httpx.Client(base_url=BASE_URL, timeout=120)


def health():
    return _client.get("/health").json()


def list_hackathons():
    return _client.get("/hackathons").json()


def create_hackathon(name: str, description: str = ""):
    return _client.post("/hackathons", json={"name": name, "description": description}).json()


def get_hackathon(hid: int):
    return _client.get(f"/hackathons/{hid}").json()


def list_projects(hid: int):
    return _client.get(f"/hackathons/{hid}/projects").json()


def get_project(pid: int):
    return _client.get(f"/projects/{pid}").json()


def get_project_data(pid: int):
    resp = _client.get(f"/projects/{pid}/data")
    if resp.status_code == 200:
        return resp.json()
    return None


def import_csv(hid: int, file_bytes: bytes, filename: str):
    return _client.post(
        f"/hackathons/{hid}/import",
        files={"file": (filename, file_bytes, "text/csv")},
    ).json()


def scrape_all(hid: int):
    return _client.post(f"/hackathons/{hid}/scrape").json()


def get_config():
    return _client.get("/config").json()


def update_config(key: str, value: str):
    return _client.put("/config", json={"key": key, "value": value}).json()


def update_config_batch(items: list[dict]):
    return _client.put("/config/batch", json=items).json()


def list_rubrics(hid: int):
    return _client.get(f"/hackathons/{hid}/rubrics").json()


def create_rubric(hid: int, data: dict):
    return _client.post(f"/hackathons/{hid}/rubrics", json=data).json()


def update_rubric(rid: int, data: dict):
    return _client.put(f"/rubrics/{rid}", json=data).json()


def delete_rubric(rid: int):
    return _client.delete(f"/rubrics/{rid}").json()


def list_hard_rules(hid: int):
    return _client.get(f"/hackathons/{hid}/hard-rules").json()


def create_hard_rule(hid: int, data: dict):
    return _client.post(f"/hackathons/{hid}/hard-rules", json=data).json()


def delete_hard_rule(rid: int):
    return _client.delete(f"/hard-rules/{rid}").json()


def start_evaluation(hid: int):
    return _client.post(f"/hackathons/{hid}/evaluate").json()


def get_evaluation_run(run_id: int):
    return _client.get(f"/evaluation-runs/{run_id}").json()


def get_scores(run_id: int):
    return _client.get(f"/evaluation-runs/{run_id}/scores").json()


def get_hard_rule_results(run_id: int):
    return _client.get(f"/evaluation-runs/{run_id}/hard-rule-results").json()


def get_leaderboard(hid: int, run_id: int | None = None):
    params = {}
    if run_id:
        params["run_id"] = run_id
    return _client.get(f"/hackathons/{hid}/leaderboard", params=params).json()


def export_excel(hid: int, run_id: int | None = None):
    params = {}
    if run_id:
        params["run_id"] = run_id
    resp = _client.get(f"/hackathons/{hid}/export", params=params)
    if resp.status_code == 200:
        return resp.content
    return None
