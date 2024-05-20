from tkinter import Tk, Label, Radiobutton, StringVar, Button
from pyg_hexagrid import HexagonGrid

  
root = Tk() 
root.title("HexRL Main Menu")
# root.geometry("300x800")


# board size selection: row 0 to 4
s = Label(root, text="Board size", font=(None, 11))
s.grid(row=0, column=0, columnspan=2, pady=5)

board_size_str_var = StringVar(root, "11")
board_size_values = [
    ("5 \u00D7 5", "5"),
    ("7 \u00D7 7", "7"),
    ("9 \u00D7 9", "9"),
    ("11 \u00D7 11", "11"),
    ("13 \u00D7 13", "13"),
    ("15 \u00D7 15", "15"),
    ("17 \u00D7 17", "17"),
    ("19 \u00D7 19", "19"),
]

for i, (text, mode) in enumerate(board_size_values[:4]):
    Radiobutton(root, text=text, variable=board_size_str_var, value=mode
                ).grid(row=i+1, column=0, sticky='w')
for i, (text, mode) in enumerate(board_size_values[4:]):
    Radiobutton(root, text=text, variable=board_size_str_var, value=mode
                ).grid(row=i+1, column=1, sticky='w')

# mode selection: row 5 to 9
m = Label(root, text="Mode", font=(None, 11))
m.grid(row=5, column=0, columnspan=2, pady=5)

mode_str_var = StringVar(root, "pvp")
mode_values = [
    ("Player vs. Player", "pvp"),
    ("Player vs. Agent", "pva"),
    ("Agent vs. Player", "avp"),
    ("Agent vs. Agent", "ava")
]

def update_all_agent_options():
    selected_mode = mode_str_var.get()
    state_1 = 'normal' if selected_mode[0] == 'a' else 'disabled'
    state_2 = 'normal' if selected_mode[2] == 'a' else 'disabled'
    for agent_radio_button in agent_radio_buttons_1:
        agent_radio_button.config(state=state_1)
    for agent_radio_button in agent_radio_buttons_2:
        agent_radio_button.config(state=state_2)

for i, (text, mode) in enumerate(mode_values):
    Radiobutton(root, text=text, variable=mode_str_var, value=mode, command=update_all_agent_options
                ).grid(row=i+6, column=0, columnspan=2, sticky='w'
    )

# bot selection: row 10 to 20 (assume 10 agents)
b = Label(root, text="Agent", font=(None, 11))
b.grid(row=10, column=0, columnspan=2, pady=5)

agent_str_var_1 = StringVar(root, "random")
agent_str_var_2 = StringVar(root, "random")
values = [
    ("Random", "random"),
    ("Q-Learning", "qlearning"),
    ("Agent 3", "agent3"),
    ("Agent 4", "agent4"),
    ("Agent 5", "agent5"),
    ("Agent 6", "agent6"),
    ("Agent 7", "agent7"),
    ("Agent 8", "agent8"),
    ("Agent 9", "agent9"),
    ("Agent 10", "agent10"),
]

agent_radio_buttons_1 = []
for i, (text, mode) in enumerate(values):
    agent_radio_button = Radiobutton(root, text=text, variable=agent_str_var_1, value=mode, state='disabled')
    agent_radio_button.grid(row=i+11, column=0, sticky='w')
    agent_radio_buttons_1.append(agent_radio_button)

agent_radio_buttons_2 = []
for i, (text, mode) in enumerate(values):
    agent_radio_button = Radiobutton(root, text=text, variable=agent_str_var_2, value=mode, state='disabled')
    agent_radio_button.grid(row=i+11, column=1, sticky='w')
    agent_radio_buttons_2.append(agent_radio_button)



# play button
def play():
    size = int(board_size_str_var.get())
    mode = mode_str_var.get()
    agent = agent_str_var_1.get()

    print(board_size_str_var.get(), mode_str_var.get(), agent_str_var_1.get())
    
    root.destroy()

    HexagonGrid(size=size, mode=mode, agent=agent).main()
    

play_button = Button(root, text="Play", command=play)
play_button.grid(row=21, column=0, columnspan=2, pady=10)

root.mainloop()