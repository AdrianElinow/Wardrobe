# Wardrobe
 Outfit generator in Python

# Get Started
Run this command to get started:
> > python wardrobe.py help

## Importing wardrobe and import file format
The application uses *.json data stored to a local 'wardrobe.json' file, but you can also import data en-masse with a file formatted as such:
> {article_type} {article_subtype} "{description}" {color} {weather} {price}$

ex:
> overshirt hoodie "oversized graphic" black any 40$
> ...

see the included `wardrobe_import` file for an example

## TODO:
- Implement factor-based outfit generation
    - Build from user-selection
    - Generation by multiple criteria (ex: "palette:neutral use:formal)

- UI/UX with Flask + React
