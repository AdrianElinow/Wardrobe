
import json, sys, pprint

DEBUG = False

class Article():

    def __init__(self,  article_type : str, 
                        subtype: str, 
                        description : str, 
                        weather : list, 
                        price : float,
                        colors : list,
                        palettes : list,
                        uses : list ):

        self.type = article_type
        self.subtype = subtype
        self.description = description
        self.weather = weather
        self.price = price
        self.colors = colors
        self.palettes = palettes
        self.uses = uses


    def summary(self):
        return self.description

    def __str__(self):
        return self.summary()
        
def debug(*msgs):
    if DEBUG:
        print(" ".join(msgs));

def enforce_consistency( fixed_data ):

    for color, compatibles in fixed_data['compatibility'].items():

        for comp in compatibles:
            
            debug(color, compatibles, '\n\t',comp, fixed_data['compatibility'][comp])
            
            if color not in fixed_data['compatibility'][comp]:
                print("Fixing Discrepancy: ", comp,"E",color,"|",color,"/E",comp)
                
                fixed_data['compatibility'][comp].append(color)

    output = open('fixed.json','w')

    output.write( json.dumps( fixed_data, indent=4 ) )

    output.close()

def list_articles(wardrobe_data, article_type):
    
    pass


def robust_str_entry(prompt, options=[]):

    entry = ""

    while not entry:

        if options:
            print('Options: ')
        
        for idx, opt in enumerate(options):
            print('{0} | {1}'.format(idx, opt))

        entry = input(prompt).strip()

        if options:
            if entry not in options:
                entry = None
                print('Invalid')
            else:    
                try:
                    entry = options[int(opt)]
                except ValueError:
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
    

    pass

def search_tree( wardrobe ):
    #criteria = create_item()
    print('not yet implemented')


def create_outfit( wardrobe ):
    print('not yet implemented')


def save( save_filename, wardrobe ):

    print("saving wardrobe as {0}".format(save_filename))

    with open(save_filename,'w') as f:
        f.write( json.dumps(wardrobe, indent=4) )


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

            save('wardrobe.json', wardrobe)

            sys.exit(0)

        if opt in menu_nav.keys():
            ret = menu_nav[opt](wardrobe)


def main():
    
    print('Loading application data')
    fixed_data = json.load( open('fixed.json') )

    print('Validating application data')
    enforce_consistency( fixed_data )
    
    color_map = fixed_data['palettes']
    color_compatibility = fixed_data['compatibility']
    article_map = fixed_data['article_types']
    
    input("Ready? > ")

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
