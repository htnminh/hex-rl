from tkinter import Tk, Label, Radiobutton, StringVar
  
root = Tk() 

root.title("HexRL Main Menu")
root.geometry("300x200")

a = Label(root, text="Settings", font=(None, 14)) 
a.pack() 
  
v = StringVar(root, "1")
values = [
    ("Random", "1"),
    ("Q-Learning", "2"),
    ("DQN", "3"),
    ("DQN with Prioritized Experience Replay", "4"),
]

for text, mode in values:
    Radiobutton(root, text=text, variable=v, value=mode).pack(anchor='w')


root.mainloop()