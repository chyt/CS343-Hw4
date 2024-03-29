import Tkinter as tk
import sys
import string
import Queue

# tower of hanoi 3 pole 3 disk successful semantic solution:
# move disk1 from pole1 to pole3 and move disk2 to pole2 from pole1 and pick up disk1 from right pole and put it down on middle pole and pick up disk3 from pole1 and put it down on right pole and move disk1 from pole2 to left pole and move disk2 to right pole from middle pole and pick up disk1 from left pole and put it down on pole3

class MyDialog:
    def __init__(self, parent):

        top = self.top = parent #tk.Toplevel(parent)

        self.entry_frame = tk.Frame(parent)
        tk.Label(self.entry_frame, text="Please enter English sentence:").pack()
        tk.Label(top, text="Example: move disk1 from pole1 to pole2").pack()
        tk.Label(top, text="Example: pick up disk1 from pole1").pack()
        tk.Label(top, text="Example: put down disk1 on pole2").pack()

        self.e = tk.Entry(self.entry_frame, width=100)
        self.e.pack(padx=15)

        self.entry_frame.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.log_frame = tk.Frame(parent)
        self.text = tk.Text(self.log_frame)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll = tk.Scrollbar(self.log_frame)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(font="Courier 12", yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)

        self.log_frame.pack(side=tk.BOTTOM)
        
        self.fBottom = tk.Frame(top)

        c = tk.Button(self.fBottom, text="Close", command=self.close)
        c.pack(side = tk.RIGHT)

        b = tk.Button(self.fBottom, text="Execute", command=self.ok)
        b.pack(side = tk.RIGHT)
        self.value = ""

        c = tk.Button(self.fBottom, text="Parse", command=self.parse)
        c.pack(side = tk.RIGHT)

        self.fBottom.pack(side=tk.BOTTOM)

        #setup other stuff
        self.log_frame.bind('<<display-text>>', self.display_text_handler)
        
        self.message = Queue.Queue()

        self.parsed_plan = ""

        self.it = ""

    def parse(self):
        if self.parsed_plan == "":
            self.value = self.e.get()
            #parse the plan
            self.parsed_plan = self.semantic_parser(self.value)
            self.log_info("{0} -> {1}".format(self.value, self.parsed_plan))
        else:
            self.log_error("Already parsed plan: {0}, cannot parse new plan.".format(self.parsed_plan))
        
    def semantic_parser(self, plan):
        #Write code for simple semantic grammar here
        #Actions should be returned in the following format:
            #1. Mov Object Source Destination
            #2. Pick Object Source
            #3. Put Object Destination
        #But first, if for some reason the plan string is empty just exit
        if (len(plan) == 0):
            return plan

        plan = string.lower(plan)
        result = [] # Create an empty array to store the results, as there may be several of them

        # Split up each individual command, separated by the word "and"
        commands = string.split(plan, 'and')

        for command in commands:
            self.log_info("Parsing command: " + command)
            words = string.split(command) # A list of the words in the user command

            #The verb phrase should come first, so look at the first word
            #If the verb phase is present go ahead and parse the noun phrases
            self.log_info("Identifying initial verb...")
            if words[0] == "mov" or words[0] == "move":
                self.log_info("Case VP1 NP1 NP3 NP4 (\"Move\") found")
                self.log_info("Identifying noun phrases...")
                result.append("Mov " + self.get_noun_phrases(command))
            elif words[0] == "pick":
                self.log_info("Case VP2 NP1 NP3 (\"Pick Up\") found.")
                self.log_info("Identifying noun phrases...")
                result.append("Pick " + self.get_noun_phrases(command))
            elif words[0] == "put":
                self.log_info("Case VP3 NP1 NP4 (\"Put\") found.")
                self.log_info("Identifying noun phrases...")
                result.append("Put " + self.get_noun_phrases(command))
            else:
                self.log_error(words, "Instructions must begin with Move, Pick or Put.")

        if len(result) > 0:
            return result
        return plan
    
    def get_noun_phrases(self, plan):
        """
        Helper method. Given a string representing a plan,
        finds the noun phrases by removing every word other than "disk*" or "pole*.
		Does not check whether these are in the correct order."
        """
        words = string.split(plan)

	subject = ""
	from_noun = ""
	to_noun = ""

	position_prefix = ""

        #asssume that the noun phrases are in a fixed order
        #then just look for the keywords "disk" and "pole", ignoring everything else
        for i in range(0,len(words)):
	    w = words[i]
            if w == "it":
                if self.it == "":
		    # during the first iteration, self.it is still an empty string
                    self.log_error("No reference for \"it\"")
		    return
                else:
                    w = self.it

            if "disk" in w:
                self.log_info("disk \"{0}\" found!".format(w))
		subject = w.title()
                self.it = w

	    elif w == "from":
		position_prefix = "from"
	    elif w == "to" or w == "on":
		position_prefix = "to"
		
            elif "pole" in w:
		if w == "pole":
		    previous_word = words[i-1]
		    if previous_word == "left":
			w = "Pole1"
		    elif previous_word == "middle":
			w = "Pole2"
		    elif previous_word == "right":
			w = "Pole3"
		    else:
			# previous word not recognized
                        self.log_error("Adjective \"{0}\" not recognized".format(previous_word))
		        return
                self.log_info("pole \"{0}\" found!".format(w))
		if position_prefix == "from":
		    from_noun = w.title()
		elif position_prefix == "to":
		    to_noun = w.title()
		else:
                    # from/to prefix was not assigned
		    self.log_error("From/to prefix was not assigned")
		position_prefix = ""

        return subject + " " + from_noun + " " + to_noun

    def ok(self):
        if self.parsed_plan == "":
            self.parse()

        if (type(self.parsed_plan) == list):
    	    for command_string in self.parsed_plan:
    	        print command_string
    	else:
    	    print self.parsed_plan
    	self.top.destroy()

    def close(self):
    	self.value = "close"
    	print self.value
    	self.top.destroy()
        
    def log_info(self, printable_object, message=""):
        s = "[INFO]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')    
    
    def log_error(self, printable_object, message=""):
        s =  "[ERROR]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')        

    def display_text_handler(self, event=None):
        s = self.message.get()
        self.text.insert(tk.END, s)
        self.text.insert(tk.END, '\n')
        self.text.yview(tk.END)

def main():
    root = tk.Tk()
    root.title('Enter Command')
    d = MyDialog(root)
    root.wait_window(d.top)
   

if __name__ == "__main__":
        main()
