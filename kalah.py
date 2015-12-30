import numpy as np
import itertools as it
import copy
import operator as op


class kalah:
    def __init__(self):
        self.board = np.zeros((2, 8)).astype(int)
        self.board[:, 1:7] = 4
        self.player = 0
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
    def plays(start, quant):
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
        assert not self.endofgame()

        quant = self.board[self.player, square]
        if quant == 0: return False
        squaresinc = kalah.plays((self.player, square), quant)
        assert len(squaresinc) == quant

        self.board[self.player, square] = 0
        for x in squaresinc: self.board[x] += 1

        lastsquare = squaresinc[-1]

        if lastsquare not in [(0, 0), (1, 7)] and self.board[lastsquare] == 1 and lastsquare[0] == self.player:
            otherplayersquare = (self.player + 1) % 2, lastsquare[1]
            mykalah = self.player, 7 if self.player else 0
            self.board[mykalah] += self.board[otherplayersquare]
            self.board[otherplayersquare] = 0

        self.player += lastsquare not in [(0, 0), (1, 7)]
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
                if copykalahinstance.player == kalahinstance.player:
                    return map(lambda (s, game): ([square] + s, game), g(copykalahinstance))
                else:
                    return [([square], copykalahinstance)]
            else: return []

        return g(self)

    def iametric(self):
        return self.board[0, 0] - self.board[1, 7]

    def bestplay(self, level=0):
        def bestplaylevels(level, kalahinstance):
            assert level >= 0
            assert kalahinstance.player == 0

            possible = kalahinstance.possibleplays()
            if level == 0:
                return max(possible, key=lambda (path, game): game.iametric())
            else:
                possibleother = map(lambda (path, game):
                                    map(lambda (pathother, gameother): (path, gameother),
                                        game.possibleplays()),
                                    possible)
                possibleother = map(lambda lst:
                                    map(lambda (path, game): (path, bestplaylevels(level-1, game)[1]),
                                        lst),
                                    possibleother)
                possibleother = map(lambda lst:
                                    min(lst, key=lambda (path, game): game.iametric()),
                                    possibleother)
                return max(possibleother, key=lambda (path, game): game.iametric())

        return bestplaylevels(level, self)

class kalahgame:
    def __init__(self):
        self.kalah = kalah()

    def interactive(self):
        while not self.kalah.endofgame():
            print self.kalah
            square = 0
            while not 1 <= square <= 6:
                try:
                    square = int(raw_input('({}) Insert the square to play: '.format(self.kalah.player+1)))
                except EOFError:
                    return
                except:
                    square = 0
            self.kalah.play(square)
        print self.kalah

    def iainteractive(self):
        while not self.kalah.endofgame():
            print self.kalah
            if self.kalah.player == 0:
                path, finalstate = self.kalah.bestplay(1)
                print '({}) Insert the square to play: {}'.format(self.kalah.player+1, ', '.join(map(str, path)))
            else:
                square = 0
                while not 1 <= square <= 6:
                    try:
                        square = int(raw_input('({}) Insert the square to play: '.format(self.kalah.player+1)))
                    except EOFError:
                        return
                    except:
                        square = 0
                path = [square]

            for square in path: self.kalah.play(square)
        print self.kalah

    def possibleplays(self):
        ret = self.kalah.possibleplays()
        for s, game in ret:
            print s
            print game
            print game.iametric()
            print
        print self.kalah.bestplay(1)


aux = kalahgame()
