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
    sql=('select * from standings;')
    c.execute(sql)
    standings = c.fetchall()
    print "Standings are:"
    print(standings)
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
    paired = []
    # check if even number of players
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
                standings.remove(player)
                break
    # Cycle through the ordered standings 2 at a time pairing the first
    # player with the second
    #for i in range(0,len(standings),2):
        #pairings.append((standings[i][0],standings[i][1], standings[i+1][0], standings[i+1][1]))
    for player in standings:
        #for pair in pairings:
            #paired.append(pair[0])
            #paired.append(pair[2])
        #paired.append(player[0])
        paired.append(0)
        paired.append(0)
        opponent = topOpponent(player[0], tuple(paired))
        pairings.append((player[0], player[1], opponent[0], opponent[1]))
        paired.append(player[0])
        paired.append(opponent[0])
        print "I am removing: {}".format(player[0])
        standings.remove(player)
        for player in standings:
            if player[0] == opponent[0]:
                print "I am removing: {}".format(player[0])
                standings.remove(player)
    print "Pairings are"
    print(pairings)
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
    """For a given player return top unplayed opponent
    """
    player1 = player1
    print "finding opponent for {}".format(player1)
    db = connect()
    c = db.cursor()
    sql=('select *, '
         '(select count(*) from matches where winner=id) as Wins, '
         '(select count(*) from matches where id in (winner, loser)) as Played '
         'from players '
         'where id in (select winner as players from matches '
         'where {0} not in (winner,loser) UNION '
         'select loser as players from matches '
         'where {0} not in (winner,loser)) '
         'and id not in {1}'
         'order by Wins desc;'.format(player1,paired))
    print(sql)
    c.execute(sql)
    #opponent = c.fetchall()[0]
    opponent = c.fetchall()
    print "print opponents"
    print(opponent)
    opponent = opponent[0]
    db.close()
    return opponent


