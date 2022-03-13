from wsgiref import headers
import requests
import pandas as pd
from constants import NOTION_DATABASE_ID, NOTION_TOKEN

def query_db(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.request("POST", url, headers=headers)
    return response.json()

def query_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.request("GET", url, headers=headers)
    return response.json()

def query_block(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"

    response = requests.request("GET", url, headers=headers)

    return response.json()

def process_block(block):
    l = len(block['results'])
    # assert l > 0, f"Block has no children"
    if l == 0:
        return ""

    else:

        for result in block['results']:
            r = result['paragraph']['rich_text'][0]['plain_text']
        # print(result['paragraph']['rich_text'][0]['plain_text'])
            return r
    # print(block)

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json"
}

def main():
    ids, dates = [], []
    data = query_db(NOTION_DATABASE_ID)
    # print(type(data))
    # print(len(data['results']))
    # print(data['results'][0])
    for result in data['results']:
        ids.append(result['id'])
        dates.append(result['created_time'])

    df = pd.DataFrame(data={"id": ids, "ts": dates})
    df['ts'] = pd.to_datetime(df['ts'])
    # print(df.info())
    df['date'] = df['ts'].dt.strftime('%Y-%m-%d')
    # print(df.head())
    df.sort_values(by=['date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    # print(df.head())

<<<<<<< HEAD
    pid = df.loc[0, 'id']
=======
    pid = "ce68e4f6-2a09-4c88-b20f-77dd55c0d0e6"
>>>>>>> 80ccad2527fdfa5937047d5b59dac6e98ce1cf31
    block = query_block(pid)
    # print(block)
    # process_block(block)
    df['text'] = df.apply(lambda x: process_block(query_block(x['id'])), axis=1)
    print(df)
    df.to_csv("data.csv", index=False)


if __name__ == "__main__":
    main()

