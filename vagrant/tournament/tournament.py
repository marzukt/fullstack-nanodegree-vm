#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('TRUNCATE TABLE matches;')
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('TRUNCATE TABLE players;')
    db.commit()
    db.close()



def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute('select count(*) from players;')
    playerCount = c.fetchall()[0][0]
    db.close()
    return playerCount



def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute('insert into players (player_name) values (%s);',(name,))
    db.commit()
    db.close()



def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    sql=('select *, '
         '(select count(*) from matches where winner=id) as Wins, '
         '(select count(*) from matches where id in (winner, loser)) as Played '
         'from players '
         'order by Wins desc;')
    c.execute(sql)
    standings = c.fetchall()
    # print(standings)
    db.close()
    return standings



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    sql = 'insert into matches (winner, loser) values (%d, %d);' % (winner, loser)
    # print(sql)
    c.execute(sql)
    db.commit()
    db.close()

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    pairings =[]
    # Cycle through the ordered standings 2 at a time pairing the first
    # player with the second
    for i in range(0,len(standings),2):
        pairings.append((standings[i][0],standings[i][1], standings[i+1][0], standings[i+1][1]))
    return pairings

def checkRematch():
    """Boolean to determine  whether the match is a rematch
    """
    db = connect()
    c = db.cursor()
    sql=('select count(*) '
         'from standings '
         'where ((loser == player1 and winner == player2) '
         ' or (loser == player1 and winner == player2))')
    print(sql)
    c.execute(sql)
    matchCount = c.fetchall()[0][0]
    if matchCount >= 1: return True
    else: return False
