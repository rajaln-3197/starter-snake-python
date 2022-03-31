import random
from typing import List, Dict
from scipy import spatial 
from sklearn.neighbors import NearestNeighbors
"""
This file can be a nice home for your Battlesnake's logic and helper functions.

We have started this for you, and included some logic to remove your Battlesnake's 'neck'
from the list of possible moves!
"""

def get_info() -> dict:
    """
    This controls your Battlesnake appearance and author permissions.
    For customization options, see https://docs.battlesnake.com/references/personalization

    TIP: If you open your Battlesnake URL in browser you should see this data.
    """

  # Made my battlesnake to be Lilac - my favourite color
    return {
        "apiversion": "1",
        "author": "rajaln-3197",
        "color": "#C89DD8",
        "head": "default",
        "tail": "default", 
    }


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_snake = data["you"]      # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates like {"x": 0, "y": 0}
    my_body = my_snake["body"]  # A list of coordinate dictionaries like [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]

    # Need the board dimensions to solve the avoid walls problem
    board_height = data["board"]["height"]
    board_width = data["board"]["height"]

    # Saving other information like other snakes and food on board
    snakes = data["board"]["snakes"]
    foods = data["board"]["food"]

    # Saving the cordinates of the possible move my snake can make as a dictionary 
    possible_moves = {
      "up": {
        "x":my_head["x"],
        "y":my_head["y"]+1,
      },
      "down": {
        "x":my_head["x"],
        "y":my_head["y"]-1,
      },
      "left": {
        "x":my_head["x"]-1,
        "y":my_head["y"],
      },
      "right": {
        "x":my_head["x"]+1,
        "y":my_head["y"],
      }
    }

    # Step 0: Don't allow your Battlesnake to move back on itself
    possible_moves = _avoid_me(my_body, possible_moves)

  # Step 1: Don't allow your Battlesnake to move into the walls
    possible_moves = _avoid_walls(board_height, board_width, possible_moves)

  # Step 2: Don't allow your Battlesnake to move into another snake
    possible_moves = _avoid_snakes(snakes, possible_moves)

  # Step 3: Move the battelesnake to the nearest food 
    target = get_target_close(foods,my_head)

    # Choose a random direction from the remaining possible_moves to move in, and then return that move

    # If there are any moves to be made
    if len(possible_moves)>0:
      # If there is food available - move to it
      if target is not None:
        move = move_to_target(possible_moves, my_head, target)

      # If no food - make a random move
      else:
        possible_moves = list(possible_moves.keys())
        move = random.choice(possible_moves)

    # If not - it's okay you tried
    else:
      move = "down"
      print("Well nobodys perfect")
    # TODO: Explore new strategies for picking a move that are better than random

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move


def _avoid_me(my_body,our_moves):
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    remove = []

    # Check if the cordinates of the body exists in any of the possible moves of our snake
    for move, cordinates in our_moves.items():
      if cordinates in my_body:
          remove.append(move)

    # Remove those moves
    for move in remove:
      del our_moves[move]

    return our_moves

def _avoid_walls(board_height,board_width,our_moves):
    remove = []

    # Check if the cordinates of the walls exists in any of the possible moves of our snake
    for move, cordinates in our_moves.items():
      if cordinates["x"]<0 or cordinates["x"]>=board_width:
          remove.append(move)
      if cordinates["y"]<0 or cordinates["y"]>=board_height:
        remove.append(move)

    # Remove those moves
    for move in remove:
      del our_moves[move]

    return our_moves

def _avoid_snakes(snakes, our_moves):
    remove = []

    # Check if the cordinates of other snakes exists in any of the possible moves of our snake
    for snake in snakes:
      for move, cordinates in our_moves.items():
        if cordinates in snake["body"]:  
            remove.append(move)

    # Remove those moves
    remove = set(remove)
    for move in remove:
      del our_moves[move]

    return our_moves

def get_target_close(foods,my_head):
    cordinates = []
    if len(foods)==0:
      return None

    # Save the food cordinates in a list
    for food in foods:
      cordinates.append([food["x"],food["y"]])
    #print(cordinates)
    # Find the closest food cordinate 
    tree = NearestNeighbors(n_neighbors = len(cordinates))
    tree = tree.fit(cordinates)
    results = tree.kneighbors([(my_head["x"],my_head["y"])])[1]
    print(results)
    idx = results[0]
    print(idx)
    return foods[idx[0]]

def move_to_target(our_moves, my_head, target):
    # Distance between the closest food cordinate and the snake head
    d_x = abs(my_head["x"]-target["x"])
    d_y = abs(my_head["y"]-target["y"])

    # Make the moves to the closest food cordinate
    for move, cordinates in our_moves.items():
      new_d_x = abs(cordinates["x"]-target["x"])
      new_d_y = abs(cordinates["y"]-target["y"])
      
      if new_d_x < d_x or new_d_y < d_y:  
        return move

    return list(our_moves.keys())[0]
    