class Tile:
    """
    A tile on the map. It may or may not be blocked, and it may or may not block sight
    """

    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        
        #by default, if a tile is blocked, it blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        self.explored = False

        