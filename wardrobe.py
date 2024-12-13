
import json, os, platform, sys, pprint

DEBUG = False


class Wardrobe():
    
    def __init__(self, json):
        
        self.data = { article_type:Wardrobe.parse_articles(articles) for article_type, articles in json.items() }


    def parse_articles(articles):
        if not articles:
            return []
    
        parsed = [ Article.from_json(article) for article in articles ]

        return parsed


    def add_article(self, article):
        self.data[article.article_type].append(article)

    def list_by_type(self, article_type):

        if article_type in self.data.keys():
            return self.data[article_type]
        
        return []


    def list_by(self, article_type=None, article_subtype=None):
        
        if article_type and article_type in self.data.keys():
            if article_subtype:
                return [ article for article in self.data[article_type] if article.subtype == article_subtype ] 

            return self.data[article_type]

        return []

    def dump(self):
        dump = {}
        
        for article_type, articles in self.data.items():
            if not articles:
                continue
            dump[article_type] = [ article.jsonify() for article in articles ]
        
        return dump


class Article():

    def __init__(self,  article_type : str, 
                        subtype: str, 
                        description : str, 
                        weather : list, 
                        price : float,
                        colors : list,
                        palettes : list,
                        uses : list ):

        self.article_type = article_type
        self.subtype = subtype
        self.description = description
        self.weather = weather
        self.price = price
        self.colors = colors
        self.palettes = palettes
        self.uses = uses

    
    def from_json(json):
        return Article( json['Type'], json['Subtype'], json['Description'], json['Weather'], json['Price'], json['Colors'], json['Palettes'], json['Uses'])

    def summary(self):
        return self.description

    def __str__(self):
        return self.summary()

    def jsonify(self):
        return self.__dict__
        '''
        return {
            "Type":self.type,
            "Subtype":self.subtype,
            "Description":self.descr,
            "Weather":self.weather,
            "Price":self.price,
            "Colors":self.colors,
            "Palettes":self.palettes,
            "Uses":self.uses
        }
        '''
        



def debug(*msgs):
    if DEBUG:
        print(" ".join(msgs));


def save( save_filename, wardrobe ):
    print("saving wardrobe as {0}".format(save_filename))

    with open(save_filename,'w') as f:
        f.write( json.dumps(wardrobe.dump(), indent=4) )


def load_wardrobe_data():
    data_filename = 'wardrobe.json'
    cwd = os.getcwd()
    while True:
        fp = "{0}/{1}".format(cwd, data_filename)
        if os.path.exists(fp):
            entry = robust_str_entry("Wardrobe data file detected [{0}] | Use this file?\n\t>".format(fp), ['yes','no'])
            if entry == 'No':
                data_filename = "---"
        else:
            data_filename = robust_str_entry("No wardrobe file found [{0}] | Enter filename\n\t>".format(fp))
        if os.path.exists(fp):
            try:
                return json.load(open(data_filename))
            except:
                print("Failed to load data from {0}".format(data_filename))
                data_filename = "---"
           
        


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



def robust_str_entry(prompt, options=[]):

    entry = ""

    while not entry:


        if options:
            print('Options: ')
        
        for idx, opt in enumerate(options):
            print('{0} | {1}'.format(idx, opt))

        try:
            entry = input(prompt).strip()

            if options:
                if ',' in entry:
                    entries = entry.split(',')
                    selected = []

                    for e in entries:
                        if e not in options:
                            try:
                                e = options[int(entry)]
                                selected.append(e)
                            except ValueError as ve:
                                pass
                        else:
                            selected.append(e)
                    
                    if selected:
                        return selected
                    else:
                        entry = None
                        selected = None
                        print("Invalid")

                if entry not in options:
                    entry = options[int(entry)] # try to interpret as numeric choice

                    if entry not in options: # still not valid
                        entry = None
                        print('Invalid')
        
        except ValueError as ve: # handle numeric choice conversion error
            debug(ve)
            entry = None
            print('Invalid')
        except KeyboardInterrupt:
            sys.exit(0)

    return entry



def create_article(fixed_data, article_type=None, article_subtype=None):
    
    # descr, price, color, palete, uses 
    
    if not article_type:
        article_type = robust_str_entry("Article type: >", fixed_data['classifications'])

    if not article_subtype:
        article_subtype = robust_str_entry("Article subtype: >",fixed_data['classifications'][article_type])
    
        descr = robust_str_entry('Description > ')
    temp = robust_str_entry('Weather >', ['cold','normal','hot','all','wet'])
    if 'all' in temp:
        temp = 'all'

    price = int(robust_str_entry('Price ($) > '))
    color = robust_str_entry('Color(s) > ', list(fixed_data['compatibility'].keys()))
    palete = robust_str_entry("Palette(s) > ", fixed_data['palettes'])
    uses = robust_str_entry('Use(s) > ')

    return Article(article_type, article_subtype, descr, temp, price, color, palete, uses)


def delete_item( fixed_data, wardrobe ):
    print('not yet implemented')

def nav_tree( fixed_data, wardrobe ):
    pass


def add_item( fixed_data, wardrobe):
    
    article_type = robust_str_entry("Article type: >", list(fixed_data['classifications'].keys()))
    article_subtype = robust_str_entry("Article subtype: >",fixed_data['classifications'][article_type])

    existing = wardrobe.list_by(article_type, article_subtype)
    if existing:
        print("Existing {0}:{1}".format(article_type, article_subtype))        
        for item in existing:
            print('- {0}'.format(item))

    article = create_article(fixed_data, article_type, article_subtype)
    wardrobe.add_article(article)


def search_tree( fixed_data, wardrobe ):
    
    #["Type","Subtype","Description","Weather","Price","Colors","Palettes","Uses"]
    categories = robust_str_entry("Search by >", fixed_data['classifications'])
    #inclusivity = "Inclusive"

    #if len(categories) > 1:
    #    inclusivity = robust_str_entry("Inclusive/Exclusive >")

    criteria = categories

    data = wardrobe.list_by_type(criteria)

    if data:
        for article in data:
            print('- ',article)
    else:
        print('No data to display')


def create_outfit( fixed_data, wardrobe ):
    print('not yet implemented')


def clear_screen():
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", end="")

def menu( wardrobe, fixed_data, menu_nav ):

    if not menu_nav or not wardrobe:
        print('malformed')
        sys.exit(1)

    while True:

        try:
            opt = robust_str_entry('> ', list(menu_nav.keys()))

            if opt == 'exit':
                break

            menu_nav[opt](fixed_data, wardrobe)

            input('>')
            clear_screen()
    
        except ValueError as ve:
            pass
        except KeyboardInterrupt as ki:
            break
            
    save('wardrobe_1.json', wardrobe)
    sys.exit(0)


def main():
    
    print('Loading application data')
    fixed_data = json.load( open('fixed.json') )

    print('Validating application data')
    enforce_consistency( fixed_data )
    
    color_map = fixed_data['palettes']
    color_compatibility = fixed_data['compatibility']
    article_map = fixed_data['article_types']

    app_fixed_data = { "palettes": color_map, "compatibility":color_compatibility, "classifications":article_map }
    
    menu_nav = {
        "add": add_item,
        "delete": delete_item,
        "nav": nav_tree,
        'search' : search_tree,
        'create outfit':create_outfit,
        'exit': None
    }

    print('Loading wardrobe data')

    wardrobe_data = load_wardrobe_data() 
    
    print('Done')
    input("Press [Enter] to start > ")

    menu( Wardrobe(wardrobe_data), app_fixed_data, menu_nav )





if __name__ == '__main__':
    main()
