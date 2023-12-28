import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta

DATETIME_FORMAT_STR = '%Y-%m-%d'

DB_PATH = "./vac_data.sqlite"
VAC_DATA_TABLE = "vac_data"
VAC_QUERIES_TABLE = "vac_queries"

SALARY_TO_PROP = 'salary.to'
SALARY_FROM_PROP = 'salary.from'
EXPERIENCE_NAME_PROP = 'experience.name'
SCHEDULE_NAME_PROP = 'schedule.name'
EMPLOYER_NAME_PROP = 'employer.name'
QUERY_PROP = "query"
PROP_NAMES = [QUERY_PROP, SALARY_FROM_PROP, SALARY_TO_PROP, EMPLOYER_NAME_PROP, SCHEDULE_NAME_PROP,
              EXPERIENCE_NAME_PROP]

HH_API_URL = 'https://api.hh.ru/vacancies'


class VacanciesDatasource:

    @staticmethod
    def get_vacancies_data(query: str) -> pd.DataFrame:
        if VacanciesDatasource.has_data_for_query(query):
            df = VacanciesDatasource.get_data_for_query(query)
            print(f'Из кэша получено {df.shape[0]} записей по запросу {query}')
            return df
        else:
            df = VacanciesDatasource.request_data_for_query(query)
            print(f'Через API получено {df.shape[0]} записей по запросу {query}')
            VacanciesDatasource.save_data_for_query(query, df)
            return df

    @staticmethod
    def has_data_for_query(query):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            res = cur.execute(
                f'select count(*) from {VAC_QUERIES_TABLE} where "query" = ? and "query_date" == ?;',
                [query, datetime.today().strftime(DATETIME_FORMAT_STR)]
            )
            row_count, = res.fetchone()
            return row_count > 0

    @staticmethod
    def get_data_for_query(query) -> pd.DataFrame:
        conn = sqlite3.connect(DB_PATH)
        return pd.read_sql_query(f'select * from {VAC_DATA_TABLE} where query == ?', con=conn, params=[query])

    @staticmethod
    def request_data_for_query(query) -> pd.DataFrame:
        v_page_json = VacanciesDatasource._request_vac_page_json(query)
        found_items = v_page_json['items']

        for i in range(1, v_page_json['pages']):
            found_items.extend(VacanciesDatasource._request_vac_page_json(query, i)['items'])

        data_frame = pd.json_normalize(found_items)
        data_frame[QUERY_PROP] = query
        return data_frame[PROP_NAMES]

    @staticmethod
    def _request_vac_page_json(query, page_number: int = 0):

        current_date = datetime.today()
        start_date = current_date - timedelta(30)
        params = {
            'text': f'NAME:("{query}")',
            # 'area': 1,
            'date_from': start_date.strftime(DATETIME_FORMAT_STR),
            'date_to': current_date.strftime(DATETIME_FORMAT_STR),
            'per_page': 100,
            'page': page_number
        }

        with requests.get(HH_API_URL, params=params) as request:
            return request.json()

    @staticmethod
    def save_data_for_query(query, df):
        with sqlite3.connect(DB_PATH) as conn:
            VacanciesDatasource.clear_query_data(query, conn)
            df.to_sql(name='vac_data', con=conn, if_exists='append', index=False)
            cur = conn.cursor()
            cur.execute(
                f'insert into {VAC_QUERIES_TABLE} values (?,?)',
                [query, datetime.today().strftime(DATETIME_FORMAT_STR)]
            )
            conn.commit()

    @staticmethod
    def clear_query_data(query, conn):
        cur = conn.cursor()
        for table in [VAC_QUERIES_TABLE, VAC_DATA_TABLE]:
            cur.execute(f'delete from {table} where query == ?', [query])
