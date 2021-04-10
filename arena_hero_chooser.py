# Arena: The Contest Hero Chooser is a random PvP team generator for the board game Arena: The Contest (see https://arenathecontest.com/)
# Copyright (C) 2021 Donato Quartuccia
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The creator of this program is not affiliated with Dragori Games or Arena: The Contest.
# All trademarks and copyrights are the property of their respective owners.

import random
from os import path


class PathNotSetError(Exception):
    """
    Raised when Team._hero_file_path is not set
    """
    pass


class Team:
    """
    A team belonging to a player. May have 3 or 4 heroes.
    Teams are compared based on the value of their rolls and share a pool of possible heroes.
    """
    # Class variables:
    _hero_file_path = None        # holds path to txt file containing hero & class data
    _possible_heroes = None       # initialized when first class instance is created
    _team_size = 3                # should only be changed by the set_team_size class method
    _allow_special_class = True   # should only be changed by the disallow_special class method

    @classmethod
    def get_team_size(cls):
        return cls._team_size

    @classmethod
    def set_hero_file(cls, path_to_file):
        """
        Sets the path to the txt file containing properly-formatted (see readme) hero & class data to filename.

        :raises FileNotFoundError: if path to filename doesn't exist
        :param str path_to_file: path to file containing properly-formatted heroes dictionary
        """
        if not path.isfile(path_to_file):
            raise FileNotFoundError
        else:
            cls._hero_file_path = path_to_file

    @classmethod
    def load_heroes(cls):
        """
        Initializes the cls._possible_heroes dictionary with class_name -> list[heroes] pairs.

        Preconditions:
            - cls.set_hero_file must have been called to set the file to load heroes from
            - file must be properly formatted (see readme)

        :raises PathNotSetError: if cls._hero_file_path was not set
        :raises FileNotFoundError: if path to filename doesn't exist
        """

        if not cls._hero_file_path:
            raise PathNotSetError("cls._hero_file_path must be set before creating a Team")
        elif not path.isfile(cls._hero_file_path):
            raise FileNotFoundError
        else:
            all_heroes = {}
            with open(cls._hero_file_path, 'r') as hero_file:
                for line in hero_file:
                    heroes = line.split(", ")
                    hero_name = heroes[0]
                    hero_class = heroes[1].strip('\n')
                    # match the hero with its class
                    try:
                        # add the hero to its associated class list (if it's not the first hero of that class)
                        all_heroes[hero_class].append(hero_name)
                    except KeyError:
                        # create a list to store heroes of that class if this is the first hero
                        all_heroes[hero_class] = [hero_name]

            cls._possible_heroes = all_heroes

    @classmethod
    def disallow_special(cls):
        """
        Prevents any hero from the special class (e.g. The Faceless Emperor) from being chosen as a team member,
        and removes the special class from _possible_heroes if it is present.

        Sets cls._allow_special_class to False.
        """
        if cls._allow_special_class:
            cls._allow_special_class = False      # prevent special class from being added to possible_heroes
        if cls._possible_heroes and 'Special' in cls._possible_heroes:
            del(cls._possible_heroes['Special'])  # remove special class from possible_heroes if it was already added

    @classmethod
    def set_team_size(cls, team_size):
        """
        Sets class variable team_size to 3 or 4.

        :param int team_size: Number of heroes to place on each team. Must be 3 or 4.
        :raises ValueError: if team_size is not 3 or 4
        """

        if cls._team_size == 3 or cls._team_size == 4:
            cls._team_size = team_size
        else:
            raise ValueError("set_team_size called with bad value")

    def __init__(self, team_name):
        """
        Creates a Team with the specified team_name.
        If this is the first time a Team has been created, initializes the heroes dictionary (cls._possible_heroes).

        Preconditions:
            - cls.set_hero_file must have been called to set the file to load heroes from
            - *(optional)* cls.set_team_size must have been called to set the team size to 4 (default is 3)
            - *(optional)* cls.disallow_special must have been called to exclude the special class (included by default)

        :param str team_name: a name for the Team
        """

        # if this is the first time any Team has been created, initialize the heroes database
        if self._possible_heroes is None:
            self.load_heroes()

        # remove the special class from consideration if disallow_special() was previously called and
        # the special class is somehow still among the possible_heroes to be chosen
        if not self._allow_special_class and 'Special' in self._possible_heroes:
            del(self._possible_heroes['Special'])

        self._name = team_name
        self._roll = random.randint(1, 20)  # roll a d20
        self._possible_classes = list(self._possible_heroes.keys())
        self._heroes = []  # len(self._heroes) should never exceed cls.team_size

    def get_name(self):
        return self._name

    def get_roll(self):
        return self._roll

    def print_roll(self):
        a_or_an = "an" if self._roll in [8, 11, 18] else "a"
        print(self._name, "rolled", a_or_an, self._roll)

    def reroll(self):
        """
        Sets self._roll to a random integer between 1 and 20, mimicking a d20 dice roll
        """
        self._roll = random.randint(1, 20)

    def choose_hero(self):
        """
        Adds a randomly-chosen hero to the Team in compliance with the standard PvP rules of Arena: the Contest.

        Heroes are chosen from cls._possible_heroes, are equally weighted, may only be chosen if no other hero of
        that class is on the Team, and may not be chosen if present on an opponent's Team.

        Removes the chosen hero from cls._possible_heroes and the chosen class from self._possible_classes.
        Adds the chosen hero to self._heroes.
        """
        # weight random choice of class by num of heroes in each class, prevent choosing from an empty list
        keys_to_choose_from = [key for key in self._possible_classes for _ in self._possible_heroes[key]]

        # choose a hero and add it to self.heroes
        key = random.choice(keys_to_choose_from)
        hero = random.choice(self._possible_heroes[key])
        self._heroes.append(hero)

        # prevent this team from choosing another hero of the same class
        self._possible_classes.remove(key)

        # prevent any team from choosing the same hero
        self._possible_heroes[key].remove(hero)

    def __lt__(self, other):
        return self._roll < other._roll if isinstance(other, Team) else NotImplemented

    def __gt__(self, other):
        return self._roll > other._roll if isinstance(other, Team) else NotImplemented

    def __eq__(self, other):
        return self._roll == other._roll if isinstance(other, Team) else NotImplemented

    def __str__(self):
        return self._name + "\'s team:\n" + '\n'.join(self._heroes)

    def __repr__(self):
        return "Team(_possible_heroes={}, _team_size={}, _allow_special_class={}, _name={}," + \
               "_roll = {} _possible_classes={}, _heroes={})"\
                .format(self._possible_heroes, self._team_size, self._allow_special_class,
                        self._name, self._roll, self._possible_classes, self._heroes)


if __name__ == '__main__':
    print("Welcome to the Arena! We're going to generate a random team for you.")
    print("")

    Team.set_hero_file("./res/heroes.txt")

    # ask user to pick a team of size 3 or 4
    while True:
        num_heroes = input("Would you like to play with 3 or 4 heroes per team? ")
        if num_heroes == "3" or num_heroes == "4":
            Team.set_team_size(int(num_heroes))
            break
        else:
            print("Please enter only \"3\" or \"4\".")
            print("")

    # ask user to choose whether to include special character(s)
    while True:
        use_special = input("Would you like to play with the special class (i.e. The Faceless Emperor)? ").lower()
        if use_special == "y" or use_special == "yes":
            break
        elif use_special == "n" or use_special == "no":
            Team.disallow_special()
            break
        else:
            print("Please enter (y)es or (n)o.")
            print("")

    # ask user to choose unique team names
    team_1_name = input("Please enter a name for the first team captain: ")
    team_2_name = input("Please enter a name for the second team captain: ")
    while team_1_name == team_2_name:
        print("Please choose a different name for each team.")
        print("")
        team_1_name = input("Please enter a name for the first team captain: ")
        team_2_name = input("Please enter a name for the second team captain: ")

    # initialize teams
    team_1 = Team(team_1_name)
    team_2 = Team(team_2_name)

    # determine who goes first, while tied, keep re-rolling
    while team_1 == team_2:
        print("")
        team_1.print_roll()
        team_2.print_roll()
        print("Oops. It's a tie! Rolling again...")
        team_1.reroll()
        team_2.reroll()

    # output team order
    print("")
    team_1.print_roll()
    team_2.print_roll()
    print("")
    print(max(team_1, team_2).get_name() + "\'s team picks first.")

    # fill each team with heroes, alternating between them
    for i in range(Team.get_team_size()):
        max(team_1, team_2).choose_hero()
        min(team_1, team_2).choose_hero()

    # output teams
    print("")
    print(team_1)
    print("")
    print(team_2)
