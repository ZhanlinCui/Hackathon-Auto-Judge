import httpx

BASE_URL = "http://127.0.0.1:8000/api"
_client = httpx.Client(base_url=BASE_URL, timeout=120)


def _get(path: str, **kwargs):
    resp = _client.get(path, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, **kwargs):
    resp = _client.post(path, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _put(path: str, **kwargs):
    resp = _client.put(path, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _delete(path: str, **kwargs):
    resp = _client.delete(path, **kwargs)
    resp.raise_for_status()
    return resp.json()


def health():
    return _get("/health")


def list_hackathons():
    return _get("/hackathons")


def create_hackathon(name: str, description: str = ""):
    return _post("/hackathons", json={"name": name, "description": description})


def get_hackathon(hid: int):
    return _get(f"/hackathons/{hid}")


def list_projects(hid: int):
    return _get(f"/hackathons/{hid}/projects")


def get_project(pid: int):
    return _get(f"/projects/{pid}")


def get_project_data(pid: int):
    resp = _client.get(f"/projects/{pid}/data")
    if resp.status_code == 200:
        return resp.json()
    return None


def import_csv(hid: int, file_bytes: bytes, filename: str):
    return _post(
        f"/hackathons/{hid}/import",
        files={"file": (filename, file_bytes, "text/csv")},
    )


def scrape_all(hid: int):
    return _post(f"/hackathons/{hid}/scrape")


def get_config():
    return _get("/config")


def update_config(key: str, value: str):
    return _put("/config", json={"key": key, "value": value})


def update_config_batch(items: list[dict]):
    return _put("/config/batch", json=items)


def list_rubrics(hid: int):
    return _get(f"/hackathons/{hid}/rubrics")


def create_rubric(hid: int, data: dict):
    return _post(f"/hackathons/{hid}/rubrics", json=data)


def update_rubric(rid: int, data: dict):
    return _put(f"/rubrics/{rid}", json=data)


def delete_rubric(rid: int):
    return _delete(f"/rubrics/{rid}")


def list_hard_rules(hid: int):
    return _get(f"/hackathons/{hid}/hard-rules")


def create_hard_rule(hid: int, data: dict):
    return _post(f"/hackathons/{hid}/hard-rules", json=data)


def delete_hard_rule(rid: int):
    return _delete(f"/hard-rules/{rid}")


def start_evaluation(hid: int):
    return _post(f"/hackathons/{hid}/evaluate")


def get_evaluation_run(run_id: int):
    return _get(f"/evaluation-runs/{run_id}")


def get_scores(run_id: int):
    return _get(f"/evaluation-runs/{run_id}/scores")


def get_hard_rule_results(run_id: int):
    return _get(f"/evaluation-runs/{run_id}/hard-rule-results")


def get_leaderboard(hid: int, run_id: int | None = None):
    params = {}
    if run_id:
        params["run_id"] = run_id
    return _get(f"/hackathons/{hid}/leaderboard", params=params)


def export_excel(hid: int, run_id: int | None = None):
    params = {}
    if run_id:
        params["run_id"] = run_id
    resp = _client.get(f"/hackathons/{hid}/export", params=params)
    if resp.status_code == 200:
        return resp.content
    return None
