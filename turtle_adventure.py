"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random
import math


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


class RandomWalkEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self._id = None

    def create(self) -> None:
        self._id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)

    def update(self) -> None:
        speed = 70
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        self.x += dx * speed
        self.y += dy * speed

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(
            self._id,
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.x + self.size / 2,
            self.y + self.size / 2,
        )

    def delete(self) -> None:
        self.canvas.delete(self._id)


class ChasingEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self._id = None

    def create(self) -> None:
        self._id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)

    def update(self) -> None:
        player = self.game.player
        dx = (player.x - self.x) / 50
        dy = (player.y - self.y) / 50
        self.x += dx
        self.y += dy

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(
            self._id,
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.x + self.size / 2,
            self.y + self.size / 2,
        )

    def delete(self) -> None:
        self.canvas.delete(self._id)


class FencingEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self._id = None
        self._home_y = self.game.home.y
        self._home_x = self.game.home.x
        self._angle = 0
        self._radius = 50
        self._speed = 5

    def create(self) -> None:
        self._id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)

    def update(self) -> None:
        self._angle += self._speed
        if self._angle >= 360:
            self._angle -= 360

        radian_angle = math.radians(self._angle)
        dx = self._radius * math.cos(radian_angle)
        dy = self._radius * math.sin(radian_angle)
        self.x = self._home_x + dx
        self.y = self._home_y + dy

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(
            self._id,
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.x + self.size / 2,
            self.y + self.size / 2,
        )

    def delete(self) -> None:
        self.canvas.delete(self._id)


class CircledangerEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self._id = None
        self._colors = ["red", "blue", "green"]
        self._change_color_timer = 100
        self._color_change_counter = 0

    def create(self) -> None:
        self._id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)

    def update(self) -> None:
        dx = 1
        dy = 1
        self.x += dx
        self.y += dy

        self._color_change_counter += 1
        if self._color_change_counter == self._change_color_timer:
            self._color_change_counter = 0
            self._color = random.choice(self._colors)
            self.canvas.itemconfig(self._id, fill=self._color)

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(
            self._id,
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.x + self.size / 2,
            self.y + self.size / 2,
        )

    def delete(self) -> None:
        self.canvas.delete(self._id)


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.create_enemy()

    def create_random_walk_enemy(self) -> None:
        new_enemy = RandomWalkEnemy(self.__game, size=20, color="blue")
        # Set initial position of the enemy
        # Example: new_enemy.x = 100, new_enemy.y = 100
        new_enemy.x = 10
        new_enemy.y = 20
        self.__game.add_enemy(new_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        if self.__level == 1:
            new_enemy = RandomWalkEnemy(self.__game, size=10, color="red")
        elif self.__level == 2:
            new_enemy = ChasingEnemy(self.__game, size=30, color="blue")
        elif self.__level == 3:
            new_enemy = FencingEnemy(self.__game, size=40, color="green")
        else:
            new_enemy = CircledangerEnemy(self.__game, size=50, color="orange")

        self.__game.add_enemy(new_enemy)

        self.__game.after(100, self.create_enemy)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
