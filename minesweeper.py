#Source for Minesweeper GUI: https://github.com/tjtrebat/minesweeper

__author__ = 'Tom and Jake'
#Edited by Jake A. Cole

import random
import time
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
#from statistics import Statistics

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.frame = Frame(root)
        self.frame.grid()
        self.size = (9,) * 2
        self.num_mines = 10
        #self.stats = Statistics()
        self.buttons = {}
        self.add_menu_bar()
        self.add_header()
        self.new_game()

        #Variables used by the AI
        self.gameover = 0
        self.flagcount = 0
        #incorrect counter
        self.ic = 0
        #clear counter
        self.cc = 0
        #win counter
        self.wc = 0
        self.aic = 0

        #the minefield the AI sees
        self.minefield = {}
            
    def add_menu_bar(self):
        menu = Menu(self.root)
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label="New", command=self.new_game)
        #file_menu.add_command(label="Statistics", command=self.stats.show_gui)
        file_menu.add_separator()
        self.level = "Beginner"
        self.levels = {"Beginner": BooleanVar(), "Intermediate": BooleanVar(),
                       "Advanced": BooleanVar(), "Custom": BooleanVar()}
        file_menu.add_checkbutton(label="Beginner", variable=self.levels["Beginner"],
                                  command=lambda x= "Beginner":self.new_game(level=x))
        file_menu.add_checkbutton(label="Intermediate", variable=self.levels["Intermediate"],
                                  command=lambda x= "Intermediate":self.new_game(level=x))
        file_menu.add_checkbutton(label="Advanced", variable=self.levels["Advanced"],
                                  command=lambda x= "Advanced":self.new_game(level=x))
        file_menu.add_command(label="Custom", command=self.custom_level)
        file_menu.add_separator()
        
        #AI solver button in file menu
        file_menu.add_command(label="AI", command=self.AI)       
        file_menu.add_separator()
        
        file_menu.add_command(label="Exit", command=quit)        
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    def add_header(self):
        frame = Frame(self.root)
        frame.grid()
        Label(frame, text="Timer:").grid(row=0, column=0)
        self.tv_timer = IntVar()
        self.time = Label(frame, textvariable=self.tv_timer)
        self.time.grid(row=0, column=1)
        Label(frame, text="Mines:").grid(row=0, column=2)
        self.tv_mines = IntVar()
        self.tv_mines.set(self.num_mines)
        Label(frame, textvariable=self.tv_mines).grid(row=0, column=3)

    def new_game(self, level=None):
        if level is not None:
            self.levels[self.level].set(False)
            #if self.level != level:
                #self.stats.winning_streak = 0
                #self.stats.losing_streak = 0
            self.level = level
            self.size = self.get_size()
            self.num_mines = self.get_num_mines()
            if self.level == "Custom":
                self.custom.destroy()
        self.levels[self.level].set(True)
        self.mines = self.get_mines()
        self.flags = []
        self.questions = []
        self.add_board()
        self.tv_mines.set(self.num_mines)
        if hasattr(self, "timer"):
            self.tv_timer.set(0)
            self.time.after_cancel(self.timer)

        #Resets the AI variables   
        self.gameover = 0
        self.flagcount = 0
        self.ic = 0
        self.cc = 0
        self.wc = 0
        self.aic = 0

    def custom_level(self):
        self.custom = Tk()
        self.custom.title("Custom")
        frame = Frame(self.custom, padx=10, pady=10)
        frame.grid()
        Label(frame, text="Height:").grid(row=0, column=0)
        self.custom_height = Spinbox(frame, width=3, from_=9, to=24)
        self.custom_height.grid(row=0, column=1)
        Label(frame, text="Width:").grid(row=1, column=0)
        self.custom_width = Spinbox(frame, width=3, from_=9, to=30)
        self.custom_width.grid(row=1, column=1)
        Label(frame, text="Mines:").grid(row=2, column=0)
        self.custom_mines = Spinbox(frame, width=3, from_=10, to=668)
        self.custom_mines.grid(row=2, column=1)
        Button(frame, text="OK", command=lambda x= "Custom":self.new_game(level=x)).grid()

####################################################################################################################        
### Solving Algorithm  #############################################################################################
### Author: Jake A. Cole ###########################################################################################
####################################################################################################################

    def AI(self):

        #Some important commands
        #print() self.size[0] #prints height
        #print() self.size[1] #prints width
        #print() self.size[0] * self.size[1] #prints total number of spaces
        #print() self.board[(0,0)] #Identity of 0,0 on the mine grid
        #print() self.num_mines #prints number of mines

        #Resets everything for a new game, AI button starts a new game on click
        self.new_game()        
        self.counter = 0
        self.gameover = 0
        self.tv_timer.set(0)

        #Array of tuples represents the AI's vision of the field
        for y in range(self.size[0]):
            for z in range(self.size[1]):
                self.minefield[(y,z)] = '-'        

        #Main loop
        while self.gameover == 0:

            self.aic = 1

            #Breaks out if there is an incorrect flag
            if (self.ic > 0):
                #print("\n", "Breaking out due to wrong flag")
                self.print_field()
                break
            
            self.solve_minefield()
            self.clear_cs()

            if ((self.ic == 0) and (self.flagcount - self.num_mines == 0)):
                #print("\n", "Clearing remaining spots on the board")
                self.clear_remaining()
                break
            
            elif (self.cc == 0):
                self.make_move()

        #Ending of the game
        #self.time.after_cancel(self.timer)        
        #print("\n", "The game has ended", "\n")
        #self.print_field()

        
    #Clears out the c values to allow the AI to progress further in the minesweeper   
    def clear_cs(self):
                
        #finds c values
        for c in range(self.size[0]):
            for d in range(self.size[1]):
                self.around_flags(c,d)

        self.cc = 0
        #solves c values
        for y in range(self.size[0]):
            for z in range(self.size[1]):
                if (self.minefield[(y, z)] == 'c'):
                    self.cc = self.cc + 1
                    #print("\n", "Clearing c values", y, ",", z, "\n")
                    
                    #Updates the GUI
                    root.update()
                                       
                    if (self.board[(y, z)] == 'm'):
                        print("RIP!", "\n")
                        self.found_mine()              
                        self.gameover = 1
                        
                    elif self.board[(y, z)] == '0':
                        print("No mines in sight", "\n") 
                        self.found_space((y, z))

                    elif self.board[(y, z)] == '1':
                        print("There is 1 mine next to this spot", "\n")
                        self.found_border((y, z))
                    else:
                        print("There are", self.board[(y, z)], "mines next to this spot", "\n") 
                        self.found_border((y, z))
    
    #After all of the mines are flagged, clear_remaining clears the remaining untouched spots
    def clear_remaining(self):
        for y in range(self.size[0]):
            for z in range(self.size[1]):
                
                #Updates the GUI
                root.update()
            
                if self.board[(y, z)] == 'm':
                    continue
                                        
                elif self.board[(y, z)] == '0':
                    self.found_space((y, z))
                        
                else:
                    self.found_border((y, z))
                    
    #Find move finds a move after there are no more c values to be cleared
    #It generates a move randomly based on the remaining untouched spots
    def find_move(self):
        moveara = {}
        g = 0
                
        for s in range(self.size[0]):
            for t in range(self.size[1]):
                if ((self.minefield[(s,t)] == 'c')):
                    move = (s,t)
                    self.cc = self.cc + 1
                
                elif ((self.minefield[(s,t)] == '-')):
                    moveara[g] = (s,t)
                    g = g + 1

        if (self.cc == 0):
            print("Random Move", "\n")
            move = moveara[(random.randrange(0,g))]
                
        return move 

    #AI makes a move after find move returns one, the first move is always random    
    def make_move(self):

        """Note the AI can die due to a mine on the first reveal due to the nature of the Source code""" 
        if self.counter == 0:
            #AI makes a random move to start
            ai_move = random.randrange(0,((self.size[0] * self.size[1]) - 1))        
            
            #Number to coordinate conversion
            row = ai_move % self.size[0]
            column = ai_move % self.size[0]
            self.start_game((row, column))
            self.counter = 1

            if (self.board[(row, column)] == 'm'):
                #print() "\n", "First move RIP!, what are the odds..."
                self.found_mine()
                self.gameover = 1
                          
        else:
            row, column = self.find_move()
        
        #0.25 second wait    
        #time.sleep(0.25)

        #Prints out to the terminal the move and type of move
        print(row, ",", column)

        #Updates the GUI
        root.update()
        
        if (self.board[(row, column)] == 'm'):
            print("RIP!") 
            self.found_mine()              
            self.gameover = 1
            
        elif self.board[(row, column)] == '0':
            print("No mines in sight") 
            self.found_space((row, column))

        elif self.board[(row, column)] == '1':
            print("There is 1 mine next to this spot") 
            self.found_border((row, column))
        else:
            print("There are", self.board[(row, column)], "mines next to this spot") 
            self.found_border((row, column))
            
    #Prints the AI's minefield, the array of tuples
    def print_field(self):
        
        printfield = ""
        for q in range(self.size[0]):
            for p in range(self.size[1]):
                printfield += self.minefield[(q,p)] + "\t"
            printfield += "\n"
        print(printfield) 

    #Allows the AI to flag a space on the minefield
    def ai_flagger(self, space):
       
        if (self.board[space] != 'm'):
            self.print_field()
            print("Incorrectly flagged mine at space: ", space, "\n") 
            self.ic = self.ic + 1
            self.minefield[space] = 'i'
            
        if (self.minefield[space] == '-'):       
            photo = self.get_photo_image('flag.png')
            self.buttons[space].config(command=lambda: None, width=11, height=20, image=photo)
            self.buttons[space].image = photo
            self.flags.append(space)
            self.tv_mines.set(self.tv_mines.get() - 1)
            self.flagcount = self.flagcount + 1
            print("Ai has flagged a mine at space: ", space, "\n") 
            
            #Updates the GUI
            root.update()
            
            self.minefield[space] = 'f'
            self.try_game_over()
            
    #Finds the flags surrounding a spot y,z
    def find_flags(self, y, z):
        flags = 0
        if ((self.minefield[(y,z)] > '0') and (self.minefield[(y,z)] < '9')):
            
            if (y < self.size[0] - 1 and z < self.size[1] - 1):                
                if (self.minefield[(y+1,z+1)] == 'f'):
                    flags = flags + 1
                                            
            if (y < self.size[0] - 1 and z > 0):
                if (self.minefield[(y+1,z-1)] == 'f'):
                    flags = flags + 1

            if (y > 0 and z < self.size[1] - 1):    
                if (self.minefield[(y-1,z+1)] == 'f'):
                    flags = flags + 1

            if (y > 0  and z > 0):
                if (self.minefield[(y-1,z-1)] == 'f'):
                    flags = flags + 1

            if (y < self.size[0] - 1):
                if (self.minefield[(y+1,z)] == 'f'):
                    flags = flags + 1

            if (y > 0):
                if (self.minefield[(y-1,z)] == 'f'):
                    flags = flags + 1

            if (z > 0):
                if (self.minefield[(y,z-1)] == 'f'):
                    flags = flags + 1
                                            
            if (z < self.size[1] - 1):
                if (self.minefield[(y,z+1)] == 'f'):
                    flags = flags + 1
                                   
        return flags
    
    #Places c values around flags where spots are guaranteed to be correct
    def around_flags(self, y, z):
        if ((self.minefield[(y,z)] > '0') and (self.minefield[(y,z)] < '9')):

            #Converts an int to a string character 
            i = self.find_flags(y, z)
            c = ""
            c = '%d' % (i,)
            
            if (self.minefield[(y,z)] == c):
                if (y < self.size[0] - 1 and z < self.size[1] - 1):                
                    if (self.minefield[(y+1,z+1)] == '-'):
                        self.minefield[(y+1,z+1)] = 'c'
                                                
                if (y < self.size[0] - 1 and z > 0):
                    if (self.minefield[(y+1,z-1)] == '-'):
                        self.minefield[(y+1,z-1)] = 'c'

                if (y > 0 and z < self.size[1] - 1):    
                    if (self.minefield[(y-1,z+1)] == '-'):
                        self.minefield[(y-1,z+1)] = 'c'

                if (y > 0  and z > 0):
                    if (self.minefield[(y-1,z-1)] == '-'):
                        self.minefield[(y-1,z-1)] = 'c'

                if (y < self.size[0] - 1):
                    if (self.minefield[(y+1,z)] == '-'):
                       self.minefield[(y+1,z)] = 'c'

                if (y > 0):
                    if (self.minefield[(y-1,z)] == '-'):
                        self.minefield[(y-1,z)] = 'c'

                if (z > 0):
                    if (self.minefield[(y,z-1)] == '-'):
                        self.minefield[(y,z-1)] = 'c'
                                                
                if (z < self.size[1] - 1):
                    if (self.minefield[(y,z+1)] == '-'):
                        self.minefield[(y,z+1)] = 'c'

            #1 - 2 Horizontal Pattern
            if (y - 1 > 0 and y + 1 < self.size[0] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y-1,z)] == '1') and (self.minefield[(y,z)] == '2') and (self.minefield[(y+1,z)] != '-')):
                    
                        if(z + 1 < self.size[1] - 1):
                            if ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f')):

                                space = (y, z+1)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 1 - 2 horizontal", "\n") 
                                    self.minefield[space] = 'c'
                                
                                
                        elif(z - 1 > 0):
                            if ((self.minefield[(y+1,z-1)] == '-') or (self.minefield[(y+1,z-1)] == 'f')):

                                space = (y,z-1)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 1 - 2 horizontal", "\n")         
                                    self.minefield[space] = 'c'

            #1 - 2 Vertical Pattern
            if (z - 1 > 0 and z + 1 < self.size[1] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y,z-1)] == '1') and (self.minefield[(y,z)] == '2') and (self.minefield[(y,z+1)] != '-')):
                    
                        if(y + 1 < self.size[0] - 1):
                            if ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f')):

                                space = (y+1, z)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 1 - 2 vertical", "\n") 
                                    self.minefield[space] = 'c'
                                
                                
                        elif(y - 1 > 0):
                            if ((self.minefield[(y-1,z+1)] == '-') or (self.minefield[(y-1,z+1)] == 'f')):

                                space = (y-1,z)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 1 - 2 vertical", "\n")         
                                    self.minefield[space] = 'c'

            #2 - 1 Horizontal Pattern
            if (y - 1 > 0 and y + 1 < self.size[0] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y-1,z)] != '-') and (self.minefield[(y,z)] == '2') and (self.minefield[(y+1,z)] == '1')):
                    
                        if(z + 1 < self.size[1] - 1):
                            if ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f')):
                
                                space = (y,z+1)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 2 - 1 horizontal", "\n") 
                                    self.minefield[space] = 'c'
                                
                                
                        elif(z - 1 > 0):
                            if ((self.minefield[(y+1,z-1)] == '-') or (self.minefield[(y+1,z-1)] == 'f')):

                                space = (y,z-1)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 2 - 1 horizontal", "\n") 
                                    self.minefield[space] = 'c'

            #2 - 1 Vertical Pattern
            if (z - 1 > 0 and z + 1 < self.size[1] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y,z-1)] != '-') and (self.minefield[(y,z)] == '2') and (self.minefield[(y,z+1)] == '1')):
                    
                        if(y + 1 < self.size[0] - 1):
                            if ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f')):
                
                                space = (y+1,z)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 2 - 1 vertical", "\n") 
                                    self.minefield[space] = 'c'
                                
                                
                        elif(y - 1 > 0):
                            if ((self.minefield[(y-1,z+1)] == '-') or (self.minefield[(y-1,z+1)] == 'f')):

                                space = (y-1,z)
                                if (self.minefield[space] == '-'):
                                    print("Attempting 2 - 1 vertical", "\n") 
                                    self.minefield[space] = 'c'
    
    #Finds the surrounding flags and surrounding untouched spaces
    def find_surrounding(self, y, z):
        surrounding = 0
        if ((self.minefield[(y,z)] > '0') and (self.minefield[(y,z)] < '9')):                                       
            if (y < self.size[0] - 1 and z < self.size[1] - 1):
                if ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f')):
                    surrounding = surrounding + 1
                                            
            if (y < self.size[0] - 1 and z > 0):
                if ((self.minefield[(y+1,z-1)] == '-') or (self.minefield[(y+1,z-1)] == 'f')):
                    surrounding = surrounding + 1

            if (y > 0 and z < self.size[1] - 1):    
                if ((self.minefield[(y-1,z+1)] == '-') or (self.minefield[(y-1,z+1)] == 'f')):
                    surrounding = surrounding + 1

            if (y > 0  and z > 0):
                if ((self.minefield[(y-1,z-1)] == '-') or (self.minefield[(y-1,z-1)] == 'f')):
                    surrounding = surrounding + 1

            if (y < self.size[0] - 1):
                if ((self.minefield[(y+1,z)] == '-') or (self.minefield[(y+1,z)] == 'f')):
                    surrounding = surrounding + 1

            if (y > 0):
                if ((self.minefield[(y-1,z)] == '-') or (self.minefield[(y-1,z)] == 'f')):
                    surrounding = surrounding + 1

            if (z > 0):
                if ((self.minefield[(y,z-1)] == '-') or (self.minefield[(y,z-1)] == 'f')):
                    surrounding = surrounding + 1
                                            
            if (z < self.size[1] - 1):
                if ((self.minefield[(y,z+1)] == '-') or (self.minefield[(y,z+1)] == 'f')):
                    surrounding = surrounding + 1
                                   
        return surrounding
    
    #This function does a majority of the flagging for the AI
    #Currently it implements three types of patterns
    #The first type of pattern is the number touching equals the value of a numbered square
    #The second type is the 1 - 2 - 2 - 1 (vertical and horizontal varients)
    #The third type is the 1 - 2 - 1 (vertical and horizontal varients)
    def solve_minefield(self):
        for y in range(self.size[0]):
            for z in range(self.size[1]):

                #Converts an int to a string character                                
                i = self.find_surrounding(y,z)
                c = ""
                c = '%d' % (i,)

                #Touching equals boarder pattern
                if ((self.minefield[(y,z)] == c) and (self.minefield[(y,z)] != ' ') and (self.minefield[(y,z)] != 'c')):
                    if (y < self.size[0] - 1 and z < self.size[1] - 1):
                        if (self.minefield[(y+1,z+1)] == '-'):
                            space = (y+1,z+1)
                            self.ai_flagger(space)
                                                                    
                    if (y < self.size[0] - 1 and z > 0):
                        if (self.minefield[(y+1,z-1)] == '-'):
                            space = (y+1,z-1)
                            self.ai_flagger(space)

                    if (y > 0 and z < self.size[1] - 1):
                        if (self.minefield[(y-1,z+1)] == '-'):
                            space = (y-1,z+1)
                            self.ai_flagger(space)

                    if (y > 0  and z > 0):
                        if (self.minefield[(y-1,z-1)] == '-'):
                            space = (y-1,z-1)
                            self.ai_flagger(space)

                    if (y < self.size[0] - 1):
                        if (self.minefield[(y+1,z)] == '-'):
                            space = (y+1,z)
                            self.ai_flagger(space)

                    if (y > 0):
                        if (self.minefield[(y-1,z)] == '-'):
                            space = (y-1,z)
                            self.ai_flagger(space)

                    if (z > 0):
                        if (self.minefield[(y,z-1)] == '-'):
                            space = (y,z-1)
                            self.ai_flagger(space)

                    if (z < self.size[1] - 1):
                        if (self.minefield[(y,z+1)] == '-'):
                            space = (y,z+1)
                            self.ai_flagger(space)
                                       
                #1 - 2 - 2 - 1 horizontal pattern
                if (y - 1 > 0 and y + 1 < self.size[0] - 1 and y + 2 < self.size[0] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y-1,z)] == '1') and (self.minefield[(y,z)] == '2') and (self.minefield[(y+1,z)] == '2') and (self.minefield[(y+2,z)] == '1')):
                    
                        if(z + 1 < self.size[1] - 1):
                            if (((self.minefield[(y,z+1)] == '-') or (self.minefield[(y,z+1)] == 'f')) and ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f'))):
                                print("Attempting 1 - 2 - 2 - 1 horizontal", "\n") 
                                space = (y-1, z+1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                                space = (y,z+1)
                                self.ai_flagger(space)
                                
                                space = (y+1,z+1)
                                self.ai_flagger(space)

                                space = (y+2, z+1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                        elif(z - 1 > 0):
                            if (((self.minefield[(y,z-1)] == '-') or (self.minefield[(y,z-1)] == 'f')) and ((self.minefield[(y+1,z-1)] == '-') or (self.minefield[(y+1,z-1)] == 'f'))):
                                print("Attempting 1 - 2 - 2 - 1 horizontal", "\n") 
                                space = (y-1, z-1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'

                                space = (y,z-1)
                                self.ai_flagger(space)
                                
                                space = (y+1,z-1)
                                self.ai_flagger(space)

                                space = (y+2, z-1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                #1 - 2 - 1 horizontal pattern
                if (y - 1 > 0 and y + 1 < self.size[0] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y-1,z)] == '1') and (self.minefield[(y,z)] == '2') and (self.minefield[(y+1,z)] == '1')):
                    
                        if(z + 1 < self.size[1] - 1):
                            if (((self.minefield[(y-1,z+1)] == '-') or (self.minefield[(y-1,z+1)] == 'f')) and ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f'))):
                                print("Attempting 1 - 2 - 1 horizontal", "\n") 
                                space = (y-1,z+1)
                                self.ai_flagger(space)

                                space = (y, z+1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                                space = (y+1,z+1)
                                self.ai_flagger(space)
                                
                        elif(z - 1 > 0):
                            if (((self.minefield[(y-1,z-1)] == '-') or (self.minefield[(y-1,z-1)] == 'f')) and ((self.minefield[(y+1,z-1)] == '-') or (self.minefield[(y+1,z-1)] == 'f'))):
                                print("Attempting 1 - 2 - 1 horizontal", "\n") 
                                space = (y-1,z-1)
                                self.ai_flagger(space)

                                space = (y,z-1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                                space = (y+1,z-1)
                                self.ai_flagger(space)
                                
                #1 - 2 - 2 - 1 vertical pattern
                if (z - 1 > 0 and z + 1 < self.size[1] - 1 and z + 2 < self.size[1] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y,z-1)] == '1') and (self.minefield[(y,z)] == '2') and (self.minefield[(y,z+1)] == '2') and (self.minefield[(y,z+2)] == '1')):
                    
                        if(y + 1 < self.size[0] - 1):
                            if (((self.minefield[(y+1,z)] == '-') or (self.minefield[(y+1,z)] == 'f')) and ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f'))):
                                print("Attempting 1 - 2 - 2 - 1 vertical", "\n") 
                                space = (y+1, z-1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[(y+1,z-1)] = 'c'

                                space = (y+1,z)
                                self.ai_flagger(space)
                                
                                space = (y+1,z+1)
                                self.ai_flagger(space)

                                space = (y+1, z+2)
                                if (self.minefield[space] == '-'):
                                    self.minefield[(y+1,z+2)] = 'c'
                                
                        elif(y - 1 > 0):
                            if (((self.minefield[(y-1,z)] == '-') or (self.minefield[(y-1,z)] == 'f')) and ((self.minefield[(y-1,z+1)] == '-') or (self.minefield[(y-1,z+1)] == 'f'))):
                                print("Attempting 1 - 2 - 2 - 1 vertical", "\n") 
                                space = (y-1, z-1)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                                space = (y-1,z)
                                self.ai_flagger(space)
                                
                                space = (y-1,z+1)
                                self.ai_flagger(space)

                                space = (y-1, z+2)
                                if (self.minefield[space] == '-'):
                                    self.minefield[space] = 'c'
                                
                #1 - 2 - 1 vertical pattern
                if (z - 1 > 0 and z + 1 < self.size[1] - 1 and (self.find_surrounding(y,z) <= self.find_flags(y,z))):
                    if ((self.minefield[(y,z-1)] == '1') and (self.minefield[(y,z)] == '2') and (self.minefield[(y,z+1)] == '1')):
                        
                        if(y + 1 < self.size[0] - 1):
                            if (((self.minefield[(y+1,z-1)] == '-') or (self.minefield[(y+1,z-1)] == 'f')) and ((self.minefield[(y+1,z+1)] == '-') or (self.minefield[(y+1,z+1)] == 'f'))):
                                print("Attempting 1 - 2 - 1 vertical", "\n") 
                                space = (y+1,z-1)
                                self.ai_flagger(space)

                                space = (y+1,z)
                                if (self.minefield[space] == ' '):
                                    self.minefield[space] = 'c'
                                
                                space = (y+1,z+1)
                                self.ai_flagger(space)
                                
                        elif(y - 1 > 0):
                            if (((self.minefield[(y-1,z-1)] == '-') or (self.minefield[(y-1,z-1)] == 'f')) and ((self.minefield[(y-1,z+1)] == '-') or (self.minefield[(y-1,z+1)] == 'f'))):
                                print("Attempting 1 - 2 - 1 vertical", "\n") 
                                space = (y-1,z-1)
                                self.ai_flagger(space)

                                space = (y-1,z)
                                if (self.minefield[space] == ' '):
                                    self.minefield[space] = 'c'
                                
                                space = (y-1,z+1)
                                self.ai_flagger(space)      
                                                
####################################################################################################################
####################################################################################################################        

    def get_size(self):
        if self.level == "Custom":
            return (int(self.custom_height.get()), int(self.custom_width.get()))
        #Edited Advanced to be 22 by 22 and have 100 mines 
        sizes = {"Beginner": (9, 9), "Intermediate": (16, 16), "Advanced": (22, 22)} 
        return sizes[self.level]

    def get_num_mines(self):
        if self.level == "Custom":
            return int(self.custom_mines.get())
        mines = {"Beginner": 10, "Intermediate": 40, "Advanced": 100}
        return mines[self.level]

    def add_board(self):
        self.board = {}
        for key in self.buttons:
            self.buttons[key].destroy()
        self.buttons = {}
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                key = (i, j)
                if key in self.mines:
                    self.board[key] = 'm'
                else:
                    self.board[key] = str(self.get_mine_count(key))
                self.add_button(key, width=1, height=1, command=lambda x=key:self.start_game(x))
        #print(self)

    def start_game(self, space):
        self.tick()
        for key, value in self.board.items():
            self.configure_command(key)
        #if self.level != "Custom":
            #self.stats.play_game(self.level)
        self.buttons[space].invoke()

    def tick(self):
        self.tv_timer.set(self.tv_timer.get() + 1)
        self.timer = self.time.after(1000, self.tick)

    def mark_mine(self, arg):
        space = None
        for key, value in self.buttons.items():
            if value == arg.widget:
                space = key
        if space in self.questions:
            self.buttons[space].destroy()
            self.add_button(space, width=1, height=1)
            self.configure_command(space)
            self.questions.remove(space)
        elif space in self.flags:
            self.buttons[space].destroy()
            self.add_button(space, width=1, height=1, text="?")
            self.flags.remove(space)
            self.questions.append(space)
            self.tv_mines.set(self.tv_mines.get() + 1)
        else:
            photo = self.get_photo_image('flag.png')
            self.buttons[space].config(command=lambda: None, width=11, height=20, image=photo)
            self.buttons[space].image = photo
            self.flags.append(space)
            self.tv_mines.set(self.tv_mines.get() - 1)
        self.try_game_over()

    def configure_command(self, key):
        if self.board[key] == 'm':
            self.buttons[key].config(command=self.found_mine)
        elif hasattr(self, "timer"):
            if self.board[key] == '0':
                self.buttons[key].config(command=lambda x=key:self.found_space(x))
            elif self.board[key] != 'm':
                self.buttons[key].config(command=lambda x=key:self.found_border(x))
        else:
            self.buttons[key].config(command=lambda x=key:self.start_game(x))

    def add_button(self, key, **kwargs):
        self.buttons[key] = Button(self.frame, **kwargs)
        self.buttons[key].grid(row=key[0], column=key[1])
        self.buttons[key].bind("<Button-3>", self.mark_mine)

    def get_mines(self):
        mines = []
        while len(mines) < self.num_mines:
            mine = (random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1))
            if mine not in mines:
                mines.append(mine)
        return mines

    def get_mine_count(self, key):
        count = 0
        for i in range(3):
            for j in range(3):
                if (key[0] + i - 1, key[1] + j - 1) in self.mines:
                    count += 1
        return count

    def found_space(self, key):
        self.board[key] = " "
        self.clear_button(key)
        for i in range(3):
            for j in range(3):
                space = (key[0] + i - 1, key[1] + j - 1)
                if (space in self.board) and (space not in self.flags + self.questions):
                    if self.board[space] == '0':
                        self.found_space(space)
                        
                        #places a space in the AI minefield
                        self.minefield[space] = self.board[space]
                        
                    elif self.board[space] != 'm':
                        self.clear_button(space)
                        
                        #places a space in the AI minefield
                        self.minefield[space] = self.board[space]
                        
        self.try_game_over()

    def clear_button(self, key):
        self.buttons[key].destroy()
        self.buttons[key] = Label(self.frame, text=self.board[key])
        self.buttons[key].grid(row=key[0], column=key[1])

    def found_mine(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                key = (i, j)
                if self.board[key] == 'm' and (key not in self.flags + self.questions):
                    self.buttons[key].destroy()
                    photo = self.get_photo_image('mine.gif')
                    self.buttons[key] = Label(self.frame, image=photo)
                    self.buttons[key].image = photo
                    self.buttons[key].grid(row=i, column=j)

                    #places a mine in the AI minefield
                    #if self.minefield[key] != 'f' and self.gameover != 0:
                    #  self.minefield[key] = self.board[key]
                    
                if isinstance(self.buttons[key], Button):
                    self.buttons[key].config(command=lambda:None)
                    self.buttons[key].unbind("<Button-3>")
                    
        if hasattr(self, "timer"):
            self.time.after_cancel(self.timer)
            
        #if self.level != "Custom":
            #self.stats.lose(self.level)

        #time.sleep(1)
                
        #if (self.aic == 1):
        #    self.AI()


    def found_border(self, key):
        self.buttons[key].destroy()
        self.buttons[key] = Label(self.frame, width=1, height=1, text=self.board[key])
        self.buttons[key].grid(row=key[0], column=key[1])

        #places a border in the AI minefield
        self.minefield[key] = self.board[key]
        
        self.try_game_over()        

    def try_game_over(self):
        num_btn = 0
        mines_found = 0
        
        if (self.wc == 0):
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if isinstance(self.buttons[(i, j)], Button):
                        num_btn += 1
                        if self.board[(i, j)] == 'm' and (i, j) in self.flags:
                            mines_found += 1
            if (num_btn ==  mines_found == self.num_mines):
                for key, value in self.buttons.items():
                    value.unbind("<Button-3>")
                if self.level != "Custom":
                    self.wc = 1
                    self.time.after_cancel(self.timer)
                    #self.stats.win(self.level, self.tv_timer.get())
        else:
            return

    def get_photo_image(self, image):
        return ImageTk.PhotoImage(Image.open(image))

    def __str__(self):
        s = ""
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                s += self.board[(i, j)] + "\t"
            s += "\n"
        return s

if __name__ == "__main__":
    root = Tk()
    minesweeper = Minesweeper(root)
    root.mainloop()
