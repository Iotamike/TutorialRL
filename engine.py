#!/usr/bin/env python3
import tcod

from components.fighter import Fighter
from entity import Entity, get_blocking_entities_at_location
from actions import EscapeAction, MovementAction
from input_handlers import EventHandler
from render_functions import render_all, clear_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialise_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_monster, kill_player
from game_messages import MessageLog


def main() -> None:
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3


    colors = {
        'dark_wall': tcod.Color(0,0,100),
        'dark_ground': tcod.Color(50,50,100),
        'light_wall': tcod.Color(130,110,50),
        'light_ground': tcod.Color(200,180,50)
    }

    fighter_component = Fighter(hp=30, defence=2, power=5)
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
    entities = [player]

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)

    fov_recompute = True

    fov_map = initialise_fov(game_map)

    game_state = GameStates.PLAYERS_TURN

    message_log = MessageLog(message_x, message_width, message_height)

    
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        play_area = tcod.Console(map_width, map_height, order="F")
        panel = tcod.Console(screen_width, panel_height, order="F")
    
        while True:
            
            clear_all(root_console, entities)
            root_console.clear()

            if fov_recompute:
                recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
            
            render_all(root_console, play_area, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, map_width, map_height, bar_width, panel_height, panel_y, colors)

            fov_recompute = False                      

            context.present(root_console)

            # ======= PLAYER TURN ========================== # 

            player_turn_results = []

            for event in tcod.event.wait():
                
                #send events to EventHandler.dispatch method - check libtcod for details ...
                action = event_handler.dispatch(event)

                if action is None:
                    continue
                
                if isinstance(action, MovementAction):
                    if game_state == GameStates.PLAYERS_TURN:
                        if not game_map.is_blocked(player.x + action.dx, player.y + action.dy):
                            target = get_blocking_entities_at_location(entities, player.x + action.dx, player.y + action.dy)

                            if target:
                                attack_results = player.fighter.attack(target)
                                player_turn_results.extend(attack_results)
                            else:
                                player.move(action.dx,action.dy)
                                fov_recompute = True
                        game_state = GameStates.ENEMY_TURN

                elif isinstance(action, EscapeAction):
                    raise SystemExit()

            for player_turn_result in player_turn_results:
                message = player_turn_result.get('message')
                dead_entity = player_turn_result.get('dead')

                if message:
                    message_log.add_message(message)

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                    message_log.add_message(message)

            # === END PLAYER TURN ========================== # 

            # ======== ENEMY TURN ========================== # 

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')

                            if message:
                                message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, game_state = kill_player(dead_entity)
                                else:
                                    message = kill_monster(dead_entity)

                                message_log.add_message(message)

                                if game_state == GameStates.PLAYER_DEAD:
                                    break
                            
                        if game_state == GameStates.PLAYER_DEAD:
                            break
                else:    
                    game_state = GameStates.PLAYERS_TURN

            # ==== END ENEMY TURN ========================== #


if __name__ == "__main__":
    main()