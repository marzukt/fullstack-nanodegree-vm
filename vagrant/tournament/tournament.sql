-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;
CREATE TABLE players ( id SERIAL PRIMARY KEY,
                       player_name TEXT);
CREATE TABLE matches (match_id SERIAL PRIMARY KEY,
                      loser int NULL references players(id),
                      winner int references players(id));
CREATE OR REPLACE VIEW standings AS
    select *,
    (select count(*) from matches where winner=id) as Wins,
    (select count(*) from matches where id in (winner, loser)) as Played
    from players
    order by Wins desc;
