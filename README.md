# notion-proj

This is just a fun project I am working on to essentially **train a language model to write like me** with all the text that I have written in Notion over the course of 2 years.

## Steps

* [x] Explore the Notion API
* [x] Iteratively query the DB to fetch all the text written in a given Notion Database
* [x] Generate csv file containing all the text
* [x] Fine - tune a language model
* [x] Check the results
* [x] Move onto the next project :)

## Setup

### Prerequisites

This project assumes that you have setup your `Notion Developer Account` and have the secret `NOTION_TOKEN` and the `NOTION_DATABASE_ID` that you wish to query.

In `constants.py`, you need to declare two variables, `NOTION_TOKEN` and `NOTION_DATABASE_ID`.

```python
# contents of constants.py
NOTION_TOKEN = 'your_secret_notion_token'
NOTION_DATABASE_ID = 'id_of_your_notion_database'
```

Once, these variables are defined. Simply run the `notion.py` using the command `python notion.py`. The file will recursively query the database and extract all the textual content in all the pages, and then create a `data.csv` containing the `date`, `id`, and the `text` in the database.
