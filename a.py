import math 

def get_agent_available_movements(agent):
    return [1,2]

def sajjad(game_state):
    """ -> [1,2,3,4]"""
    i = 0
    while True:
        yield [i, i+1, i+2, i+3]
        i += 1
gen = sajjad(1)


def calculate_state(game_state, agent, movement):
    """
    game state : یه چیزی مثل turn data
    agent : یه دونه از عامل ها
    movement: حرکتی که انجام میده مثل right یا left

    returns:
        یه state برمیگردونه. یه جیزی مثل turn data
    """
    pass


def minimax(game_state, depth, agents, agent_index ):
    # our agent index should be given as agent_index in first function call

    if depth == 0:
        # return next(gen)
        return sajjad(game_state)
    
    max_values = [-10 for i in range(len(agents))]
    for movement in get_agent_available_movements(agents[agent_index]):
        new_state = calculate_state(game_state, agents[agent_index], movement)
        values = minimax(new_state, depth-1, agents, (agent_index+1)%len(agents))
        
        print (values)
        if max_values[agent_index] < values[agent_index]:
            max_values = values
    return max_values

print('lastttttt', minimax(1, 4, [1,2,3], 0))