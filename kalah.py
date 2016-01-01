import numpy as np
import itertools as it
import copy
import operator as op
import time


class kalah:
    def __init__(self, initialplayer=0):
        self.board = np.zeros((2, 8)).astype(int)
        self.board[:, 1:7] = 4
        self.player = initialplayer
        assert self.board.sum() == 4*12

    def __repr__(self):
        ret = ''
        for i in range(2):
            for j in range(8):
                if (i, j) not in [(1, 0), (0, 7)]:
                    ret += ' {:>2}'.format(self.board[i, j])
                else:
                    ret += ' {:>2}'.format(('<' if i == 0 else ' ')
                                           if self.player == 0 else
                                           (' ' if i == 0 else '>'))
            if i == 0: ret += '\n'
        return ret

    @staticmethod
    def moves(start, quant):
        player, square = start
        assert 0 <= player <= 1
        assert 1 <= square <= 6
        gen = it.cycle([(0, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                        (1, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1)])
        gen = it.dropwhile(lambda (p, s): (p, s) != start, gen)
        otherplayer = (player + 1) % 2
        otherkalah = otherplayer, 7 if otherplayer else 0
        gen = it.ifilter(lambda (p, s): (p, s) != otherkalah, gen)
        assert gen.next() == start
        plays = [gen.next() for _ in xrange(quant)]
        return plays

    def endofgame(self):
        return self.board[0, 1:7].sum() == 0 or self.board[1, 1:7].sum() == 0

    def play(self, square):
        assert 0 <= self.player <= 1
        assert 1 <= square <= 6
        if self.endofgame(): return None
        assert not self.endofgame()

        quant = self.board[self.player, square]
        if quant == 0: return False
        squaresinc = kalah.moves((self.player, square), quant)
        assert len(squaresinc) == quant

        self.board[self.player, square] = 0
        for x in squaresinc: self.board[x] += 1

        lastsquare = squaresinc[-1]

        if lastsquare not in [(0, 0), (1, 7)] and self.board[lastsquare] == 1 and lastsquare[0] == self.player:
            otherplayersquare = (self.player + 1) % 2, lastsquare[1]
            mykalah = self.player, 7 if self.player else 0
            self.board[mykalah] += self.board[otherplayersquare]
            self.board[otherplayersquare] = 0

        self.player += (lastsquare not in [(0, 0), (1, 7)] or self.endofgame())
        self.player %= 2

        if self.endofgame():
            self.board[0, 0] += self.board[0, 1:7].sum()
            self.board[0, 1:7] = 0
            self.board[1, 7] += self.board[1, 1:7].sum()
            self.board[1, 1:7] = 0

        assert self.board.sum() == 4*12
        return True

    def possibleplays(self):
        def g(kalahinstance):
            return reduce(op.concat, map(lambda square: f(square, kalahinstance), xrange(1, 6+1)))

        def f(square, kalahinstance):
            assert isinstance(square, int)
            assert isinstance(kalahinstance, kalah)
            copykalahinstance = copy.deepcopy(kalahinstance)
            ret = copykalahinstance.play(square)
            if ret:
                if copykalahinstance.player == kalahinstance.player and not copykalahinstance.endofgame():
                    return map(lambda (s, game): ([square] + s, game), g(copykalahinstance))
                else:
                    return [([square], copykalahinstance)]
            else: return []

        return g(self)

    def bestplay(self, level=0):
        starttime = time.time()
        def bestplaytail(level, kalahinstance):
            assert level >= 0

            if kalahinstance.endofgame(): return (None, None)

            possible = kalahinstance.possibleplays()
            assert len(possible) > 0
            assert all(kalahinstance.player != game[1].player for game in possible), \
                (kalahinstance.player, [game[1].player for game in possible], kalahinstance, possible)

            def iametric(game):
                assert isinstance(game, kalah)
                return game.board[0, 0] - game.board[1, 7] \
                    if kalahinstance.player == 0 else \
                    game.board[1, 7] - game.board[0, 0]

            if level == 0:
                return max(possible, key=lambda (path, game): iametric(game))
            else:
                possibleother = map(lambda (path, game): (path, bestplaytail(level-1, game)[1]), possible)
                possibleother = filter(lambda (path, game): game is not None, possibleother)
                if len(possibleother) == 0: return max(possible, key=lambda (path, game): iametric(game))
                else: return max(possibleother, key=lambda (path, game): iametric(game))

        ret = bestplaytail(level, self)
        endtime = time.time()
        print 'Time thinking: {} seconds'.format(endtime - starttime)
        return ret

class kalahgame:
    def __init__(self, initialplayer=0, iaplayer=0, ialevel=2):
        self.kalah = kalah(initialplayer)
        self.iaplayer = iaplayer
        self.ialevel = ialevel

    def interactive(self):
        while not self.kalah.endofgame():
            print self.kalah
            square = 0
            while not 1 <= square <= 6:
                try:
                    square = int(raw_input('Player {}. Insert the square to play: '.format(self.kalah.player)))
                except EOFError:
                    return
                except:
                    square = 0
            self.kalah.play(square)
        print self.kalah

    def iainteractive(self):
        while not self.kalah.endofgame():
            print self.kalah
            printlinetext = 'Player {}. Insert the square to play:'.format(self.kalah.player)

            if self.kalah.player == self.iaplayer:
                path, finalstate = self.kalah.bestplay(self.ialevel)
                print printlinetext, path[0]
            else:
                square = 0
                while not 1 <= square <= 6:
                    try:
                        square = int(raw_input(printlinetext + ' '))
                    except EOFError:
                        return
                    except:
                        square = 0
                path = [square]
            assert len(path) > 0

            self.kalah.play(path[0])
            for square in path[1:]:
                print self.kalah
                print printlinetext, square
                self.kalah.play(square)
        print self.kalah


game = kalahgame(1, 0, 4)
game.iainteractive()
