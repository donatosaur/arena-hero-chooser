# Arena: The Contest Hero Chooser
A random PvP team generator for the board game Arena: The Contest (https://arenathecontest.com/)

## How do I use it?
Just run it in a python shell! There's a simple CLI included in the script.

## Why would I want to use this?
It's meant to introduce a degree of randomness in your games, to force you to experiment with heroes you might avoid picking on your own teams, or to simply provide a challenge. Who needs a healer or tank, anyway?

## Changing the Available Heroes
If you want to use different/custom heroes/classes, you'll need to add them to the existing file in res/heroes.txt, or create your own file with one hero on each line, and each line containing "hero name, hero class" (without quotes). Basically, the format is as follows:
  hero1 name, hero1 class
  hero2 name, hero2 class
  ...

## To-Do
- [x] add a CLI interface demo when run as a script
- [ ] add the ability to pass the hero file as a command line argument
- [ ] add a gui
- [ ] add Tanares Adevntures heroes
 
