
import json, os, platform, sys, pprint
from typing import *

DEBUG = False



class Article():

    def __init__(self,  article_type : str, 
                        subtype: str, 
                        description : str, 
                        weather : list, 
                        price : float,
                        colors : list):

        self.article_type = article_type
        self.subtype = subtype
        self.description = description
        self.weather = weather
        self.price = price
        self.colors = colors

    
    def from_json(json: Dict):
        return Article( json['article_type'], json['subtype'], json['description'], json['weather'], json['price'], json['colors'])

    def summary(self) -> str:
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
        }
        '''

class Wardrobe():
    
    def __init__(self, json):
        self.data = { article_type:Wardrobe.parse_articles(articles) for article_type, articles in json.items() }


    def parse_articles(articles: List[str]) -> List[Article]:
        if not articles:
            return []
    
        parsed = [ Article.from_json(article) for article in articles ]

        return parsed


    def add_article(self, article):
        self.data[article.article_type].append(article)

    def list_by_type(self, article_type: str) -> List:

        if article_type in self.data.keys():
            return self.data[article_type]
        
        return []


    def list_by(self, article_type: str =None, article_subtype: str =None) -> List:
        
        if article_type and article_type in self.data.keys():
            if article_subtype:
                return [ article for article in self.data[article_type] if article.subtype == article_subtype ] 

            return self.data[article_type]

        return []

    def dump(self) -> Dict:
        dump = {}
        
        for article_type, articles in self.data.items():
            if not articles:
                continue
            dump[article_type] = [ article.jsonify() for article in articles ]
        
        return dump
        
class WardrobeGenerator():

    def __init__(self, fixed_data_filename, wardrobe_data_filename=""):
        self.load_fixed_data(fixed_data_filename)

        self.wardrobe = Wardrobe(self.load_wardrobe_data(wardrobe_data_filename))

    def save(self, save_filepath ):
        print("saving wardrobe as {0}".format(save_filepath))

        with open(save_filepath,'w') as f:
            f.write( json.dumps(self.wardrobe.dump(), indent=4) )
    
    def load_fixed_data(self, fixed_data_filename):
        try:
            fixed_data = json.load( open(fixed_data_filename) )
            
            self.fixed_data = WardrobeGenerator.enforce_consistency( fixed_data )
            self.color_map = self.fixed_data['palettes']
            self.color_compatibility = self.fixed_data['compatibility']
            self.article_map = self.fixed_data['article_types']
            self.weather = self.fixed_data['weather']


        except JSONDecodeError as jsonde:
            print("Failed to load application data.")
            print("Error:",jsonde)
            sys.exit(1)


    def load_wardrobe_data(self, wardrobe_data_filename: str) -> str:
        cwd = os.getcwd()
        
        while True:
            fp = "{0}/{1}".format(cwd, wardrobe_data_filename)
            if os.path.exists(fp):
                entry = robust_str_entry("Wardrobe data file detected [{0}] | Use this file?\n\t>".format(fp), ['yes','no'])
                if entry == 'no':
                    wardrobe_data_filename = "---"
                    continue
            else:
                wardrobe_data_filename = robust_str_entry("No wardrobe file found [{0}] | Enter filename\n\t>".format(fp))
            if os.path.exists(fp):
                try:
                    return json.load(open(wardrobe_data_filename))
                except:
                    print("Failed to load data from {0}".format(wardrobe_data_filename))
                    wardrobe_data_filename = "---"

    def enforce_consistency( fixed_data ):

        for color, compatibles in fixed_data['compatibility'].items():
            for comp in compatibles:
                #debug(color, compatibles, '\n\t',comp, fixed_data['compatibility'][comp])
                if color not in fixed_data['compatibility'][comp]:
                    print("Fixing Discrepancy: ", comp,"E",color,"|",color,"/E",comp)
                    fixed_data['compatibility'][comp].append(color)

        output = open('fixed.json','w')
        output.write( json.dumps( fixed_data, indent=4 ) )
        output.close()
        return fixed_data

    def handle_add(self):
        article_type = robust_str_entry("Article type: >", list(fixed_data['classifications'].keys()))
        article_subtype = robust_str_entry("Article subtype: >",fixed_data['classifications'][article_type])

        existing = wardrobe.list_by(article_type, article_subtype)
        if existing:
            print("Existing {0}:{1}".format(article_type, article_subtype))        
            for item in existing:
                print('- {0}'.format(item))

        article = create_article(fixed_data, article_type, article_subtype)
        self.wardrobe.add_article(article)

    def handle_add_cli(self, args):
        print('handle_add_cli({0})'.format(','.join(args)))
        
        if len(args) == 0:
            print('Add Help -> ',
                '[type:{{{0}}}] [subtype:{{{1}}}] [description:str] [color:str] [temperature:<{2}>] [price:<$#>]'
                .format( ','.join(self.article_map.keys()), "depends on type", ','.join(self.weather)))
        
        elif len(args) == 1:
            print('Add Help -> ',
                '[type:{{{0}}}] [subtype:{{{1}}}] [description:str] [color:str] [temperature:<{2}>] [price:<$#>]'
                .format( args[0], ','.join(self.article_map[args[0]]), ','.join(self.weather)))

        else:
            article_type, article_subtype, description, color, temp, price = self.parse_article_cli_args(args)
            self.wardrobe.add_article(Article(article_type, article_subtype, description, color, temp, price))

    def handle_delete(self):
        print('Not yet implemented')

    def handle_delete_cli(self, args):
        print('handle_delete_cli({0})'.format(','.join(args)))
        print('Not yet implemented')

    def handle_nav(self):
        print('Not yet implemented')

    def handle_search(self):
        #["Type","Subtype","Description","Weather","Price","Colors","Palettes","Uses"]
        categories = robust_str_entry("Search by >", list(fixed_data['classifications'].keys()))
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

    def handle_search_cli(self):
        print('handle_search_cli({0})'.format(','.join(args)))
        print('Not yet implemented')


    def handle_create_outfit(self):
        print('Not yet implemented')

    def handle_generate_cli(self):
        print('handle_generate_cli({0})'.format(','.join(args)))
        print('Not yet implemented')

    def parse_article_cli_args(self, args):

        article_type, article_subtype, description, color, temp, price = ""

        for arg in args:
            # article type
            if arg in self.article_map.keys():
                article_type = arg

            # article subtype
            elif article_type and arg in self.article_map[article_type]:
                article_subtype = arg

            elif arg in self.color_map.keys():
                color = arg

            elif arg in ['hot','cold','normal','all','wet']:
                temp = arg

            elif '$' in arg:
                try:
                    price = int(arg.replace('$',''))
                except ValueError as ve:
                    pass

            else:
                description += " |",arg

        return article_type, article_subtype, description, color, temp, price


    def menu(self):

        menu_nav = {
            "add": self.handle_add,
            "delete": self.handle_delete,
            "nav": self.handle_nav,
            'search' : self.handle_search,
            'create outfit':self.handle_create_outfit,
            'exit': None
        }

        while True:
            try:
                opt = robust_str_entry('> ', list(menu_nav.keys()))

                if opt == 'exit':
                    break

                menu_nav[opt]()

                input('')
                clear_screen()
        
            except ValueError as ve:
                pass
            except KeyboardInterrupt as ki:
                break

        self.save('wardrobe.json')

    def handle_cli_transaction(self, args):

        cli_nav = {
            'add':self.handle_add_cli,
            'delete':self.handle_delete_cli,
            'search':self.handle_search_cli,
            'generate':self.handle_generate_cli
        }

        cli_nav[args[1]](args[2:])




def debug(*msgs):
    if DEBUG:
        print('[DEBUG]',msgs);



def robust_str_entry(prompt, options=[]):
    '''  '''

    if type(options) == type({}):
        debug("Converting dict keys to list of options")
        options = list(options.keys())

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
                                e = options[int(e)]
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
                    debug(options)
                    debug(entry, int(entry))

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
    
    # descr, temp, price, color(s)
    
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

    return Article(article_type, article_subtype, descr, temp, price, color)


def clear_screen():
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", end="")


def main():

    WG = WardrobeGenerator('fixed.json', 'wardrobe.json')

    WG.menu()


def is_cli_transaction( args: List[str] ) -> bool:
    
    if len(args) > 1:
        return args[1] in ['add','delete','update','search','generate']

    return False

def handle_cli_transaction( args: List[str] ):

    WG = WardrobeGenerator('fixed.json','wardrobe.json')

    WG.handle_cli_transaction(args)


if __name__ == '__main__':
    if is_cli_transaction(sys.argv):
        handle_cli_transaction(sys.argv)
    else:
        print("Starting Interactive")
        main()
