import time


def query_db(session, db_id, cursor=None):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": 100}
    if cursor:
        payload["start_cursor"] = cursor
    # ponytail: serial requests respect Notion's 3/s limit; share a limiter before parallelizing.
    time.sleep(0.35)
    response = session.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def iter_pages(session, db_id):
    cursor = None
    while True:
        data = query_db(session, db_id, cursor)
        yield from data["results"]
        if not data["has_more"]:
            return
        cursor = data["next_cursor"]


def query_block(session, block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    results = []
    params = {"page_size": 100}
    while True:
        time.sleep(0.35)
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results.extend(data["results"])
        if not data["has_more"]:
            return {"results": results}
        params["start_cursor"] = data["next_cursor"]


def process_block(session, block):
    texts = []
    for result in block["results"]:
        content = result[result["type"]]
        text = "".join(part["plain_text"] for part in content.get("rich_text", []))
        if text:
            texts.append(text)
        if result.get("has_children"):
            text = process_block(session, query_block(session, result["id"]))
            if text:
                texts.append(text)
    return "\n\n".join(texts)
