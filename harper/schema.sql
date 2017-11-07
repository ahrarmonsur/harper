--Temperature Measurements
drop table if exists temperature;
create table temperature (
      id integer primary key autoincrement,
      measurement real,
      timestamp integer not null
);

--Moisture Measurements
drop table if exists moisture;
create table moisture (
      id integer primary key autoincrement,
      measurement real,
      timestamp integer not null
);
