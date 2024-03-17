from multiprocessing import Pool

import pandas as pd
import requests

from constants import NOTION_DATABASE_ID, NOTION_TOKEN

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
}


def process_and_query(id):
    return process_block(query_block(id))


def query_db(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()


def query_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.request("GET", url, json=payload, headers=headers)
    return response.json()


def query_block(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"

    response = requests.request("GET", url, headers=headers)

    return response.json()


def process_block(block):
    # print(block)
    length = len(block["results"])
    # assert l > 0, f"Block has no children"
    if length == 0:
        return ""

    else:
        r = ""
        # print(block)
        for result in block["results"]:
            if "paragraph" in result.keys():
                # return result['properties']['title']
                try:
                    r += result["paragraph"]["rich_text"][0]["plain_text"]
                except KeyError:
                    continue
        # print(result['paragraph']['rich_text'][0]['plain_text'])
        return r
    # print(block)


payload = {}
# payload = {
#     "page_size": 1,
#     "start_cursor": "cursor",
# }


def main():
    ids, dates = [], []
    data = query_db(NOTION_DATABASE_ID)
    # print(data)
    # print(len(data['results']))
    # print(data['results'][0])
    for result in data["results"]:
        ids.append(result["id"])
        dates.append(result["created_time"])

    # print(len(data['results']))

    while data["has_more"]:
        payload["start_cursor"] = data["next_cursor"]
        data = query_db(NOTION_DATABASE_ID)
        for result in data["results"]:
            ids.append(result["id"])
            dates.append(result["created_time"])

    df = pd.DataFrame(data={"id": ids, "ts": dates})
    df["ts"] = pd.to_datetime(df["ts"])
    df["date"] = df["ts"].dt.strftime("%Y-%m-%d")
    df.sort_values(by=["date"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # pid = df.loc[0, 'id']
    # pid = '7edba87fc83d4064a7a8308ea0c788bf'
    # block = query_block(pid)
    # print(block)
    # process_block(block)
    # texts = []
    # for i in tqdm(range(len(df))):
    #     pid = df.loc[i, 'id']
    #     block = query_block(pid)
    #     text = process_block(block)
    #     texts.append(text)

    # df['text'] = df.apply(lambda x: process_block(query_block(x['id'])), axis=1)

    # df["text"] = list(map(process_block, map(query_block, df["id"])))
    with Pool() as p:
        df["text"] = list(p.map(process_and_query, df["id"]))
    name = input("Enter name of the file: ")
    df.to_csv(f"{name}.csv", index=False)


if __name__ == "__main__":
    main()
