from typing import Optional

import tcod.event

from actions import Action, EscapeAction, MovementAction


#EventHandler is a subclass of tcod EventDispatch

class EventHandler(tcod.event.EventDispatch[Action]):
    
    #override EventDispatch:ev_quit
    #ev_quit called when quit event is received
    def ev_quit(self, event: tcod.event.Quit): 
        raise SystemExit()

    #ev_keydown receives keypress events
    #Optional type is used to return either an Action subclass, or None
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.K_KP_8 or tcod.event.KP_w:
            action = MovementAction(dx=0, dy=-1)
        elif key == tcod.event.K_KP_2 or tcod.event.KP_x:
            action = MovementAction(dx=0, dy=1)
        elif key == tcod.event.K_KP_4 or tcod.event.KP_a:
            action = MovementAction(dx=-1, dy=0)
        elif key == tcod.event.K_KP_6 or tcod.event.KP_d:
            action = MovementAction(dx=1, dy=0)
        elif key == tcod.event.K_KP_7 or tcod.event.KP_q:
            action = MovementAction(dx=-1, dy=-1)
        elif key == tcod.event.K_KP_9 or tcod.event.KP_e:
            action = MovementAction(dx=1, dy=-1)
        elif key == tcod.event.K_KP_1 or tcod.event.KP_z:
            action = MovementAction(dx=-1, dy=1)
        elif key == tcod.event.K_KP_3 or tcod.event.KP_c:
            action = MovementAction(dx=1, dy=1)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        return action
