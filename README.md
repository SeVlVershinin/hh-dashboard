# Получения агрегированных данных о вакансиях на HeadHunter 
Репозиторий содержит код сервиса, который через API HeadHunter выполняет поиск вакансий по заданной фразе 
поиска и выводит некоторые обобщенные показатели для найденного множества вакансий (количество, среднюю 
зарплатную вилку, количество вакансий по работодателю, опыту работы и форме занятости).

Сервис представляет собой реализованный на FastApi (Python) Web API. Результаты запросов к API Headhunter
кэшируются в БД на SQLite и устаревают (и при последующих запросах перезаписываются) на следующие сутки.

В репозитории также содержится dockerfile, который позволяет упаковать сервис в docker-контейнер.
Кроме того, в ```github/workflows``` содержатся yaml-описания для CI- (запуск тестов) и CD-(сборка и публикация
образа на Docker Hub) конвейеров.

Образ сервиса можно скачать с Docker Hub по ссылке: https://hub.docker.com/repository/docker/sevlvershinin/hh-dashboard/

Работающий сервис размещена по адресу: http://94.139.242.35/


