from turtle import *
import random
import math
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# Setup
screen = Screen()
screen.setup(800, 600)  # Set explicit screen size
screen_width, screen_height = 800, 600
boundary_x = screen_width // 2 - 20  # Leave some margin
boundary_y = screen_height // 2 - 20
bgcolor('black')
tracer(0, 0)

# Data for plotting
time_points = deque(maxlen=500)  # Store last 500 time points
pathogen_counts = deque(maxlen=500)
agent_counts = deque(maxlen=500)
cytokine_counts = deque(maxlen=500)

# Setup the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(10, 6))
pathogen_line, = ax.plot([], [], 'g-', label='Pathogens')
agent_line, = ax.plot([], [], 'r-', label='immune cells')
cytokine_line, = ax.plot([], [], 'b-', label='Cytokines')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Count')
ax.set_title('Immune System Simulation')
ax.legend()
ax.grid(True)
ax.set_facecolor('#E0E0E0')


# Constants
max_stride = 10
agent_speed = 10
spawn_distance = 100
pathogen_replication_chance = 0.0060
kill_interval = 30
killer_mutation_chance = 0.0
agent_detection_radius = 30
cytokine_decay_rate = 0.999
cytokine_count = 0
cytokine_response_cooldown = 4
max_cytokines = 50  # Limit total cytokines to prevent overload
max_agents = 100
step_size = 10
start_pathogen_amount = 10
cytokine_recruitment_threshold = 3

# Lifespan tracking
agent_metadata = {}
cytokine_metadata = {}

# Entities
pathogens = []
agents = []
cytokines = []

# Circle drawer for debug visuals
circle_drawer = Turtle()
circle_drawer.hideturtle()
circle_drawer.penup()
circle_drawer.speed(0)
circle_drawer.color('blue')

# Utility
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def save_plot(elapsed_time):
    # Create a timestamp for unique filenames
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    # Create a new figure for saving (to avoid interference with the live plot)
    save_fig, save_ax = plt.subplots(figsize=(10, 6))
    
    # Specify the directory where you want to save the plots
    save_directory = "~/Documents/Python code/simulation_results/sim6"  # Change this to your desired directory
    
    # Create the directory if it doesn't exist
    import os
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    # Create a new figure for saving
    save_fig, save_ax = plt.subplots(figsize=(10, 6))
    
    # Plot the data
    save_ax.plot(time_points, pathogen_counts, 'g-', label='Pathogens')
    save_ax.plot(time_points, agent_counts, 'r-', label='Immune Cells')
    save_ax.plot(time_points, cytokine_counts, 'b-', label='Cytokines')
    
    # Add labels and title
    save_ax.set_xlabel('Time (s)')
    save_ax.set_ylabel('Count')
    save_ax.set_title(f'Immune System Simulation - Duration: {elapsed_time:.1f}s')
    save_ax.legend()
    save_ax.grid(True)
    
    # Save the figure
    filename = f"immune_simulation_{timestamp}.png"
    save_fig.savefig(filename)
    plt.close(save_fig)  # Close the figure to free memory
    
    print(f"Plot saved as {filename}")

def keep_in_bounds(entity):
    """Keep an entity within screen boundaries"""
    x, y = entity.xcor(), entity.ycor()
    
    if x > boundary_x:
        entity.setx(boundary_x)
        entity.setheading(random.randint(100, 260))  # Turn left
    elif x < -boundary_x:
        entity.setx(-boundary_x)
        entity.setheading(random.randint(-80, 80))  # Turn right
        
    if y > boundary_y:
        entity.sety(boundary_y)
        entity.setheading(random.randint(190, 350))  # Turn down
    elif y < -boundary_y:
        entity.sety(-boundary_y)
        entity.setheading(random.randint(10, 170))  # Turn up

# Pathogen class
class Pathogen(Turtle):
    def __init__(self, x=0, y=0, killer=False):
        super().__init__()
        self.color('blue' if killer else 'green')
        self.shape('circle')
        self.shapesize(0.5)
        self.speed(0)
        self.penup()
        self.goto(x, y)
        self.killer = killer

# Agent class
class Agent(Turtle):
    def __init__(self, x=0, y=0):
        super().__init__()
        self.color('red')
        self.shape('circle')
        self.shapesize(0.5)
        self.speed()
        self.penup()
        self.goto(x, y)
        self.detection_radius = agent_detection_radius
        self.last_cytokine_response = 0
        self.cytokine_cooldown = True  # Prevent immediate cytokine response

# Cytokines class
class Cytokine(Turtle):
    def __init__(self, x=0, y=0):
        super().__init__()
        self.color('white')
        self.shape('circle')
        self.scale = 0.5
        self.shapesize(self.scale)
        self.speed(0)
        self.penup()
        self.goto(x, y)
        self.birth_pos = (x,y)

# Create entities
def create_pathogen(x=0, y=0, killer=None):
    if killer is None:
        killer = (random.random() < killer_mutation_chance)
    p = Pathogen(x, y, killer)
    pathogens.append(p)
    return p

def create_agent(x=0, y=0):
    # Limit the number of agents
    if len(agents) >= max_agents:
        return None
        
    a = Agent(x, y)
    agents.append(a)
    agent_metadata[a] = time.time() + random.uniform(20, 40)
    return a

def create_cytokine(x, y):
    global cytokine_count
    
    # Limit the number of cytokines
    if cytokine_count >= max_cytokines:
        return None
        
    c = Cytokine(x, y)
    cytokines.append(c)
    cytokine_metadata[c] = time.time() + random.uniform(10, 20) 
    cytokine_count += 1
    return c

def patrol(agent, target_pos):
    agent.setheading(agent.towards(target_pos))
    agent.forward(agent_speed)
    keep_in_bounds(agent)

def random_patrol(agent):
    if random.random() < 0.1:
        agent.left(random.randint(-45, 45))
    agent.forward(2)
    keep_in_bounds(agent)

def spawn_single_agent(x, y):
    """Spawn a single agent at the given position"""
    if len(agents) < max_agents:
        create_agent(x, y)

def cytokine_move():
    for cytokine in list(cytokines):
        cytokine.goto(
            cytokine.xcor() + random.uniform(-step_size, step_size),
            cytokine.ycor() + random.uniform(-step_size, step_size)
            )
        keep_in_bounds(cytokine)

def update_plot(elapsed_time):
    time_points.append(elapsed_time)
    pathogen_counts.append(len(pathogens))
    agent_counts.append(len(agents))
    cytokine_counts.append(cytokine_count)
    
    # Update the plot data
    pathogen_line.set_data(time_points, pathogen_counts)
    agent_line.set_data(time_points, agent_counts)
    cytokine_line.set_data(time_points, cytokine_counts)
    
    # Adjust the plot limits
    ax.set_xlim(0 if not time_points else min(time_points), 
                max(time_points) + 5 if time_points else 10)
    ax.set_ylim(0, max(max(pathogen_counts, default=10), 
                        max(agent_counts, default=10), 
                        max(cytokine_counts, default=10)) + 5)
    
    # Draw the plot
    fig.canvas.draw_idle()
    fig.canvas.flush_events()


# Initialization
def initialize():
    global pathogens, agents, agent_metadata, cytokines, cytokine_metadata, last_clone_time, last_kill_time, last_cytokine, cytokine_count
    for p in pathogens: p.hideturtle()
    for a in agents: a.hideturtle()
    for c in cytokines: c.hideturtle()
    pathogens.clear()
    agents.clear()
    agent_metadata.clear()
    cytokines.clear()
    cytokine_metadata.clear()
    cytokine_count = 0
    
    # Clear plot data
    time_points.clear()
    pathogen_counts.clear()
    agent_counts.clear()
    cytokine_counts.clear()

    
    # Create initial pathogens in random positions
    for _ in range(start_pathogen_amount):
        x = random.randint(-boundary_x, boundary_x)
        y = random.randint(-boundary_y, boundary_y)
        create_pathogen(x, y)
    
    # Create initial agents in strategic positions
    for pos in [(100, 100), (-100, 100), (-100, -100), (100, -100)]:
        create_agent(*pos)
        
    last_clone_time = time.time()
    last_kill_time = time.time()
    last_cytokine = time.time()
    return last_clone_time, last_kill_time, last_cytokine

# Clone an existing pathogen
def clone_pathogen(p):
    x_offset = random.uniform(-20, 20)
    y_offset = random.uniform(-20, 20)
    x, y = p.xcor() + x_offset, p.ycor() + y_offset
    create_pathogen(x, y, killer=p.killer)

# Main simulation loop
def simulation():
    global last_clone_time, last_kill_time, last_cytokine, cytokine_count
    last_clone_time, last_kill_time, last_cytokine = initialize()
    start_time = time.time()
    last_plot_update = start_time
    plot_update_interval = 0.5  # Update plot every 0.5 seconds
    

    while True:
        now = time.time()
        elapsed_time = now - start_time
        
        
        
        # Update plot at regular intervals
        if now - last_plot_update >= plot_update_interval:
            update_plot(elapsed_time)
            last_plot_update = now
        
        # Restart if no pathogens
        if not pathogens or len(pathogens) > 500:
            print("All pathogens eliminated. Restarting simulation...")
            save_plot(elapsed_time)
            last_clone_time, last_kill_time, last_cytokine = initialize()
            start_time = time.time()

        # Update pathogens
        for p in list(pathogens):
            if p.killer:
                targets = [a for a in agents if distance(p.pos(), a.pos()) < 30]
                if targets:
                    t = targets[0]
                    t.hideturtle()
                    agents.remove(t)
                    agent_metadata.pop(t, None)
                    p.setheading(p.towards(t.pos()))
                    p.forward(max_stride)
                    continue
            p.forward(random.randint(0, max_stride))
            p.left(random.randint(-90, 90))
            keep_in_bounds(p)
            
        # Clone pathogens
        for pathogen in pathogens:
            if random.random() < pathogen_replication_chance:
                clone_pathogen(pathogen)
                
        # Kill random pathogen
        if now - last_kill_time > kill_interval and len(pathogens) > 1:
            victim = random.choice(pathogens)
            victim.hideturtle()
            pathogens.remove(victim)
            last_kill_time = now
            
        # Gradually decay cytokines visually
        for c in list(cytokines):
            c.scale *= cytokine_decay_rate
            c.shapesize(c.scale)
            if c.scale < 0.05:
                cytokine_count -= 1
                c.hideturtle()
                cytokines.remove(c)
                cytokine_metadata.pop(c, None)
                
        # Remove expired cytokines
        for c in list(cytokines):
            if c in cytokine_metadata and cytokine_metadata[c] < now:
                cytokine_count -= 1
                c.hideturtle()
                cytokines.remove(c)
                cytokine_metadata.pop(c, None)
                
        # Agent behavior
        for agent in list(agents):
            # Check if agent should die of old age
            if agent not in agent_metadata or agent_metadata[agent] < now and now - agent.last_cytokine_response > 30:
                agent.hideturtle()
                agents.remove(agent)
                agent_metadata.pop(agent, None)
                continue
                
            # Find nearby pathogens and cytokines
            visible_pathogens = [
                p for p in pathogens
                if distance(agent.pos(), p.pos()) < agent.detection_radius
            ]
            visible_pathogens.sort(key=lambda p: (not p.killer, distance(agent.pos(), p.pos())))
            
            visible_cytokines = [
                c for c in cytokines
                if distance(agent.pos(), c.pos()) < agent.detection_radius
            ]
            
                
            # Priority 1: Chase and destroy pathogens
            if visible_pathogens:
                target = visible_pathogens[0]
                patrol(agent, target.pos())
                if distance(agent.pos(), target.pos()) < 15:
                    target.hideturtle()
                    pathogens.remove(target)
                    # Create a cytokine when pathogen is destroyed
                    create_cytokine(agent.xcor(), agent.ycor())
                    agent.last_cytokine_response = now
            
            # Priority 2: Respond to cytokines if not recently responded
            elif visible_cytokines and (now - agent.last_cytokine_response > cytokine_response_cooldown):
                target = visible_cytokines[0]
                patrol(agent, target.birth_pos)
                
                # When agent reaches cytokine
                if distance(agent.pos(), target.birth_pos) < 15:
                    # Create a new immune cell
                    offset_x = random.uniform(-30, 30)
                    offset_y = random.uniform(-30, 30)
                    spawn_single_agent(agent.xcor() + offset_x, agent.ycor() + offset_y)

                    # Create a new cytokine (but not too many)
                    if random.random() < 0.3 and cytokine_count < max_cytokines // 2:
                        create_cytokine(agent.xcor(), agent.ycor())
                        
                    # Remove the cytokine that was responded to
                    target.hideturtle()
                    cytokines.remove(target)
                    cytokine_count -= 1
                    cytokine_metadata.pop(target, None)
                    
                    # Update agent's response time
                    agent.last_cytokine_response = now
            
            # Priority 3: Random patrol if nothing to do
            else:
                random_patrol(agent)
                
        # Optional: draw detection radius (comment out if you don't want it)
        circle_drawer.clear()
        for agent in agents:
            circle_drawer.penup()
            circle_drawer.goto(agent.xcor(), agent.ycor() - agent.detection_radius)
            circle_drawer.pendown()
            circle_drawer.circle(agent.detection_radius)
            circle_drawer.penup()
            
        update()
        cytokine_move()
        
        # Less frequent status updates to reduce console spam
        if int(now) % 5 == 0:
            print(f"Cytokines: {cytokine_count}, Agents: {len(agents)}, Pathogens: {len(pathogens)}")
            
        time.sleep(0.05)

# Run the simulation
simulation()
