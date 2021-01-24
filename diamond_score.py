import random
import time
import threading
from base import BaseAgent, TurnData, Action



class Diamond  :
    GREEN = 0
    BLUE = 1
    RED = 2
    YELLOW = 3
    GRAY = 4


class Agent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.path = []
        self.threads = []
        self.last_Action = None
        self.mode_start_position = None
        self.base_positions = None
        print(f"MY NAME: {self.name}")
        print(f"PLAYER COUNT: {self.agent_count}")
        print(f"GRID SIZE: {self.grid_size}")
        print(f"MAX TURNS: {self.max_turns}")
        print(f"DECISION TIME LIMIT: {self.decision_time_limit}")


    def find_all_bases(self, agent, map):
        base_positions = [(i,j) for i in range(len(map)) for j in range(len(map[i])) if map[i][j] == agent.name.lower()]
        return base_positions
        # self.base_positions = base_positions

    def manhatan_dist(self, x1, y1, x2,y2) :
        return abs(x1 - x2) + abs(y1- y2)

    def manhatan_dist_to_closest_base(self, x, y, base_positions) :
        return min( [ self.manhatan_dist(x,y,base[0],base[1]) for base in base_positions ] )

    def number_of_close_points_in_zone(self, x, y, zone , distance=3 ) :
        return len(list(map(lambda manhatan_distance : manhatan_distance <= distance ,[self.manhatan_dist(x,y,point[0], point[1]) for point in zone] )))


    def ygy_constraint(self, agent, color) :
        return color == Diamond.YELLOW and agent.collected[-2] == Diamond.YELLOW and agent.collected[-1] == Diamond.GREEN

    def calculate_diamonds_score(self, agent, turn_data) :
        """
        return a list of tuples in (x, y, score, color)
        each tuple crossponds to a specific diamond
        """
        output = [[i,j, 0, eval(turn_data.map[i][j])] for i in range(len(turn_data.map)) for j in range(len(turn_data.map[i])) if turn_data.map[i][j].isdigit()]

        for diamond in output :
            diamond[2] += (agent.collected.count(diamond[3]) * 2)  # number of picked diamonds with color d    
            diamond[2] += ( agent.count_required[diamond[3]] * -1) # ad
            diamond[2] += ( ( agent.count_required[diamond[3]] - agent.collected.count(diamond[3])) *2) # ad - number of picked diamonds with color d   
            base_positions = self.find_all_bases(agent, turn_data.map)
            diamond[2] += (self.manhatan_dist_to_closest_base(diamond[0], diamond[1], base_positions ) * -1) # manhatan distance to closest base  
            diamond[2] += (self.number_of_close_points_in_zone( diamond[0], diamond[1], [(point[0],point[1]) for point in output], 3)*2)
            not_carrying_agents_positions = [other_agent.position for other_agent in turn_data.agent_data if not other_agent.carrying and agent.name != other_agent.name] 
            diamond[2] += (self.number_of_close_points_in_zone(diamond[0], diamond[1], not_carrying_agents_positions ,3)* -20) 
            diamond[2] += 3 if self.ygy_constraint(agent, diamond[3]) else 0
            if diamond[2] < 0 :
                diamond[2] = 0 

        return output

    def cell_score(self, agent, turn_data, x, y) :
        diamond_scores = self.calculate_diamonds_score(agent=agent, turn_data=turn_data)
        sum = 0 
        for score in diamond_scores :
            sum += score[2] / self.manhatan_dist(x, y, score[0], score[1])
        
        return sum 

    def print_map (self, map) :
        for row in map :
            print(row)
        print('')


    def do_turn(self, turn_data: TurnData) -> Action:
        for agent in turn_data.agent_data:
            if agent.name == self.name:
                me = agent
                if not self.base_positions :
                    self.base_positions = self.find_all_bases(me, turn_data.map)
                

        # self.print_map(turn_data.map)
        # print(turn_data)
        print(self.__dict__)
        try :
            print(self.cell_score(me, turn_data, me.position[0] , me.position[1]+1))
        except Exception as exc :
            print('\n\nERROR\n\n')
        return random.choice([Action.UP,Action.DOWN,Action.LEFT,Action.RIGHT,])

if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)

