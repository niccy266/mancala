from tkinter import *
from functools import partial
from random import randint
from math import floor
from tkinter import messagebox
import sys




class MancalaGame() :



    def __init__(self, root) :

        #lets the ai play solo for a loooooong time
        sys.setrecursionlimit(1000000)

        #setting up the window in the object
        self.root = root
        self.root.title("Mancala")


        #declaring constant variables
        #size of canvas
        self.BOARD_WIDTH = 1200
        self.BOARD_HEIGHT = 600
        #self.BOARD_WIDTH = root.winfo_screenwidth()
        #self.BOARD_HEIGHT = root.winfo_screenheight()

        #space between pools
        self.GAP = 5

        #number of rows on the board
        self.NUM_ROWS = 2

        #default number of pools per side, and a min and max for the user's selection
        self.START_NUM_POOLS = 6
        self.MIN_POOLS = 1
        self.MAX_POOLS = 100

        #default number of pebbles per pool, and a min and max for the user's selection
        self.START_NUM_PEBBLES = 4
        self.MIN_PEBBLES = 1
        self.MAX_PEBBLES = 100

        #the default speed that the game plays at
        self.ANIMATION_SPEED = 100
        self.MIN_SPEED = 0
        self.MAX_SPEED = 20

        #the colours I chose to be used in the game
        self.CANVAS_COL = "#72583b"
        self.POOL_COL = "#dcbe8c"
        self.COUNTER_BG = "beige"

        #the font used by buttons in the menus
        self.BUTTON_FONT = ("Helvetica", "8")


        #declaring the settings at default values from constants
        #I used a dictionary here because I could call self.settings[variable] where the variable was the name of the setting being changed
        #rather than having if statements for each setting and a line of code for self.speed, self.pools, etc.
        self.settings = {"pools": self.START_NUM_POOLS, "pebbles": self.START_NUM_PEBBLES, "speed": self.ANIMATION_SPEED}



        #making canvas
        self.Board = Canvas(self.root, width = self.BOARD_WIDTH, height = self.BOARD_HEIGHT, bg = self.CANVAS_COL)

        #attaching the click event to the canvas
        self.Board.bind("<Button-1>", self.click)

        #packing the canvas onto the window
        self.Board.pack()


        self.ai_playing = False

        #creating controls
        #text entry for editing settings
        self.Text_Entry = Entry(self.root, width = 30)

        #creating quit button here, as it is used in multiple functions
        self.Quit_Button = Button(self.root, text = "Quit", width = 20, command = self.quit, bg = self.POOL_COL, font = self.BUTTON_FONT)
        self.Next_Level = Button(self.root, text = "Next Level", width = 20, command = self.next_level, bg = self.POOL_COL, font = self.BUTTON_FONT)

        #calling the function that sets up the game on the canvas
        self.start_game()

        #updating canvas with everything that's been drawn onto it
        self.Board.update()




    class area() :



        def __init__(self, x, y, w, h, pool, col, count, last):

            #saving given information
            self.x = x
            self.y = y
            self.width = w
            self.height = h
            self.pool = pool
            self.colour = col
            self.count = count

            #the x2 and y2 variable could be calculated outside the object, but they are used more than once,
            #for drawing the pools and defining where they are click-able, so I have calculated them here for ease of access
            self.x2 = x + w
            self.y2 = y + h

            #this is for storing the ids of the pebbles that are drawn in the pool, so they can be deleted individually
            self.pebble_IDs = []




    def start_game(self) :

        #stops the player from activating any of the pools while the game is still building
        self.player_turn = False
        
        #stops the player from activating any of the pools while the game is still building
        
        
        ai_temp = self.ai_playing
        print(ai_temp)
        self.ai_playing = False
            

        #the game has not started yet
        self.game_over = True

        #clears the list of click-able areas
        self.areas = []

        #which area is the player's bank
        self.player_bank = self.settings["pools"]
        #which area is the computer's bank
        self.computer_bank = self.player_bank * 2 + 1

        #there is a bank on either side of the board, so the total number of columns is two more than the number of pools per side
        total_columns = self.player_bank + 2

        #recalculates the size of each pool based on the number of pools there are
        self.pool_width = (self.BOARD_WIDTH - (total_columns + 1) * self.GAP) / total_columns
        self.pool_height = (self.BOARD_HEIGHT - (self.NUM_ROWS + 1) * self.GAP) / self.NUM_ROWS

        #deleting all items from the canvas, including menus, displays, pools and their pebbles
        self.Board.delete(ALL)

        #this list stores the IDs of all the controls that make up the currently open menu screen,
        #so they can be deleted from the canvas individually.
        #this line also clears the list in a new game as the controls have all been deleted
        self.menu_control_IDs = []

        #if the menu was open before, it's now closed
        self.menu_open = False

        #this list stores the IDs of the controls used in thew AI's display
        self.ai_display_IDs = []

        #draws the title on the screen
        self.Board.create_text(self.BOARD_WIDTH/2, self.BOARD_HEIGHT/2, text = "MANCALA", font = ("Helvetica", "32"), fill = self.POOL_COL)
        self.Board.update()

        #after a delay, starts building the game. 
        #This delay is the same no matter what the player's chosen speed is, else it becomes way too long on the higher settings
        self.root.after(15 * self.ANIMATION_SPEED)

        #clears the title screen
        self.Board.delete(ALL)


        #creates a menu button
        Menu_Button = Button(self.root, text = "Menu", width = 20, command = self.open_menu, bg = self.POOL_COL)

        #places it in the bottom left corner
        self.Board.create_window(0, self.BOARD_HEIGHT, window = Menu_Button, height = 25, width = 100, anchor = SW)



        #drawing the pools with nothing in them
        for row in range(self.NUM_ROWS) :
            #for each row

            for reverse_col, column in enumerate(reversed(range(self.player_bank))) :
                #for each pool in the row

                #calculates where the pool should be drawn from
                point = {"x": (self.GAP + self.pool_width) * (reverse_col + 1) + self.GAP     if row == 0 else     (self.GAP + self.pool_width) * (column + 1) + self.GAP,
                         "y": self.GAP + (self.pool_height + self.GAP) * (1-row)}

                #sends the start coordinates and the dimensions of the pool into a pool object
                #which calculates the coordinates for the draw method
                pool = self.area(point["x"], point["y"], self.pool_width, self.pool_height, len(self.areas), self.POOL_COL, self.settings["pebbles"], self.settings["pebbles"])

                #the pool object is saved to a list
                #this saves the coordinates of each pool so the click method knows where the pools are and they can be redrawn when necessary
                self.areas.append(pool)

            #creates banks on left and right
            point = {"x": self.BOARD_WIDTH - (self.GAP + self.pool_width),   "y": self.GAP}       if row == 0 else       {"x": self.GAP,    "y": self.GAP}
            pool = self.area(point["x"], point["y"], self.pool_width, self.GAP + self.pool_height * 2, len(self.areas), self.POOL_COL, 0, 0)
            self.areas.append(pool)


        #the player pools are a range of pools from 0 to the player's bank - 1, which is what this line of code represents
        player_pools = range(self.player_bank)

        #creates labels for the player's pools
        for pool in player_pools :

            #calculating the x and y positions for the label
            x = (self.GAP + self.pool_width) * (pool + 1) + self.GAP * 3
            y = self.pool_height * 2 + self.GAP

            #drawing the label
            self.Board.create_text(x, y, text = pool + 1)


        #drawing the starting pebbles and the counters for the pools
        for pool in self.areas : self.Board.create_oval(pool.x, pool.y, pool.x2, pool.y2, fill = pool.colour)
        self.Board.update()

        #adds a delay before starting to draw pebbles in the pools
        self.root.after(10 * self.settings["speed"])
        self.draw_board()

        #at the start of the game, no moves have been started
        self.playing = False

        #the player always goes first, so it's their turn at the start of each game
        #now that the board is built, the user can play
        self.player_turn = True

        #lets the program know the game has started
        self.game_over = False

        #recalling if the game is AI vs AI
        self.ai_playing = ai_temp
        if self.ai_playing :
            self.root.after(10 * self.settings["speed"])
            #print("Playing as the first AI")
            self.ai_turn(side = 0)



    def draw_board(self) :

        #draws all the pebbles in the pools
        for pool in self.areas :
            self.update_pool(pool)



    def update_pool(self, pool) :

        #deletes the pebbles already in the pool and the counter for the pool
        for pebble in pool.pebble_IDs : self.Board.delete(pebble)

        #drawing the counter for the pool
        #draws a rectangle
        pool.pebble_IDs.append(self.Board.create_rectangle(pool.x, pool.y, pool.x + 20, pool.y + 20, fill = self.COUNTER_BG))
        #writes the number of pebbles in the pool in the rectangle
        pool.pebble_IDs.append(self.Board.create_text(pool.x + 10, pool.y + 10, text = pool.count))

        
        #list of hexadecimal characters for picking a random hex colour
        HEX = "0123456789ABCDEF"

        #draws pebbles for the pool
        pebble_radius = self.pool_width / 6
        for pebble in range(pool.count) :

            #picks a random position for the pebble
            x = pool.x + randint(0, floor(pool.width/3)) + pool.width/3
            y = pool.y + randint(0, floor(pool.height/3)) + pool.height/3

            #picks a random colour
            hex_colour = "#" + "".join(HEX[randint(0, 15)] for i in range(6))

            #draws the pebble
            pool.pebble_IDs.append(self.Board.create_oval(x - pebble_radius, y- pebble_radius, x + pebble_radius, y + pebble_radius, fill = hex_colour))
        
        
        #tag_raise is a command that raises an object on the canvas to the top layer, so it is displayed in front of other things drawn on the canvas.
        #this is useful when the AI is playing, because it draws the pebbles over the "AI's turn" display, this code avoids that
        for AI_Control in self.ai_display_IDs : self.Board.tag_raise(AI_Control)
        for Menu_Control in self.menu_control_IDs : self.Board.tag_raise(Menu_Control)

        #updates the canvas
        self.Board.update()

        #pauses before exiting the function
        self.root.after(self.settings["speed"])



    #play functions

    def click(self, event) :

        #checks if the player has already started a move
        if not self.playing : 

            #this checks if the player clicked a pool on their side

            #for each of the saved areas on the player's side
            for area in self.areas[:self.player_bank] :

                #checks if the x and y of the click is within the area
                if event.y > area.y and event.y < area.y2 and event.x > area.x and event.x < area.x2 :

                    #saves the area's number
                    clicked = area.pool

                    #if the pool that the user clicked was on the player's side, it activates the pool
                    if clicked in range(self.player_bank) and self.player_turn and area.count != 0 : 
                        self.playing = True
                        self.activate_pool(clicked)

                    #exits the function, exiting the loop
                    return



    def ai_turn(self, side = 1) :

        #at the start of the AI's turn, a window saying "AI's turn" appears on the player's side of the board,
        #so that the player doesn't attempt to play when it is not their turn

        if side:
            #draws the box
            self.ai_display_IDs.append(self.Board.create_rectangle(self.BOARD_WIDTH / 4, 5 * self.BOARD_HEIGHT / 8, 3 * self.BOARD_WIDTH / 4, 7 * self.BOARD_HEIGHT / 8, fill = self.CANVAS_COL, outline = self.POOL_COL))
            #draws the text
            self.ai_display_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, 5 * self.BOARD_HEIGHT / 8, text = "AI's turn", font = ("Helvetica", "80"), fill = self.POOL_COL, anchor = N))
        else:
            #draws the box
            self.ai_display_IDs.append(self.Board.create_rectangle(self.BOARD_WIDTH / 4, self.BOARD_HEIGHT / 8, 3 * self.BOARD_WIDTH / 4, 3 * self.BOARD_HEIGHT / 8, fill = self.CANVAS_COL, outline = self.POOL_COL))
            #draws the text
            self.ai_display_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, self.BOARD_HEIGHT / 8, text = "AI's turn", font = ("Helvetica", "80"), fill = self.POOL_COL, anchor = N))

        #raises any menus that are open above the new window
        for Menu_Control in self.menu_control_IDs : self.Board.tag_raise(Menu_Control)

        #updates the board to show the window
        self.Board.update()

        #adds a delay before the AI makes it's move
        self.root.after(10 * self.settings["speed"])

        #checks which pools on the AI's side have any pebbles and so can be played, saves them to a list
        options = []
        if side :
            for pool in self.areas[self.player_bank + 1 : self.computer_bank] :
                if pool.count != 0 : options.append(pool)

            #the options list is currently ordered from pools closest to the player's side rather than starting closest to the AI's bank
            #I reversed the order, because it is usually more likely that activating a second turn closer to the bank is a better option,
            #as it lets other options that are further away and give a second turn be used in the second turn without covering the other ones
            options.reverse()
        else: 
            for pool in self.areas[0: self.player_bank] :
                if pool.count != 0 : options.append(pool)

        #goes through the list of options
        good_options = []
    


        for pool in options :

            #saves the number of times the pebbles go around the board, starting at one
            times_around_board = 1

            #finding where the last pebble would land
            
            #starting from current pool
            current_pool = pool.pool
            #gets the number of pebbles that are in the pool
            pebbles = self.areas[current_pool].count
            #while there are pebbles left in hand
            
            while pebbles > 0 : 
                #moves on to the next pool
                current_pool += 1
                #if passed the last pool, go back to the first pool
                if current_pool > self.computer_bank + side - 1: 
                    current_pool -= self.computer_bank + side
                    times_around_board += 1
                    
                #if the next pool is the other side's bank, the pool is skipped
                if side:
                    if current_pool != self.player_bank   :
                        #saves the pool's number so we know which was the last pool a pebble landed in
                        last_pool = current_pool
                        #now have one less
                        pebbles -= 1
                else :
                    if current_pool != self.computer_bank  :
                        #saves the pool's number so we know which was the last pool a pebble landed in
                        last_pool = current_pool
                        #now have one less
                        pebbles -= 1 
  
            
            #if the last pebble would land in the AI's bank, it immediately chooses this option because it will get an extra turn
            if side:
                if last_pool == self.computer_bank :

                    #activates the pool to get a second turn
                    self.activate_pool(pool.pool)

                    #exits function, as the AI has played
                    return

                else :
                    #if the last pebble would land in the activated pool, then it would be empty plus however many times the pebbles went around the board
                    last_pool_count = (self.areas[last_pool].count if last_pool != pool.pool else 0)

                    #if the number of pebbles in the last pool is 1 after all the moves, then the last pebbles landed in an empty pool
                    last_pool_empty = last_pool_count + times_around_board == 1

                    #if the last pool is subtracted by the number of the player's bank + 1, then it's puts the AI's banks in the range of 0 to the player's bank
                    last_pool_on_own_side = last_pool - self.player_bank - 1 in range(self.player_bank)

                    #checks if the last pebble lands in an empty pool on the AI's side
                    if last_pool_on_own_side and last_pool_empty :
                        #if this move would land in an empty pool on the AI's side, it saves the option as a good option
                        good_options.append(pool)
            else : 
                if last_pool == self.player_bank :

                    #activates the pool to get a second turn
                    self.activate_pool(pool.pool)

                    #exits function, as the AI has played
                    return

                else :
                    #if the last pebble would land in the activated pool, then it would be empty plus however many times the pebbles went around the board
                    last_pool_count = (self.areas[last_pool].count if last_pool != pool.pool else 0)

                    #if the number of pebbles in the last pool is 1 after all the moves, then the last pebbles landed in an empty pool
                    last_pool_empty = last_pool_count + times_around_board == 1

                    #if the last pool is subtracted by the number of the player's bank + 1, then it's puts the AI's banks in the range of 0 to the player's bank
                    last_pool_on_own_side = last_pool - 1 in range(self.player_bank)

                    #checks if the last pebble lands in an empty pool on the AI's side
                    if last_pool_on_own_side and last_pool_empty :
                        #if this move would land in an empty pool on the AI's side, it saves the option as a good option
                        good_options.append(pool)     


        #if there are any good options, the AI will pick randomly from the good options it found
        if len(good_options) > 0 :
            #picks a random number between 0 and the number of good_options there are
            rand_pool = randint(0, len(good_options)-1)

            #activates the pool from the option chosen by the random number
            self.activate_pool(good_options[rand_pool].pool)

        else :
            #if there were no particularly good options, the AI just picks a random pool from the options list

            #picks a random number
            rand_pool = randint(0, len(options)-1)

            #activated the option with that number
            self.activate_pool(options[rand_pool].pool)




    def activate_pool(self, activated) :

        #this function can be used by both the player and the AI
        #the number passed into this function is always within the range of pools being used
        #so I don't need to check that it's withing the range of pools

        #if the pool passed into this function is the player's or computer's bank, it does nothing
        #if it's not a bank, then it's a playable pool.
        if not activated in [self.player_bank, self.computer_bank] :

            if self.player_turn :
                bank = self.player_bank
                opposite_bank = self.computer_bank
            else : 
                bank = self.computer_bank
                opposite_bank = self.player_bank

            #move starts at the pool that was clicked
            current_pool = activated

            #gets the number of pebbles that are in the pool
            pebbles = self.areas[current_pool].count

            #takes the pebbles out of the chosen pool and updates it
            self.areas[current_pool].count = 0
            self.update_pool(self.areas[current_pool])

            #while there are pebbles left in hand
            while pebbles > 0 : 

                #moves on to the next pool
                current_pool += 1

                #if passed the last pool, go back to the first pool
                if current_pool > self.computer_bank : current_pool -= self.computer_bank + 1

                #if the next pool is the other side's bank, the pool is skipped
                if not current_pool == opposite_bank :

                    #adds a pebble to the current pool
                    self.areas[current_pool].count += 1

                    #saves the pool's number so we know which was the last pool a pebble landed in
                    last_pool = current_pool

                    #updates the pool on the board
                    self.update_pool(self.areas[current_pool])

                    #now have one less pebble
                    pebbles -= 1

            #counts up how many pebbles are on each side of the board. if either side is empty, the function skips to ending the game
            row1_total = self.check_row(self.areas[:self.player_bank])
            row2_total = self.check_row(self.areas[self.player_bank + 1 : self.computer_bank])

            #checks if the player gets a second turn if it's the player's turn, or if the ai gets a second turn if it's the AI's turn
            if ((self.player_turn and last_pool == self.player_bank) or ((not self.player_turn) and last_pool == self.computer_bank)) and (row1_total != 0 and row2_total != 0) :

                if not self.player_turn:
                    #if the AI gets a second turn, it will just play again
                    self.ai_turn()
                else :
                    #if it's the player's turn, a display pops up at the top of the screen letting the player know they get another turn
                    if (self.ai_playing): self.ai_turn(side=0)
                    else:
                        
                        #saves id's of display
                        bonus_turn_display_IDs = []

                        #creates the display
                        bonus_turn_display_IDs.append(self.Board.create_rectangle(self.BOARD_WIDTH / 4, self.BOARD_HEIGHT / 8, 3 * self.BOARD_WIDTH / 4, 3 * self.BOARD_HEIGHT / 8, fill = self.CANVAS_COL, outline = self.POOL_COL))
                        bonus_turn_display_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, self.BOARD_HEIGHT / 8, text = "Extra Turn", font = ("Helvetica", "80"), fill = self.POOL_COL, anchor = N))

                        #raises any menus that are open above the new window
                        for Menu_Control in self.menu_control_IDs : self.Board.tag_raise(Menu_Control)

                        #makes the board updates, then removes the display after a delay
                        self.Board.update()
                        self.root.after(5 * self.settings["speed"])

                        #deleting each item from the display
                        for widget in bonus_turn_display_IDs : self.Board.delete(widget)
            else :
                #if the player or AI didn't land in their bank, this checks if they landed in an empty pool on their side

                #finds out how many pebbles are in the pool opposite the last pool
                opposite_pool = (self.player_bank * 2 - last_pool)

                #tests if the last pebble landed on the side it came from
                landed_on_own_side = (self.areas[last_pool].pool if self.player_turn else self.areas[last_pool].pool - self.player_bank - 1) in range(self.player_bank)
                #tests if the pool was empty before the last pebble landed in it, case being it should now have one pebble
                pool_was_empty = self.areas[last_pool].count == 1

                #checking if the last pebble landed in an empty pool on the playing side
                if pool_was_empty and landed_on_own_side :

                    #saves the pool number of the playing side's bank
                    bank = self.player_bank if self.player_turn else self.computer_bank

                    #takes the pebbles from the last pool and it's opposite pool to the active side's bank
                    self.areas[bank].count += self.areas[opposite_pool].count + 1

                    #set's the pools to empty
                    self.areas[opposite_pool].count = 0
                    self.areas[last_pool].count = 0

                    #updates the pools on the board that were changed
                    self.update_pool(self.areas[opposite_pool])
                    self.update_pool(self.areas[last_pool])
                    self.update_pool(self.areas[bank])

                #whether the player stole extra pebbles or not, it is no longer their turn.
                #this toggles whoever's turn it is
                self.player_turn = not self.player_turn

                #calls the function for when a turn ends
                self.turn_end()

            #let's the program know that the move has ended, so the player can make their next move
            self.playing = False



    def turn_end(self) :

        #deletes the "ai_turn" display
        for control in self.ai_display_IDs : self.Board.delete(control)

        #gets the total number of pebbles in the player's pools (not including their bank)
        total = self.check_row(self.areas[:self.player_bank])
        #gets the same total for the pools on the AI's side
        total2 = self.check_row(self.areas[self.player_bank + 1 : self.computer_bank])

        #if either side has run out of pebbles, the game is over
        if total == 0 or total2 == 0:

            #makes the player unable to play, because the game is over
            self.player_turn = False

            #calls the game end function
            self.game_end()

        #if the game is still on, and it's no longer the player's turn, then the ai plays
        elif not self.player_turn: self.ai_turn()
        elif (self.ai_playing) : self.ai_turn(side=0)
        



    def check_row(self, pools) :

        #adds up the total for a set of pools

        #declaring total variable to add to
        total = 0
        #for each pool given
        for pool in pools :
            #adds the number of pebbles in this pool to the total
            total += pool.count

        #returns the total number of pebbles
        return total



    def game_end(self) :

        #clearing the screen and changing variables

        #if it was the AI's turn at the end of the game, this line makes sure the "AI' turn" display is gone
        for control in self.ai_display_IDs : self.Board.delete(control)

        #stops the player from being able to click the pools after the game has ended
        self.player_turn = False

        #changes the behavior of other functions by letting them know the game is not active anymore
        self.game_over = True

        #closes any open menus
        self.close_menu()



        #packing up the board

        #counts up the number of pebbles left on the player's side of the board
        player_side_total = self.check_row(self.areas[:self.player_bank])
        #adds the pebbles to the player's bank
        self.areas[self.player_bank].count += player_side_total

        #counts the pebbles left on the AI's side
        ai_side_total = self.check_row(self.areas[self.player_bank + 1 : self.computer_bank])
        #adds the AI's pebbles to their bank
        self.areas[self.computer_bank].count += ai_side_total


        #shows clearing the pebbles from the board and leaving them in the banks
        for pool in self.areas :
            #sets each of the pools to having 0 pebbles
            if pool.pool not in [self.player_bank, self.computer_bank] : pool.count = 0

        #updates the board to show where the pebbles are and the scores
        self.draw_board()




        #pulls the scores from the player and AI's banks
        player_total = self.areas[self.player_bank].count
        ai_total = self.areas[self.computer_bank].count


        #finding the winner and changing the display based on the result

        #if the player won
        if player_total > ai_total :
            if self.ai_playing : text = "AI 1 Won"
            else : text = "You Win"
            #puts the display on the user's side of the board
            y = 5 / 8 * self.BOARD_HEIGHT

        #if the AI won
        elif player_total < ai_total :
            if self.ai_playing : text = "AI 2 Won"
            else : text = "AI Won"
            #puts the display on the AI's side of the board
            y = 1 / 8 * self.BOARD_HEIGHT

        #if it's a draw
        else :
            text = "Draw"
            #puts the display in the middle of the board
            y = 3 / 8 * self.BOARD_HEIGHT



        #declaring the size of the display and centering it horizontally
        x = self.BOARD_WIDTH / 4
        display_width =  self.BOARD_WIDTH / 2
        display_height = self.BOARD_HEIGHT / 4

        #saving the IDs of the components of the display so it can be deleted
        winner_display_IDs = []

        #draws the display
        winner_display_IDs.append(self.Board.create_rectangle(x, y, x + display_width, y + display_height, fill = self.CANVAS_COL, outline = self.POOL_COL))
        winner_display_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, y, text = text, font = ("Helvetica", "80"), fill = self.POOL_COL, anchor = N))

        #raises the menu window above the box if it is open
        for Menu_Control in self.menu_control_IDs : self.Board.tag_raise(Menu_Control)

        #updates the canvas to show the display
        self.Board.update()



        #puts a delay on the play again menu showing
        self.root.after(15 * self.settings["speed"])

        if self.ai_playing :
            
            self.next_level()
            return

        #creates buttons with the option to play again, or proceed to the next level
        Play_Again = Button(self.root, text = "Play Again", width = 20, command = self.start_game, bg = self.POOL_COL, font = self.BUTTON_FONT)

        #saves buttons to list to pass to window function (including quit button)
        buttons = []
        buttons.append(Play_Again)
        if self.settings["pools"] < self.MAX_POOLS or self.settings["pebbles"] < self.MAX_POOLS / 2 + 1 : buttons.append(self.Next_Level)
        buttons.append(self.Quit_Button)

        #draws the text "would you like to play again" on the play again window
        text_ID = self.Board.create_text(self.BOARD_WIDTH / 2, self.BOARD_HEIGHT / 2 , text = "Would you like to play again?", font = ("Helvetica", "10"), fill = self.POOL_COL)

        #creates a window with the chosen buttons
        self.open_window(buttons)

        #moves the text to the top layer
        self.Board.tag_raise(text_ID)

        #adds it to the list of menu controls so it will be removed with the rest of the windows when it closes
        self.menu_control_IDs.append(text_ID)

        #updates the canvas
        self.Board.update()

        



    def next_level(self) :

        #added a sort of level system
        #at the end of a game, the player is offered a Next Level button, which calls this function

        #these are the max settings I want to use for the levels
        max_level_pools = self.MAX_POOLS
        max_level_pebbles = int(self.MAX_POOLS / 2 + 1)


        #if the number of pools is within 2 of the max number of pools
        if self.settings["pools"] >= max_level_pools - 2 :
            #number of pools is set to max
            self.settings["pools"] = max_level_pools
            #and number of pebbles is set to the halfway point plus one
            self.settings["pebbles"] = max_level_pebbles

        #otherwise, if the number of pebbles is within 1 the max for the levels
        elif self.settings["pebbles"] >= max_level_pebbles - 1 :
            #increases the number of pools by 2
            self.settings["pools"] += 2
            #sets the number of pebbles to the max for the levels
            self.settings["pebbles"] = max_level_pebbles

        #other wise, both settings increment
        else :
            #two more pools on each side
            self.settings["pools"] += 2
            #one more pebble in each pool
            self.settings["pebbles"] += 1

        #starts the game with the new settings
        self.start_game()



    #menus



    def menu(self) :

        #the menu will only open on the player's turn, after the game has ended, or if another menu is already open
        
        
        #the menu will open whenever it is clicked now
        menu_can_open = True

        if self.player_turn or self.game_over or self.menu_open or menu_can_open :

            #stops the player from clicking on pools while in the menu
            self.player_turn = False

            #saves the status of the menu
            self.menu_open = True

            #creates the buttons for the menu

            #opens the menu to change settings
            Settings = Button(self.root, text = "Settings", width = 20, font = self.BUTTON_FONT, command = self.show_settings, bg = self.POOL_COL)
            #ends the current game
            End = Button(self.root, text = "End this game", width = 20, bg = self.POOL_COL, font = self.BUTTON_FONT, command = self.game_end)
            #resets the game, keeping the current settings
            Restart = Button(self.root, text = "Reset level", width = 20, font = self.BUTTON_FONT, command = self.start_game, bg = self.POOL_COL)
            #shows the instructions of the game
            Help_Button = Button(self.root, text = "How to Play", width = 20, bg = self.POOL_COL, font = self.BUTTON_FONT, command = self.show_instructions)
            
            #button to make ai play for you
            
            AI_Play = Button(self.root, text = "Make AI play", width = 20, bg = self.POOL_COL, font = self.BUTTON_FONT, command = self.ai_fight)

            #list for passing into the window function
            buttons = []
            buttons.append(Settings)
            #only appends this button if there is a game in progress to be ended
            buttons.append(End if not self.game_over else self.Next_Level)
            buttons.append(Restart)
            buttons.append(Help_Button)
            buttons.append(AI_Play)
            buttons.append(self.Quit_Button)

            #draws the menu with these buttons
            self.open_window(buttons)

            

    def ai_fight(self) :
        self.ai_playing = not self.ai_playing
        if self.ai_playing : self.ai_turn(side=0)
        self.clear_menus()
        

    def show_instructions(self) :

        #closes currently open windows and adds a close button
        self.open_window(close_command = self.menu)

        #coordinates for window
        coords = {
            "left" : self.BOARD_WIDTH / 5,
            "top" : 5 * self.BOARD_HEIGHT / 24,
            "right" : 4 * self.BOARD_WIDTH / 5,
            #same base as the other windows, so close button will be the same distance from the bottom of this window as in the other windows
            "base" : 3 / 4 * self.BOARD_HEIGHT
        }
        #draws the rectangle
        self.menu_control_IDs.append(self.Board.create_rectangle(coords["left"], coords["top"], coords["right"], coords["base"], fill = self.CANVAS_COL, outline = self.POOL_COL))

        #puts a title at the top of the window
        Y_pos = self.BOARD_HEIGHT / 4
        self.menu_control_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, 12 * self.BOARD_HEIGHT / 48, text = "How to Play", font = ("Helvetica", "30"), fill = self.POOL_COL, anchor = N, justify = CENTER))

        #instructions of the game, copied from a website and edited
        instructions = """*When the game starts, you pick up all of the pebbles in any one of the pits on your side.
*Moving counter-clockwise, one of the pebbles is deposited in each pit until the pebbles run out.
*When passing your store, a pebble is deposited, but your opponent's store is skipped.
*If the last piece you drop is in your own store, you get an extra turn.
*If the last pebble goes in an empty pit on your side, you capture it and any pebbles in the opposite pit.
*Captured pieces go in your store (on the right).
*The game ends when all spaces on one side of the Mancala board are empty.
*When the game ends, the player who still has pieces on their side captures all of those pieces.
*The winner is the player with the most pieces in their store at the end of the game."""

        #displays these instructions in the box
        Y_pos = 35 * self.BOARD_HEIGHT / 96
        self.menu_control_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, Y_pos, text = instructions, font = ("Helvetica", "10"), fill = self.POOL_COL, anchor = N, justify = CENTER))



    def open_window(self, buttons = [], close_command = None) :

        #the instructions window has a close button that takes you back to the main menu instead of closing the menu
        #I did this by making the close button have a default command of closing the main menu
        #but the function will accept another command for the close button
        if close_command == None :
            #I could not reference a command that was part of the object in the parameters of this function, as it is also part of the object
            #my solution was to set close_command to None by default, and then change it if a value wasn't submitted
            close_command = self.close_menu

        #makes the close button with the chosen command
        Close = Button(self.root, text = "Close", width = 20, font = self.BUTTON_FONT, command = close_command, bg = self.POOL_COL)

        #the height for all the buttons
        button_height = 25

        #defining the width and location of the close button
        button_width = self.BOARD_WIDTH / 15
        x = self.BOARD_WIDTH / 2
        y = 5 * self.BOARD_HEIGHT / 8 + button_height

        #closes open menus to replace with this menu
        self.clear_menus()

        #puts the close button on the canvas
        self.menu_control_IDs.append(self.Board.create_window(x, y, window = Close, height = button_height, width = button_width, anchor = N))

        #if any buttons were passed into the function, it draws a window with the buttons
        #if no buttons are passed into the function, no window is drawn, as the only window that doesn't
        #pass any buttons is the Instructions screen, which draws it's own, bigger screen, and only needs a close button
        if len(buttons) > 0 :

            #draws the window
            coords = {
                "left" : self.BOARD_WIDTH / 4,
                "top" : self.BOARD_HEIGHT / 4,
                "right" : 3 * self.BOARD_WIDTH / 4,
                "base" : 3 * self.BOARD_HEIGHT / 4
            }
            self.menu_control_IDs.append(self.Board.create_rectangle(coords["left"], coords["top"], coords["right"], coords["base"], fill = self.CANVAS_COL, outline = self.POOL_COL))

            #adds the title "MANCALA"
            self.menu_control_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, 3 * self.BOARD_HEIGHT / 8, text = "MANCALA", font = ("Helvetica", "32"), fill = self.POOL_COL))

            #decides the width of the buttons from how many buttons there are
            button_width = self.BOARD_WIDTH / 3 / len(buttons)

            #location of the first button
            x = self.BOARD_WIDTH / 3
            y = 5 * self.BOARD_HEIGHT / 8

            #for each button to draw
            for button in buttons :
                #add the button to the canvas
                self.menu_control_IDs.append(self.Board.create_window(x, y, window = button, height = button_height, width = button_width, anchor = SW))
                #shift the x coordinate for the next button
                x += button_width

        #updates the board with the window on it, in case there is another function running when the menu is opened
        self.Board.update()



    def close_menu(self) :

        #if the game has not ended, then this resumes the player's turn
        if not self.game_over : self.player_turn = True

        #closes the open menus
        self.clear_menus()
        self.menu_open = False



    def clear_menus(self) :

        #removes existing controls from the screen
        for control in self.menu_control_IDs : self.Board.delete(control)
        #clears the list, as the controls have been deleted
        self.menu_control_IDs = []



    def open_menu(self) :

        #if the menu is already open, this function will instead close the menu when the player clicks the menu button
        if self.menu_open : self.close_menu()
        #otherwise, opens the menu
        else : self.menu()



    def show_settings(self) :

        #creating partial functions to call the change setting function with a setting to change
        #partials allow you to save a function with a parameter as a new function with no parameters
        #this is so I can pass parameters into functions I am calling with buttons, which do not accept parameters
        change_play_speed = partial(self.change_setting, "speed")
        change_pool_num = partial(self.change_setting, "pools")
        change_pebble_num = partial(self.change_setting, "pebbles")


        #buttons to display

        #for changing the length of the delays in the game
        Play_Speed = Button(self.root, text = "Animation Speed", width = 20, font = self.BUTTON_FONT, command = change_play_speed, bg = self.POOL_COL)
        #for changing the number of pools on each side of the board
        Num_Pools = Button(self.root, text = "Number of Pits", width = 20, font = self.BUTTON_FONT, command = change_pool_num, bg = self.POOL_COL)
        #for changing the number of pebbles in each pool
        Num_Pebbles = Button(self.root, text = "Number of Pebbles", width = 20, font = self.BUTTON_FONT, command = change_pebble_num, bg = self.POOL_COL)
        #takes the user back to the main menu
        Back_Button = Button(self.root, text = "Back", width = 20, font = self.BUTTON_FONT, command = self.menu, bg = self.POOL_COL)

        #list to send to window function
        buttons = []
        buttons.append(Play_Speed)
        buttons.append(Num_Pools)
        buttons.append(Num_Pebbles)
        buttons.append(Back_Button)

        #opens window
        self.open_window(buttons)

        #draws a subtitle "what setting would you like to change?"
        self.menu_control_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, self.BOARD_HEIGHT / 2 , text = "What settings would you like to change?", font = ("Helvetica", "10"), fill = self.POOL_COL))



    def change_setting(self, setting) :

        #makes the text box empty when it opens for the user
        self.Text_Entry.delete(0, 'end')

        #determines the message to be displayed in the option change window
        if setting == "speed" : message = "How long do you want the animations to be? (5 is default)"
        elif setting == "pools" : message = "How may pits do you want to play with? (6 traditionally)"
        elif setting == "pebbles" : message = "How may pebbles do you want in each pit? (4 traditionally)"

        #creates partial function for the submit button
        #this will activate the submit setting function and pass it the setting being changed
        setting_changer = partial(self.submit_setting, setting)

        #creates the buttons for the window
        Submit = Button(self.root, text = "Submit", width = 20, font = self.BUTTON_FONT, command = setting_changer, bg = self.POOL_COL)
        Back_Button = Button(self.root, text = "Back", width = 20, font = self.BUTTON_FONT, command = self.show_settings, bg = self.POOL_COL)

        #putting the buttons in a list to be passed into the window  maker
        buttons = []
        buttons.append(self.Text_Entry)
        buttons.append(Submit)
        buttons.append(Back_Button)

        #creates a window with the buttons
        self.open_window(buttons)

        #displays the text in the window
        self.menu_control_IDs.append(self.Board.create_text(self.BOARD_WIDTH / 2, self.BOARD_HEIGHT / 2 , text = message, font = ("Helvetica", "10"), fill = self.POOL_COL))


    #this function is for submitting the value the user entered. If the entry was valid, it changes the setting
    def submit_setting(self, setting) :

        #makes sure the input is the correct format
        #gets min and max inputs for the setting being changed
        try :

            #can be a decimal number for speed
            if setting == "speed" :
                entry = float(self.Text_Entry.get())
                min_input = self.MIN_SPEED
                max_input = self.MAX_SPEED

            #must be a whole number if changing pools or pebbles
            elif setting == "pools" :
                entry = int(self.Text_Entry.get())
                min_input = self.MIN_POOLS
                max_input = self.MAX_POOLS

            elif setting == "pebbles" :
                entry = int(self.Text_Entry.get())
                min_input = self.MIN_PEBBLES
                max_input = self.MAX_PEBBLES

        #if the user's input wasn't a number
        except :
            #tells user their input was not the correct format
            messagebox.showinfo("Input Error", "Please enter a whole number")
            #clears text box
            self.Text_Entry.delete(0, 'end')
            #exits the function
            return

        #this section will only run if the code in the try section passed correctly
        #makes sure the input is within the determined range
        if entry < min_input or entry > max_input :

            #displays an info window telling the user that their input was out of range
            messagebox.showinfo("Input Error", ("That input is out of range\n" +
                         "Please enter a number between " + str(min_input) + " and " + str(max_input)))
            #clears the text box
            self.Text_Entry.delete(0, 'end')

        else:

            #changes the setting
            if setting == "speed" : self.settings[setting] = int(floor(entry * 20))
            elif setting in ["pools", "pebbles"] : self.settings[setting] = int(entry)
            self.start_game()



    def quit(self, root = None) :

        #closes a specified window, if no window is specified, it will default to closing the main window
        self.root.destroy() if root == None else root.destroy()




#creates the tkinter window
root = Tk()

#creates a MancalaGame object connected to the new window
Mancala = MancalaGame(root)

#loops the tkinter window
Mancala.root.mainloop()
