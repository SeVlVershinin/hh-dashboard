create table vac_data
(
    "salary.from"     REAL,
    "salary.to"       REAL,
    "employer.name"   TEXT,
    "schedule.name"   TEXT,
    "experience.name" TEXT,
    query             TEXT NOT NULL
);

create table vac_queries
(
    query      text not null,
    query_date text not null
);
