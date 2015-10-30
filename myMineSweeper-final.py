from tkinter import *
import tkinter.messagebox
import time
import random

SIZE = 15
CELLSIZE = 2
MINE_RATIO = 0.15

class GamePlay():
    def __init__(self, _size, _cellSize, _mineRat):
        self.isRunning = False
        self.size = _size
        self.rows = _size
        self.columns = _size
        self.cellSize = _cellSize
        self.mineRatio = _mineRat
        self.createWindow()
        self.createTopMenu()
        self.createResButton()
        self.createTimer()
        self.createGameBoard()

    def main(self):
        self.root.mainloop()

    #creates game window    
    def createWindow(self):
        self.root = Tk()
        self.root.title("MineSweeper")

    def createTopMenu(self):
        menuBar = Menu(self.root)
        fileMenu = Menu(menuBar, tearoff = 0)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.quitGame)
        menuBar.add_cascade(label="File", menu=fileMenu)
        menuBar.add_command(label = "About", command = self.aboutGame)
        self.root.config(menu=menuBar)
    
    def createSaveWindow(self):
        saveWin = Toplevel(root, bd=5, bg='lightblue')
        saveWin.title('save game')
        saveWin.minsize(width = 200, height = 100)
        saveWin.grid()
        saveBut = Button(saveWin, text = 'Save', width = 20, height = 2)
        saveBut.bind('<Button-1>', saveGame)
        cancelBut = Button(saveWin, text = 'Cancel', width = 20, height = 2)
        cancelBut.bind('<Button-1>', closeWindow)
        saveBut.pack(side = LEFT)
        cancelBut.pack(side = RIGHT)

    #creates class which contains frame on game window
    def createGameBoard(self):
        self.myGameBoard = GameBoard(self.root, self.rows, self.columns, self.size, self.cellSize, self.mineRatio)
        for cells in self.myGameBoard.getCells():
            for cell in cells:
                cell.getButton().bind('<Button-1>',
                                      lambda event, arg=cell.getButton(): self.leftButHandler(event, arg))
                cell.getButton().bind('<Button-3>',
                                      lambda event, arg=cell: self.rightButHandler(event, arg))
                                              
    #handles event from clicking left mouse button
    def leftButHandler(self, event, widget):
        pos = self.myGameBoard.getButtonPosition(widget)
        if self.checkLose(pos[0], pos[1]):
            tkinter.messagebox.showwarning("BOOOOOOM!!!", "You're done!")
            self.timerLabel.grid_forget()
        else:
            self.myGameBoard.openCells(pos[0], pos[1])
            if self.checkWin():
                tkinter.messagebox.showinfo("Victory!", "You won!")
                self.timerLabel.grid_forget()
        if self.isRunning == False:
            self.isRunning = True
            self.runTimer(event)
            
    #checkes whether player loses or not
    def checkLose(self, _row, _column):
        if self.myGameBoard.cells[_row][_column].hasMine():
            self.myGameBoard.openAllCells()
            self.root.after_cancel(self.runTimer)
            self.isRunning = False
            return True
        return False

    #checks whether player wins or not
    def checkWin(self):
        for cells in self.myGameBoard.cells:
            for cell in cells:
                if not cell.hasMine() and not cell.isOpened():
                    return False
        for cells in self.myGameBoard.cells:
            for cell in cells:
                if cell.hasMine() and not cell.hasFlag():
                    return False
        self.root.after_cancel(self.runTimer)
        self.isRunning = False
        return True

    #handles event from clicking right mouse button
    def rightButHandler(self, event, cellInstance):
        cellInstance.setFlag()
                                                              
    #creates reset button          
    def createResButton(self):
        resetBut = Button(self.root, text = "Reset", width = 10,
                          height = 2, fg = "red", relief = RAISED,
                          font = "Arial 16", bd = 10)
        resetBut.grid(row = 0, column = 1)
        resetBut.bind('<Button-1>', self.resetGame)
        
    #creates timer   
    def createTimer(self):
        self.timerLabel = Label(self.root, text='00:00:00',
                          width = 10, height = 2,
                          font = ("Arial", 20), relief = SUNKEN, bd = 10)
        self.timerLabel.grid(row = 0, column = 0)
        self.timer = [0,0,0]
        self.timeFormat = "{0:02d}:{1:02d}:{2:02d}"

    #starts the timer
    def runTimer(self, event=None):
        if self.isRunning:
            self.timer[2] += 1
            if self.timer[2] >= 60:
                self.timer[1] += 1
                self.timer[2] = 0
            if self.timer[1] >= 60:
                self.timer[0] += 1
                self.timer[1] = 0
            timeString = self.timeFormat.format(self.timer[0],self.timer[1],self.timer[2])    
            self.timerLabel.configure(text=timeString)
            self.root.after(1000, self.runTimer)

    #resets the game
    def resetGame(self, event=None):
        self.myGameBoard.reset()
        self.timerLabel.grid_forget()
        self.root.after_cancel(self.runTimer)
        self.isRunning = False
        self.createGameBoard()
        self.createTimer()

    def quitGame(self):
        self.root.destroy()

    def aboutGame(self):
        tkinter.messagebox.showinfo("About program", "Written by @Dmytro \nCSCI-0010 \nDecember, 2014")
        
class GameBoard():
    def __init__(self, _widget, _rows, _columns, _size, _cellSize, _mineRat):
        self.rows = _rows
        self.columns = _columns
        self.size = _size
        self.cellSize = _cellSize
        self.minesRatio = _mineRat
        self.labels = [[0 for x in range (self.rows)] for x in range (self.columns)]
        self.buttons = [[0 for x in range (self.rows)] for x in range (self.columns)]
        self.cells = [[0 for x in range (self.rows)] for x in range (self.columns)]
        self.createGameFrame(_widget, self.rows, self.columns, self.size, self.cellSize)
        self.distributeMines()
        self.placeLabels()
        
    #creates game field(frame) on game window, creates and places labels on frame and
    #above every label creates a button, using class Cell
    def createGameFrame(self, _widget, _rows, _columns, _size, _cellSize):
        self.fr = Frame(_widget, width = _size*_cellSize,
                          height = _size*_cellSize, relief = SUNKEN, bd = 10)
        self.fr.grid(row = 1, columnspan = 2)
        for r in range(self.rows):
            for c in range(self.columns):
                self.labels[r][c] =  Label(self.fr, width = self.cellSize,
                                           height = int(self.cellSize/2),
                                           font=("Arial", 18))
                self.labels[r][c].grid(row = r, column = c)
                self.labels[r][c].grid_propagate(0)
                self.cells[r][c] = Cell(self.fr, r, c, self.size, self.cellSize, self.rows, self.columns)
                               
    #randomly distributes mines among cells               
    def distributeMines(self):
        img = PhotoImage(file = '.\\mine50x50.gif')
        mines = 0
        while mines < self.rows*self.columns*self.minesRatio:
            row = random.randrange(0, self.rows)
            column = random.randrange(0, self.columns)
            if self.cells[row][column].hasMine() == False:
                mines += 1
                self.cells[row][column].putMine()
                self.labels[row][column].configure(image = img)
                self.labels[row][column].image = img
            
    #places number of mines in neighbouring cells in every label                    
    def placeLabels(self):
        for row in range(self.rows):
            for column in range(self.columns):
                if not self.cells[row][column].hasMine():
                    n = self.countNeighbourMines(row, column)
                    if n > 0:
                        self.cells[row][column].setNeighbourMines(n)
                        self.labels[row][column].configure(text = n)

    #calculates the number of mines in neighbouring cells
    def countNeighbourMines(self, _row, _column):
        count = 0
        if self.cells[_row][_column].hasMine():
            return -1
        for r in range(_row-1, _row+2):
            for c in range(_column-1, _column+2):
                if r < 0 or r >= self.rows or c < 0 or c >= self.columns:
                    continue
                if self.cells[r][c].hasMine():
                    count += 1
        return count

    def openCells(self, _row, _column):
        if _row < 0 or _row >= self.rows or _column < 0 or _column >= self.columns or self.cells[_row][_column].isOpened() or self.cells[_row][_column].hasMine():
            return
        elif self.cells[_row][_column].getNeighbourMines() > 0:
            self.cells[_row][_column].openCell()
        else:
            self.cells[_row][_column].openCell()
            self.openCells(_row, _column-1)
            self.openCells(_row, _column+1)
            self.openCells(_row-1, _column)
            self.openCells(_row+1, _column)
            self.openCells(_row+1, _column-1)
            self.openCells(_row+1, _column+1)
            self.openCells(_row-1, _column-1)
            self.openCells(_row-1, _column+1)
                      
    def openAllCells(self):
        for cells in self.cells:
            for cell in cells:
                if not cell.isOpened():
                    cell.openCell()
            
    def getButtonPosition(self, button):
        for r in range(self.rows):
            for c in range(self.columns):
                if self.cells[r][c].getButton() == button:
                    return [r, c]
        return [-1, -1]
       
    def getCells(self):
        return self.cells

    def reset(self):
        self.fr.grid_forget()
        

#class for every cell on the game field, creates covering button   
class Cell():
    def __init__(self, _widget, _row, _column, _size, _cellSize, _rows, _columns):
        self.opened = False
        self.mined = False
        self.flagged = False
        self.neighbourMines = 0
        self.row = _row
        self.column = _column
        self.rows = _rows
        self.columns = _columns
        self.myBut = Button(_widget, width = _cellSize, height = int(_cellSize/2),
                       image = '', relief = RAISED, bd = 5)
        self.myBut.grid(row = _row, column = _column)
                
    #returns button    
    def getButton(self):
        return self.myBut

    #destroy button on the game field, calls function which should open neighbouring cells
    def openCell(self, event=None):
        self.myBut.grid_remove()
        self.opened = True

    #says if cell opened or not 
    def isOpened(self):
          return self.opened

    #places flag on the button when right mouse button pressed
    def setFlag(self, event=None):
        if self.myBut['image']:
            img = ''
            self.myBut.configure(image = img)
            self.myBut.img = img
            self.flagged = False
        else:
            img = PhotoImage(file = '.\\flag50x50.gif')
            self.myBut.configure(image = img)
            self.myBut.img = img
            self.flagged = True

    #sets mine in cell
    def putMine(self):
        self.mined = True

    #says if cell has mine or not
    def hasMine(self):
        return self.mined

    def hasFlag(self):
        return self.flagged

    #sets number of mines in neighbouring cells for this cell
    def setNeighbourMines(self, _n):
        self.neighbourMines = _n

    #returns number of neighbouring mines
    def getNeighbourMines(self):
          return self.neighbourMines

def main():
     myMineSweeper = GamePlay(SIZE, CELLSIZE, MINE_RATIO)
     myMineSweeper.main()
    
if __name__ == '__main__':
     main()
        
    
    
        
