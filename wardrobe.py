
import json, sys, pprint


def enforce_consistency( color_map ):

    for color, compatibles in color_map.items():

        for comp in compatibles:
            if color not in color_map[comp]:
                print("Fixing Discrepancy: ", comp,"E",color,"|",color,"/E",comp)
                
                color_map[comp].append(color)

    output = open('fixed.json','w')

    output.write( json.dumps( color_map, indent=4 ) )

    output.close()




def robust_str_entry(prompt, options=[]):

    entry = ""

    while not entry:

        if options:
            print('Options: ',' | '.join(options))

        entry = input(prompt).strip()

        if options:
            if entry not in options:
                entry = None
                print('Invalid')

    if ', ' in entry:
        return entry.split(', ')

    return entry


def create_item():
    
    # descr, price, color, palete, uses 
    article = robust_str_entry("Article type: >", ['Hat','Undershirt','Overshirt','Jacket','Pants','Footwear'])

    subtype = robust_str_entry("Article subtype: >")

    descr = robust_str_entry('Description > ')

    temp = robust_str_entry('Weather >', ['cold','normal','hot','all','wet'])
    if 'all' in temp:
        temp = 'all'

    price = int(robust_str_entry('Price ($) > '))

    color = robust_str_entry('Color(s) > ')

    palete = robust_str_entry("Palette(s) > ")

    uses = robust_str_entry('Use(s) > ')

    return {
        "Type":article,
        "Subtype":subtype,
        "Description":descr,
        "Weather":temp,
        "Price":price,
        "Colors":color,
        "Palettes":palete,
        "Uses":uses
    }


def add_item( wardrobe ):

    item = create_item()

    wardrobe[item['Type']].append(item)

    return wardrobe


def delete_item( wardrobe ):
    print('not yet implemented')

def nav_tree( wardrobe ):
    print('not yet implemented')

def search_tree( wardrobe ):
    #criteria = create_item()
    print('not yet implemented')


def create_outfit( wardrobe ):
    print('not yet implemented')


def menu( wardrobe, menu_nav ):

    if not menu_nav or not wardrobe:
        print('malformed')
        sys.exit(1)

    while True:

        print('options:')
        for k,v in menu_nav.items():
            print('{0}'.format(k))

        opt = robust_str_entry('> ').lower()

        if opt == 'exit':
            with open('wardrobe.json','w') as f:
                f.write( json.dumps(wardrobe, indent=4) )

            sys.exit(0)

        if opt in menu_nav.keys():
            ret = menu_nav[opt](wardrobe)


def main():

    color_map = json.load( open(sys.argv[1]) )

    enforce_consistency( color_map )


    input("Continue? > ")

    menu_nav = {
        "add": add_item,
        "delete": delete_item,
        "nav": nav_tree,
        'search' : search_tree,
        'create outfit':create_outfit,
        'exit': None
    }

    
    wardrobe = json.load(open('wardrobe.json')) 

    menu( wardrobe, menu_nav )





if __name__ == '__main__':
    main()
