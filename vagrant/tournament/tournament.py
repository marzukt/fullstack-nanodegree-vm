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
    """Remove all the player records from the database.

       Note also removes dependant tables!!!

    """
    db = connect()
    c = db.cursor()
    # use cascade to truncate matches at the same time
    # due to foriegn key dependacies
    c.execute('TRUNCATE TABLE players CASCADE;')
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
    sql=('select * from standings;')
    c.execute(sql)
    standings = c.fetchall()
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
    sql = 'insert into matches (winner, loser) values (%s, %s);'
    c.execute(sql,(winner,loser))
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
    # create a list to hold the match pairings to return
    pairings =[]
    # create a list to keep track of already paired players
    paired = []
    # If there are an uneven number of players give one a bye
    if len(standings)%2 != 0:
        # Retrieve players with byes from the db
        db = connect()
        c = db.cursor()
        # matches with byes have only a winner
        sql = 'select winner from matches where loser is null'
        c.execute(sql)
        playersWithByes = c.fetchall()
        db.close()
        # find highest ranked player without a bye and give them a bye
        for player in standings:
            if player[0] not in playersWithByes:
                reportMatch(player[0],'NULL')
                paired.append(player[0])
                standings.remove(player)
                break

    # Pair the remaining players
    for player in standings:
        paired.append(player[0])
        opponent = topOpponent(player[0], paired)
        pairings.append((player[0], player[1], opponent[0], opponent[1]))
        paired.append(opponent[0])
        standings.remove(player)
        for player in standings:
            if player[0] == opponent[0]:
                standings.remove(player)
    return pairings

def swissPairingsNew():
    standings = playerStandings()
    return standings
def checkRematch(player1,player2):
    """Boolean to determine  whether the match is a rematch
    """
    player1 = player1
    player2 = player2
    db = connect()
    c = db.cursor()
    sql=('select count(*) '
         'from matches '
         'where ((loser = {0} and winner = {1}) '
         ' or (loser = {1} and winner = {0}))'.format(player1,player2))
    print(sql)
    c.execute(sql)
    matchCount = c.fetchall()[0][0]
    db.close()
    if matchCount >= 1: return True
    else: return False

def topOpponent(player1,paired):
    """For a given player returns the top unplayed opponent

    Args:
        player1: id of the player for whom to return the top unplayed opponent
        paired: list of id's for players who have already been paired
                in this round

    Returns:
      A tuple of the opponents standings:
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played

    """
    db = connect()
    c = db.cursor()
    # query database for a list of unplayed opponents
    # exclude players that have already been paired in this round
    sql=('select * '
         'from standings '
         'where id in (select winner as players from matches '
         'where %s not in (winner,loser) UNION '
         'select loser as players from matches '
         'where %s not in (winner,loser)) '
         'and NOT(id = ANY(%s))' # postgresql ANY command to use list as IN
         'order by Wins desc;')
    c.execute(sql,(player1,player1,paired))
    opponent = c.fetchall()[0]
    db.close()
    return opponent


