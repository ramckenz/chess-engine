"""

"""

class GameState():
    def __init__(self):
        #board is an 8x8 2d list, each element of the list has 2 characters.
        #first character is the color of the piece, black or white
        #second character is the type of the pieces
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R':self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        #self.inCheck = False #come back to this later for better valid moves algorithm
        #self.pins = []
        #self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #coordinates for the square where an en passant capture is possible.
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]

    '''
    takes a move as a parameter and executes it (this doesn't work for castling, en passant, and promotion)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        #update the king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #en passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
        #update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2-square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #copies the rook into its new square
                self.board[move.endRow][move.endCol + 1] = '--' #erase old rook.
            else: #queenside castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        #update castling rights - whenever a rook or king moves.
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))

    '''
    Update castle rights given a move.
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False
    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop() 
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update the king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo a 2-square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            #undo castling rights
            self.castleRightsLog.pop() #get rid of the most recent entry
            self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks, self.castleRightsLog[-1].wqs, self.castleRightsLog[-1].bqs)  #set current castle rights to what is now the last in the list.
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            checkmate = False
            stalemate = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCurrentCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        #1 generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        #2 for each move, make the move
        for i in range(len(moves)-1, -1, -1): #when removing from a list, go backwards
            self.makeMove(moves[i])
            #3 after making each move, generate all opponent's moves
            #4 for each of those moves, see if they capture your king
            #5 if they capture your king the move is not valid
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if(len(moves) == 0):
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCurrentCastleRights
        return moves

    '''
    Determine whether the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine whether the enemy can attack the square at r,c
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponent's point of view
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under attack:
                return True
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    '''
    get all pawn moves for a pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #1-square pawn advance.
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2-square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
                
        else: #black pawn moves
            if self.board[r+1][c] == "--": #1-square pawn advance.
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #2-square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0: #captures to the left
                if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7: #captures to the right
                if self.board[r+1][c+1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))

    '''
    get all rook moves for a pawn located at row, col and add these moves to the list
    '''
    def getRookMoves(self, r, c, moves):
        rookColor = 'b'
        if self.whiteToMove:
            rookColor = 'w'

        if c < 7: #check the right
            for col in range(c + 1, 8):
                if self.board[r][col] == "--":
                    moves.append(Move((r,c), (r, col), self.board))
                else:
                    if self.board[r][col][0] != rookColor:
                        moves.append(Move((r,c), (r, col), self.board))
                    break
        if c > 0: #check the left
            for col in reversed(range(c)):
                if self.board[r][col] == "--":
                    moves.append(Move((r,c), (r, col), self.board))
                else:
                    if self.board[r][col][0] != rookColor:
                        moves.append(Move((r,c), (r, col), self.board))
                    break
        if r < 7: #check below
            for row in range(r + 1, 8):
                if self.board[row][c] == "--":
                    moves.append(Move((r,c), (row, c), self.board))
                else:
                    if self.board[row][c][0] != rookColor:
                        moves.append(Move((r,c), (row, c), self.board))
                    break
        if r > 0: #check above
            for row in reversed(range(r)):
                if self.board[row][c] == "--":
                    moves.append(Move((r,c), (row, c), self.board))
                else:
                    if self.board[row][c][0] != rookColor:
                        moves.append(Move((r,c), (row, c), self.board))
                    break
    '''
    get all knight moves for a pawn located at row, col and add these moves to the list
    '''
    def getKnightMoves(self, r, c, moves):
        knightColor = 'b'
        if self.whiteToMove:
            knightColor = 'w'
        possibleMoves = [(r-1, c-2),(r-2,c-1),(r-2,c+1),(r-1,c+2),(r+1,c+2),(r+2,c+1),(r+2,c-1),(r+1,c-2)]
        for m in possibleMoves:
            if 0 <= m[0] <= 7 and 0 <= m[1] <= 7:
                if self.board[m[0]][m[1]][0] != knightColor:
                    moves.append(Move((r,c), (m[0],m[1]), self.board))
    '''
    get all bishop moves for a pawn located at row, col and add these moves to the list
    '''
    def getBishopMoves(self, r, c, moves):
        bishopColor = 'b'
        if self.whiteToMove:
            bishopColor = 'w'
        #Check above and to the left
        for diff in range(1,7):
            if r - diff >= 0 and c - diff >= 0:
                if self.board[r - diff][c - diff] == "--":
                    moves.append(Move((r, c), (r-diff, c-diff), self.board))
                else:
                    if self.board[r - diff][c - diff][0] != bishopColor:
                        moves.append(Move((r, c), (r-diff, c-diff), self.board))
                    break
            else:
                break
        #Check above and to the right
        for diff in range(1,7):
            if r - diff >= 0 and c + diff <= 7:
                if self.board[r - diff][c + diff] == "--":
                    moves.append(Move((r, c), (r-diff, c+diff), self.board))
                else:
                    if self.board[r - diff][c + diff][0] != bishopColor:
                        moves.append(Move((r, c), (r-diff, c+diff), self.board))
                    break
            else:
                break
        #check below and to the left
        for diff in range(1,7):
            if r + diff <= 7 and c - diff >= 0:
                if self.board[r + diff][c - diff] == "--":
                    moves.append(Move((r, c), (r+diff, c-diff), self.board))
                else:
                    if self.board[r + diff][c - diff][0] != bishopColor:
                        moves.append(Move((r, c), (r+diff, c-diff), self.board))
                    break
            else:
                break
        #check below and to the right
        for diff in range(1,7):
            if r + diff <= 7 and c + diff <= 7:
                if self.board[r + diff][c + diff] == "--":
                    moves.append(Move((r, c), (r+diff, c+diff), self.board))
                else:
                    if self.board[r + diff][c + diff][0] != bishopColor:
                        moves.append(Move((r, c), (r+diff, c+diff), self.board))
                    break
            else:
                break
    '''
    get all queen moves for a pawn located at row, col and add these moves to the list
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
    '''
    get all king moves for a pawn located at row, col and add these moves to the list
    '''
    def getKingMoves(self, r, c, moves):
        kingColor = 'b'
        if self.whiteToMove:
            kingColor = 'w'
        possibleMoves = [(r-1,c-1),(r-1,c),(r-1,c+1),(r,c-1),(r,c+1),(r+1,c-1),(r+1,c),(r+1,c+1)]
        for m in possibleMoves:
            if 0 <= m[0] <= 7 and 0 <= m[1] <= 7:
                if self.board[m[0]][m[1]][0] != kingColor:
                    moves.append(Move((r,c), (m[0],m[1]), self.board))
    '''
    Generate all valid castle moves for the king of a specified color at (r,c) and add them to the moves list.
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r,c):
            return #can't castle in check.
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)
        
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove = True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    #maps keys to values
    #key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        #En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)

    '''
    overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]