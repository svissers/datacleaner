-- drop table users;
-- drop table data;
-- drop table owner_data;

CREATE TABLE Users(
	id SERIAL,
	username VARCHAR(64) UNIQUE NOT NULL,
	password VARCHAR(256) NOT NULL,
	name VARCHAR(64) NOT NULL,
    email varchar(64) NOT NULL DEFAULT '',
	active BOOLEAN NOT NULL DEFAULT TRUE,
	admin BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY(id)
);

CREATE TABLE Data(
	id SERIAL,
	name VARCHAR(64) UNIQUE NOT NULL,
	description TEXT NOT NULL,
	tablename VARCHAR(64) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE Owner_data(
	data_id integer NOT NULL,
	user_id integer NOT NULL,
	PRIMARY KEY(data_id, user_id)
);
