import tcod

from enum import Enum

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def render_all(root_console, play_area, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, map_width, map_height, bar_width, panel_height, panel_y, colors):

    # render function updated for compatibility with newest tcod
    #
    # root_console is the context we will show in the main loop with context.present
    # so we blit everything to play_area and panel as per the roguelikedev 'old' tutorial
    # then we blit those to the root_console, which is then displayed in the main loop
    #
    # more than one context.present will give you flickering
    #
    # You could just blit everything to one console and keep tabs on all the positions
    # however, separation makes sense for advanced UI's, easy reorganisation and not
    # forcing constant map re-draws 
    # e.g. in the future you might have a console popping up with options but no 'time'
    # passing. So this way you can put it in a new console, blit it on top of the rest and
    # freeze all the other consoles.
    #
    # TO DO
    #
    # break this all out into seperate render functions / renderer class that handles blitting whatever to the root_console

    if fov_recompute:
        play_area.clear() #clear all tiles when recomputing fov
        #draw all the tiles in the world map
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(play_area, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(play_area, x, y, colors.get('light_ground'), tcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(play_area, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(play_area, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

    

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    
    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(play_area, entity, fov_map)
        
    play_area.blit(root_console, 0,0, 0,0, map_width, map_height)
    clear_all(play_area, entities) #clears the current entity positions stored on the play_area console *after* blit to root_console

    
    tcod.console_set_default_background(panel, tcod.black)
    panel.clear()

    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, tcod.light_red, tcod.darker_red)

    panel.blit(root_console, 0,map_height, 0,0, screen_width, panel_height)


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width >0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
                        '{0}: {1}/{2}'.format(name,value,maximum))
    

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)