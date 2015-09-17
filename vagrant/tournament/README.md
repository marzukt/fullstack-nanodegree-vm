#Tournament
A backend for running a Swiss tournament

##What’s Included:
README.md - this file
tournament.sql - SQL to configure the database schema
tournament.py - provides an interface to the database to run the tournament
tournament_test.py - test file for the functions in tournament.py

#Prerequisites:
PostgreSQL 9.3.9
Python 2.7+

##Cofiguring the db:
1) Open PostgreSQL `psql`
2) Run the command `\i tournament.sql` to create the database “tournament”
NB The script will drop any previous instruments of the database tournament


##Run the tests:
1)Run `python tournament_test.py` to run the tests
