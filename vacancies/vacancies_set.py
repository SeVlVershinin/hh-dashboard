from pydantic import BaseModel
from enum import Enum

from vacancies.vacancies_datasource import (
    VacanciesDatasource,
    SALARY_FROM_PROP,
    SALARY_TO_PROP,
    EXPERIENCE_NAME_PROP,
    SCHEDULE_NAME_PROP,
    EMPLOYER_NAME_PROP
)


class VacanciesInfo(BaseModel):
    """
    Основная информация о наборе вакансий: исходный запрос, количество найденных вакансий и средние
    значения нижней и верхней границ зарплатных вилок
    """
    query: str
    count: int
    salary_from: float
    salary_to: float


class VacanciesCountGroup(BaseModel):
    """наименование группы и количество вакансий в ней"""
    name: str
    count: int


class VacanciesCount(BaseModel):
    """Количество вакансий в группах, полученных при группировке набора вакансий по некоторому признаку"""
    query: str
    groups: list[VacanciesCountGroup]


class GroupingType(str, Enum):
    """Способы группировки найденных вакансий"""
    by_employer = "by_employer"
    by_experience = "by_experience"
    by_schedule = "by_schedule"


class VacanciesSet:
    def __init__(self, query: str):
        self.query = query.lower()
        self._load()

    def _load(self):
        self.data_frame = VacanciesDatasource.get_vacancies_data(self.query)

    def get_data(self):
        return self.data_frame

    def get_info(self) -> VacanciesInfo:
        return VacanciesInfo(query=self.query,
                             count=self.data_frame.shape[0],
                             salary_from=self.data_frame[SALARY_FROM_PROP].mean(),
                             salary_to=self.data_frame[SALARY_TO_PROP].mean())

    def _get_count_by(self, group_column: str = EMPLOYER_NAME_PROP, limit_to: int = 5) -> VacanciesCount:
        group_series = self.data_frame[group_column].value_counts()
        n = min(limit_to, group_series.shape[0])

        res = VacanciesCount(query=self.query, groups=[])
        for item in group_series[:n].items():
            res.groups.append(VacanciesCountGroup(name=item[0], count=item[1]))
        return res

    def get_count_by(self, grouping_type):
        if grouping_type == GroupingType.by_employer:
            return self._get_count_by(EMPLOYER_NAME_PROP)
        elif grouping_type == GroupingType.by_schedule:
            return self._get_count_by(SCHEDULE_NAME_PROP)
        else:
            return self._get_count_by(EXPERIENCE_NAME_PROP)
