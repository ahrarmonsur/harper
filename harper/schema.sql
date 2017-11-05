drop table if exists temperatures;
create table temperatures (
      id integer primary key autoincrement,
      measurement real,
      timestamp integer not null
);
