"""Lipeipei Sun
Santa Cross The Street Game
"""

import pyglet
from pyglet import shapes
from pyglet.window import key
import random
import datetime
from pyglet.window import mouse
import tkinter as tk
import tkinter.ttk as ttk


# CONSTANTS
# WINDOW
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
BACKGROUND_COLOR_R = 0.68
BACKGROUND_COLOR_G = 0.7
BACKGROUND_COLOR_B = 0.7
BACKGROUND_COLOR_A = 0.7
# CARS & ROADS
N_CAR_ON_RAOD = 5
N_TREE_ON_RAOD = 6
CAR_X_MODULE = 250
CAR_SCALE = 0.35
TREE_SCALE = 0.35
TREE_X_MODULE = 10
ROAD_Y = 100
CAR_STARTING_X = -60
CAR_IMG_LST_R = [pyglet.image.load(f"Car_{i}.png") for i in range(10)]
CAR_IMG_LST_L = [pyglet.image.load(f"Car_{i}.png") for i in range(8, 18)]
SIDEWALK_COLOR = (222, 222, 222)
# PEOPLE
SANTA_IMAGE = "Santa_1.png"
SANTA_SCALE = 0.1
SANTA_START_Y = 0
SANTA_MOVE_Y = 5
SANTA_MOVE_X = 5
SANTA_BUFFER = 1
BOY_IMAGE = "Boy_0.png"
BALLOON_IMAGE = "Boy_balloon.png"
DOG_IMAGE = "Dog_0.png"
BOY_SCALE = 0.2
BOY_SPEED_DX = 1
BALLOON_SCALE = 0.4
BALLOON_DEGREE = 20
BALLOON_MOVE_TIME = 1 / 5
DOG_BOY_DX = 10
DOG_SCALE = 0.1
DOG_MOVE_DX = 15
# MESSAGE
MESSAGE_SCALE = 1
MESSAGE_FAIL_IMG = "Message_fail.png"
MESSAGE_WIN_IMG = "Message_win.png"
# SNOW
SNOW_SCALE = 2.5
SNOW_GIF = "snow.gif"


window = pyglet.window.Window(
    width=WINDOW_WIDTH, height=WINDOW_HEIGHT, visible=False
    )
pyglet.gl.glClearColor(
    BACKGROUND_COLOR_R, BACKGROUND_COLOR_G, BACKGROUND_COLOR_B,
    BACKGROUND_COLOR_A
)


# GRAPHIC FUNCTIONS


@window.event
def on_draw():
    """
    Handle the drawing event for the game window.
    This function draws roads, sidewalks, people, trees,
    and messages in case of collision or win.
    """
    window.clear()
    road_test.draw()
    sidewalk.draw()
    santa.draw()
    snow.draw()
    # if collision(fail) or gift(win) happens, show a message
    if collision_flag:
        message.sprite.draw()
    if gift_flag:
        message.sprite.draw()


def update(dt):
    """
    Update the game state, including moving cars and
    checking for collisions or win conditions.
    This function is scheduled to be called regularly by Pyglet's clock.

    Args:
        dt (float): seconds elapsed since the last call of this function
    """
    if not scene_paused:
        road_test.move()
        collision_reset(road=road_test, santa=santa)
        win_reset(santa=santa, boy=boy)
        boy.move(BOY_SPEED_DX, BALLOON_DEGREE, DOG_MOVE_DX)
        if collision_flag is False:
            # Up, Down, Left, Right keys to control Santa walk direction
            if key_handler[key.UP]:
                santa.move("up")
                santa.update()
            if key_handler[key.DOWN]:
                santa.move("down")
                santa.update()
            if key_handler[key.RIGHT]:
                santa.move("right")
                santa.update()
            if key_handler[key.LEFT]:
                santa.move("left")
                santa.update()


def collision_reset(road, santa):
    """
    Check for collision between cars and santa,
    if collision happens, show a message and reset the santa

    Args:
        road (Road object): The Road object containing cars
        santa (Santa object): The Santa object containing santa
    """
    global collision_flag
    for car_list in [
                     road.car_sprites_1,
                     road.car_sprites_2,
                     road.car_sprites_3
                     ]:
        for car in car_list:
            # check if car is overlapped with santa
            if (
                santa.sprite.x + santa.sprite.width + SANTA_BUFFER
                    > car.sprite.x
                    and santa.sprite.x - SANTA_BUFFER
                    < car.sprite.x + car.sprite.width
                    and santa.sprite.y + santa.sprite.height - SANTA_BUFFER*3
                    > car.sprite.y
                    and santa.sprite.y + SANTA_BUFFER
                    < car.sprite.y + car.sprite.height
            ):
                collision_flag = True
                message.update_message(MESSAGE_FAIL_IMG)
                pyglet.clock.schedule_once(show_message, 3)
                # Stop Santa and Reset Santa's position
                santa.stop()
                santa.sprite.x = WINDOW_WIDTH / 2
                santa.sprite.y = SANTA_START_Y


def win_reset(santa, boy):
    """
    Check if Santa has reached the boy to deliver the gift and win the game
    If Santa has reached the boy, show a message and resset the Santa

    Args:
        santa (Santa object): The Santa object containing santa
        boy (Boy object): The Boy object containing boy
    """
    global gift_flag, collision_flag
    # Check if santa is overlapped with the boy
    if (
        santa.sprite.x + santa.sprite.width > boy.boy.x
        and santa.sprite.x < boy.boy.x + boy.boy.width
        and santa.sprite.y + santa.sprite.height > boy.boy.y
        and santa.sprite.y < boy.boy.y + boy.boy.height
    ):
        gift_flag = True
        message.update_message(MESSAGE_WIN_IMG)
        pyglet.clock.schedule_once(show_message, 3)
        # Stop Santa and Reset Santa's position
        santa.stop()
        santa.sprite.x = WINDOW_WIDTH / 2
        santa.sprite.y = SANTA_START_Y


def show_message(dt):
    """
    Disable the message flags after a delay,
    effectively hiding the collision or win messages.

    Args:
        dt (float): seconds elapsed since the last call of this function
    """
    global collision_flag, gift_flag
    collision_flag = False
    gift_flag = False


@window.event
def on_key_press(symbol, modifiers):
    """
    Handle key press events for the game.

    Args:
        symbol (class 'int'): The key symbol pressed.
        modifiers (class 'int'): Modifiers used during the key press
    """
    global scene_paused
    # Space key to control pause
    if symbol == key.SPACE:
        scene_paused = not scene_paused


@window.event
def on_mouse_press(x, y, button, modifiers):
    """
    Handle mouse press events for the game.

    Args:
        button (int): The mouse button pressed.
        modifiers (int): Modifiers used during the mouse click.
    """
    if button == mouse.LEFT:
        snow.toggle_visibility()


# PROJECT CLASSES
class Road:
    """
    Represents the road in the game, including moving cars.
    This class manages multiple car sprites and handles their movement.
    """

    def __init__(self):
        """
        Initialize the Road object with cars at specific positions.
        """
        self.car_sprites_1 = []
        self.car_sprites_2 = []
        self.car_sprites_3 = []
        for i in range(N_CAR_ON_RAOD):
            x_position = i * CAR_X_MODULE
            y_position = ROAD_Y
            car = Car(x_position, y_position, CAR_IMG_LST_R)
            self.car_sprites_1.append(car)
        for i in range(N_CAR_ON_RAOD):
            x_position = i * CAR_X_MODULE
            y_position = ROAD_Y * 3
            car = Car(x_position, y_position, CAR_IMG_LST_L)
            self.car_sprites_2.append(car)
        for i in range(N_CAR_ON_RAOD):
            x_position = i * CAR_X_MODULE
            y_position = ROAD_Y * 5
            car = Car(x_position, y_position, CAR_IMG_LST_R)
            self.car_sprites_3.append(car)

    def draw(self):
        """
        Draw the cars on the road.
        """
        for car in self.car_sprites_1:
            car.draw()
        for car in self.car_sprites_2:
            car.draw()
        for car in self.car_sprites_3:
            car.draw()

    def move(self):
        """
        Update the position of all cars on the road
        """
        for car in self.car_sprites_1:
            car.move_right(gui_app.car_speed)
        for car in self.car_sprites_2:
            car.move_left(gui_app.car_speed)
        for car in self.car_sprites_3:
            car.move_right(gui_app.car_speed)


class SideWalk:
    """
    Represents the sidewalks in the game, including trees and people.
    This class manages sidewalk graphics and other elements like trees and
    people on the sidewalks.
    """
    def __init__(self):
        """
        Initialize the SideWalk object with trees at specific positions.
        """
        self.batch = pyglet.graphics.Batch()
        sidewalk_1 = shapes.Rectangle(
            0, 0, WINDOW_WIDTH, 100, color=SIDEWALK_COLOR, batch=self.batch
        )
        sidewalk_2 = shapes.Rectangle(
            0, ROAD_Y * 2, WINDOW_WIDTH, 100, color=SIDEWALK_COLOR,
            batch=self.batch
        )
        sidewalk_3 = shapes.Rectangle(
            0, ROAD_Y * 4, WINDOW_WIDTH, 100, color=SIDEWALK_COLOR,
            batch=self.batch
        )
        sidewalk_4 = shapes.Rectangle(
            0, ROAD_Y * 6, WINDOW_WIDTH, 100, color=SIDEWALK_COLOR,
            batch=self.batch
        )
        self.sidewalks = [sidewalk_1, sidewalk_2, sidewalk_3, sidewalk_4]

        self.tree_sprites = []
        for m in range(4):
            for i in range(N_TREE_ON_RAOD):
                x_position = random.randrange(
                    TREE_X_MODULE, WINDOW_WIDTH - TREE_X_MODULE
                )
                y_position = ROAD_Y * (2 * m)
                tree = Tree(x_position, y_position)
                self.tree_sprites.append(tree)

    def draw(self):
        """
        Draw the sidewalks, trees, and people on them.
        """
        for sidewalk in self.sidewalks:
            sidewalk.draw()
        for tree in self.tree_sprites:
            tree.draw()
        for element in boy.boy_list:
            element.draw()


class Sprite:
    """
    A superclass for handling drawing sprites in the game.
    This class provides basic functionalities to draw sprites using
    a Pyglet batch, which helps in efficient rendering of multiple sprites.
    """

    def __init__(self):
        """
        Initialize the Sprite object with a Pyglet graphics batch.
        """
        self.batch = pyglet.graphics.Batch()

    def draw(self):
        """
        Draw the sprite using the Pyglet graphics batch.
        """
        self.batch.draw()


class Car(Sprite):
    """
    Represents a car in the game, as a subclass of Sprite.
    This class handles the rendering and movement of a car sprite.

    Args:
        Sprite (supper class): A superclass for handling drawing sprites.
    """
    def __init__(self, x_position, y_position, car_img_list):
        """
        Initialize a Car object with a specific position and image.

        Args:
            x_position (int): The x-coordinate for the car's initial position.
            y_position (int): The y-coordinate for the car's initial position.
            car_img_list (list): A list of images to randomly choose from for
                                 the car's appearance.
        """
        super().__init__()
        self.sprite = pyglet.sprite.Sprite(
            img=random.choice(car_img_list),
            x=x_position,
            y=y_position,
            batch=self.batch,
        )
        self.sprite.scale = CAR_SCALE

    def move_right(self, dx):
        """
        Move the car sprite to the right.

        Args:
            dx (int): The amount by which the car should move to the right.
        """
        self.sprite.x += dx
        if self.sprite.x > WINDOW_WIDTH:
            self.sprite.x = CAR_STARTING_X

    def move_left(self, dx):
        """
        Move the car sprite to the left.

        Args:
            dx (int): The amount by which the car should move to the left.
        """
        self.sprite.x -= dx
        if self.sprite.x < CAR_STARTING_X:
            self.sprite.x = WINDOW_WIDTH - CAR_STARTING_X


class Tree(Sprite):
    """
    Represents a tree in the game, as a subclass of Sprite.
    This class handles the rendering of a tree sprite on the screen.

    Args:
        Sprite (supper class): A superclass for handling drawing sprites.
    """
    def __init__(self, x_position, y_position):
        """
        Initialize a Tree object with a specific position.

        Args:
            x_position (int): The x-coordinate for the tree's position.
            y_position (int): The y-coordinate for the tree's position.
        """
        super().__init__()
        tree_img_list = [pyglet.image.load(f"Tree_{i}.png") for i in range(4)]
        self.sprite = pyglet.sprite.Sprite(
            img=random.choice(tree_img_list),
            x=x_position,
            y=y_position,
            batch=self.batch,
        )
        self.sprite.scale = TREE_SCALE
        self.sprite.opacity = 100


class Santa(Sprite):
    """
    Represents Santa in the game, as a subclass of Sprite.
    This class handles the rendering and movement of Santa's sprite.

    Args:
        Sprite (supper class): A superclass for handling drawing sprites.
    """
    def __init__(self):
        """
        Initialize the Santa object with a image and position.
        """
        super().__init__()
        santa_img = pyglet.image.load(SANTA_IMAGE)
        self.sprite = pyglet.sprite.Sprite(
            img=santa_img, x=WINDOW_WIDTH / 2, y=SANTA_START_Y,
            batch=self.batch
        )
        self.sprite.scale = SANTA_SCALE
        self.moving_direction = None

    def move(self, direction):
        """
        Set Santa moving direction.
        """
        self.moving_direction = direction

    def stop(self):
        """
        Stop Santa moving.
        """
        self.moving_direction = None

    def update(self):
        """
        Update Santa position if Santa is moving.
        """
        if self.moving_direction == "up" and self.sprite.y < (
            WINDOW_HEIGHT - self.sprite.height
             ):
            self.sprite.y += SANTA_MOVE_Y
        elif self.moving_direction == "down" and self.sprite.y > 0:
            self.sprite.y -= SANTA_MOVE_Y
        elif self.moving_direction == "left" and self.sprite.x > 0:
            self.sprite.x -= SANTA_MOVE_X
        elif self.moving_direction == "right" and self.sprite.x < (
            WINDOW_WIDTH - self.sprite.width
             ):
            self.sprite.x += SANTA_MOVE_X


class Boy(Sprite):
    """
    Represents a boy character in the game, as a subclass of Sprite.
    This class manages the boy character's sprite, including its movement and
    interactions.

    Args:
        Sprite (supper class): A superclass for handling drawing sprites.
    """
    def __init__(self):
        """
        Initialize the Boy object with a image and position.
        """
        super().__init__()
        self.boy_list = []
        boy_img = pyglet.image.load(BOY_IMAGE)
        bolloon_img = pyglet.image.load(BALLOON_IMAGE)
        dog_img = pyglet.image.load(DOG_IMAGE)
        self.boy = pyglet.sprite.Sprite(
            img=boy_img, x=WINDOW_WIDTH / 2, y=ROAD_Y * 6, batch=self.batch
        )
        self.balloon = pyglet.sprite.Sprite(
            img=bolloon_img,
            x=WINDOW_WIDTH / 2 + 12,
            y=ROAD_Y * 6 + 22,
            batch=self.batch,
        )
        self.dog = pyglet.sprite.Sprite(
            img=dog_img,
            x=WINDOW_WIDTH / 2 - DOG_BOY_DX,
            y=ROAD_Y * 6,
            batch=self.batch,
        )
        self.boy.scale = BOY_SCALE
        self.balloon.scale = BALLOON_SCALE
        self.dog.scale = DOG_SCALE
        self.boy_list.append(self.balloon)
        self.boy_list.append(self.dog)
        self.boy_list.append(self.boy)
        self.last_moved = datetime.datetime.now()
        # Set up defaut direction for boy's movement
        self.direction = -1

    def balloon_dog_move(self, rotate_degree, dog_dx):
        """
        Animate the movement of the boy's balloon and dog.

        Args:
            rotate_degree (int): The degree to which the balloon should rotate.
            dog_dx (int): The amount by which the dog should move.
        """
        if (
            datetime.datetime.now() - self.last_moved
             ).seconds >= BALLOON_MOVE_TIME:
            self.balloon.rotation = random.randint(
                -rotate_degree, rotate_degree
                )
            self.dog.x += random.randint(-dog_dx, dog_dx)
            self.last_moved = datetime.datetime.now()

    def move(self, boy_dx, rotate_degree, dog_dx):
        """
        Move the boy character along with its balloon and dog.

        Args:
            boy_dx (int): The amount by which the boy should move horizontally.
            rotate_degree (int): The degree to which the balloon should rotate.
            dog_dx (int): The amount by which the dog should move.
        """
        self.balloon_dog_move(rotate_degree, dog_dx)
        dx = boy_dx * self.direction
        for element in self.boy_list:
            element.x += dx
            if element.x < 0:
                element.x = 0
                self.direction = 1
            elif element.x + element.width > WINDOW_WIDTH:
                element.x = WINDOW_WIDTH - element.width
                self.direction = -1


class Messages(Sprite):
    """
    Represents a message display in the game, as a subclass of Sprite.
    This class manages the display of messages, such as win or fail messages.

    Args:
        Sprite (supper class): A superclass for handling drawing sprites.
    """
    def __init__(self):
        """
        Initialize the Messages object with a default image.
        """
        super().__init__()
        self.load_image(MESSAGE_FAIL_IMG)

    def load_image(self, image_path):
        """
        Load a new image for the message display.

        Args:
            image_path (str): The path to the new image file.
        """
        self.message_img = pyglet.image.load(image_path)
        self.sprite = pyglet.sprite.Sprite(
            img=self.message_img,
            x=0,
            y=0,
            batch=self.batch,
        )
        self.sprite.scale = MESSAGE_SCALE

    def update_message(self, new_image_path):
        """
        Update the message display with a new image.

        Args:
            new_image_path (str): The path to the new image file.
        """
        self.load_image(new_image_path)


class Snow(Sprite):
    """
    Represents snow animation in the game.
    This class handles the rendering and visibiliy toggle of the
    snow animation.

    Args:
        Sprite (supper class): A superclass for handling drawing sprites.
    """
    def __init__(self):
        """
        Initialize the Snow object with a snow animation.
        """
        super().__init__()
        self.ani = pyglet.resource.animation(SNOW_GIF)
        self.sprite = pyglet.sprite.Sprite(
            img=self.ani, x=0, y=0, batch=self.batch
            )
        self.sprite.scale = SNOW_SCALE
        self.visible = True

    def toggle_visibility(self):
        """
        Toggle the visibiliy of the snow animation.
        """
        self.visible = not self.visible

    def draw(self):
        """
        If the Snow is set to visible, draw the sprite.
        This overide the draw() method in the Sprite supper class.
        """
        if self.visible:
            super().draw()


class SantaGameGUI:
    def __init__(self, root):
        """set up tk window to None to start"""
        self.root = root
        self.root.title("Santa Cross The Street")
        self.create_widgets()
        self.car_speed = 1

    def get_value(self, v):
        """
        Get value from the scale.

        Args:
            v (string): Selected value on the Scale.
        """
        self.car_speed = float(v)

    def create_widgets(self):
        """
        Create widgets for the GUI.
        """
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.grid()

        # Add image
        self.canvas = tk.Canvas(
            self.frame, width=480, height=360, bg="#FFFFFF"
            )
        self.santa_img = tk.PhotoImage(file="Game_logo.png")
        self.canvas.create_image(240, 180, image=self.santa_img)
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Add labels
        intro_label = tk.Label(
            self.frame,
            text="Help Santa deliver the gift to the little boy!",
            font=("Helvetica", 16),
            pady=10,
            padx=10,
            fg="#d10f22",
        )
        intro_label.grid(row=1, column=0, columnspan=3)

        # Game difficulty selection
        easy_label = tk.Label(
            self.frame, text="EASY", font=("Helvetica", 12), pady=20, padx=10
        )
        easy_label.grid(row=2, column=0)
        hard_label = tk.Label(
            self.frame, text="HARD", font=("Helvetica", 12), pady=20, padx=10
        )
        hard_label.grid(row=2, column=2)
        slider = tk.Scale(
            self.frame,
            from_=1,
            to=4,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=250,
            showvalue=0,
            command=self.get_value
        )
        slider.grid(row=2, column=1)

        # Start the game button
        start_button = tk.Button(
            self.frame,
            text="PLAY",
            font=("Helvetica", 12, "bold"),
            padx=5,
            pady=5,
            command=self.run_game,
        )
        start_button.grid(row=3, column=1)

    def run_game(self):
        """run the program"""
        pyglet.clock.schedule_interval(update, 1/60)
        self.root.withdraw()  # Hide the Tkinter window
        window.set_visible(True)
        window.on_close = self.on_pyglet_close  # Set the close event handler
        pyglet.app.run()

    def on_pyglet_close(self):
        """Handle the Pyglet window close event."""
        pyglet.app.exit()
        window.set_visible(False)
        self.reopen_tkinter()  # Call method to reopen Tkinter window

    def reopen_tkinter(self):
        """Reopen the Tkinter window."""
        self.root.deiconify()  # Show the Tkinter window again


# GLOBAL VARIABLES
road_test = Road()
santa = Santa()
sidewalk = SideWalk()
message = Messages()
scene_paused = False
collision_flag = False
gift_flag = False
boy = Boy()
snow = Snow()
key_handler = pyglet.window.key.KeyStateHandler()
window.push_handlers(key_handler)


# MAIN PROGRAM
if __name__ == "__main__":
    root = tk.Tk()
    gui_app = SantaGameGUI(root)
    root.mainloop()
