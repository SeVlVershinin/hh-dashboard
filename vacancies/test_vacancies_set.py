from unittest import TestCase
from vacancies.vacancies_set import VacanciesSet


class TestVacanciesSet(TestCase):
    def setUp(self):
        self.set = VacanciesSet("Delphi")

    def test_vacancies_set_created(self):
        self.assertTrue(True)
