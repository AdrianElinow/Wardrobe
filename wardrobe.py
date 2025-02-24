
import json, os, platform, sys, random, uuid
from pprint import pprint
from typing import *

DEBUG = False
PRETTY = True


class Article():

    def __init__(self,  oid: str,
                        article_type : str, 
                        subtype: str, 
                        description : str, 
                        colors : List[str],
                        weather : List[str], 
                        price : float):

        self.oid = oid if oid else uuid.uuid4()

        self.article_type = article_type
        self.article_subtype = subtype
        self.description = description
        self.weather = weather
        self.price = price
        self.colors = [ c.lower() for c in colors] if type(colors) == type([]) else []

    def from_json(json: Dict):
        try:
            oid = uuid.uuid4() if 'oid' not in json else uuid.UUID(json['oid'])

            return Article(oid, json['article_type'], json['article_subtype'], json['description'], json['colors'], json['weather'], json['price'])
        except KeyError as ke:
            print("Error while importing from JSON \n{0}\n".format(json))
            print(ke)

    def summary(self) -> str:
        main_line = "{0} {1} {2}".format((','.join(self.colors) if self.colors else "").capitalize(), self.description.capitalize(), self.article_subtype.capitalize(), )
        summary = "{0:55}|(${3}|{1}|{2})".format(main_line, self.article_type, "{0} weather".format(self.weather), self.price)
        
        return summary

    def __str__(self):
        return self.summary()

    def jsonify(self):
        data = self.__dict__
        data['oid'] = str(data['oid'])

        return data

class Outfit():

    def __init__(self, oid, article_map, articles: List[Article]):

        self.oid = uuid.uuid4() if not oid else oid

        if not articles:
            raise IndexError("'articles' cannot be empty")

        self.articles = articles

    def from_json(article_map, outfit_json: Dict):

        articles = {}
        oid = uuid.uuid1()

        for article_type, article in outfit_json.items():
            
            if article_type == 'oid':
                oid = uuid.UUID(article)
                continue

            items = []

            if type(article) == type({}):
                items.append(article)
            elif type(article) == type([]):
                items = article

            articles[article_type] = [ Article.from_json(item) for item in items ]

        return Outfit( oid, article_map, articles )

    def dump(self):
        data = { article_type:[ article.jsonify() for article in articles ] for article_type, articles in self.articles.items() }

        data['oid'] = str(self.oid)

        return data

    def __str__(self):

        summary = f"Outfit - [{self.oid}]"

        for article_type,articles in self.articles.items():
            if articles:
                summaries = [ article.summary() for article in articles ]
                summary += "\n{0:10}| {1}".format(article_type, '\n\t'.join(summaries) )

        return summary



class Wardrobe():
    
    def __init__(self, article_map, json):
        
        self.outfit_history = []
        if 'outfit_history' in json.keys() and json['outfit_history'] != []:
            for outfit_data in json['outfit_history']:
                if outfit_data:
                    self.outfit_history.append(Outfit.from_json(article_map, outfit_data))
            json.pop('outfit_history')

        self.data = { article_type:Wardrobe.parse_articles(articles) for article_type, articles in json.items()}
        
        for article_type in article_map.keys():
            if article_type not in self.data.keys():
                self.data[article_type] = []


    def add_outfit(self, outfit: Outfit):
        if self.outfit_history:
            self.outfit_history.append(outfit)
        else:
            self.outfit_history = [outfit]

    def parse_articles(articles: List[str]) -> List[Article]:
        if type(articles) != type([]):
            raise ValueError("incorrect type 'articles'")

        if not articles:
            return []
    
        parsed = [ Article.from_json(article) for article in articles ]

        return parsed


    def add_article(self, article):
        self.data[article.article_type].append(article)
        return article

    def remove_article(self, article):
        if article in self.data[article.article_type]:
            self.data[article.article_type].remove(article)
        else:
            print("Article not found in '{0}'".format(article.article_type))

    def list_by_type(self, article_type: str) -> List:

        if article_type in self.data.keys():
            return self.data[article_type]
        
        return []


    def list_by(self, article_type: str ="", article_subtype: str ="", description:str ="", colors: List[str] =[], weather: str ="", price: int =0) -> List:
        
        if article_type and article_type in self.data.keys():
            if article_subtype:
                return [ article for article in self.data[article_type] if article.article_subtype == article_subtype ] 

            return self.data[article_type]

        return []

    def list_by_type(self, article_type: str) -> List[Article]:
        return self.data[article_type]

    def list_by_subtypes(self, article_type: str, subtypes: List[str]) -> List[Article]:
        articles = self.list_by_type(article_type)

        return [ article for article in articles if article.article_subtype in subtypes]

    def list_by_color(self, article_type: str, colors: List[str]) -> List[Article]:
        articles = self.list_by_type(article_type)

        selected_articles = [article for article in articles if Wardrobe.article_color_in_colors(article, colors) ]

        return selected_articles

    def article_color_in_colors(article: Article, colors: List[str]) -> bool:

        for color in article.colors:
            if color in colors:
                return True

        return False

    def list_by_weather(self, article_type: str, weather: str) -> List[Article]:
        articles = self.list_by_type(article_type)

        selected_articles = [article for article in articles if (weather in article.weather or 'any' in article.weather) ]

        return selected_articles


    def dump(self) -> Dict:
        dump = {}
        
        for article_type, articles in self.data.items():
            if not articles:
                continue
            dump[article_type] = [ article.jsonify() for article in articles if article ]
        
        dump['outfit_history'] = [ outfit.dump() for outfit in self.outfit_history if outfit ]

        return dump
        

class WardrobeGenerator():

    cli_modes = ['add','list','delete','generate','import','history','help','last']

    def __init__(self, fixed_data_filename, wardrobe_data_filename="", is_cli=False):
        self.load_fixed_data(fixed_data_filename)
        self.is_cli = is_cli

        self.wardrobe = Wardrobe(self.article_map, self.load_wardrobe_data(wardrobe_data_filename))
        self.filepath = wardrobe_data_filename

    def save(self, save_filepath=None, pretty=False ):
        if not save_filepath:
            save_filepath = self.filepath

        if not self.is_cli:
            print("saving changes to {0}".format(save_filepath))

        with open(save_filepath,'w') as f:
            if pretty:
                f.write( json.dumps(self.wardrobe.dump(), indent=4))
            else:
                f.write(json.dumps(self.wardrobe.dump()))
    
    def load_fixed_data(self, fixed_data_filename):
        try:
            fixed_data = json.load( open(fixed_data_filename) )
            
            self.fixed_data = WardrobeGenerator.enforce_consistency( fixed_data )
            self.palettes = self.fixed_data['palettes']
            self.color_map = self.fixed_data['compatibility']
            self.article_map = self.fixed_data['article_types']
            self.weather = self.fixed_data['weather']
            self.uses = self.fixed_data['uses']


        except json.JSONDecodeError as jsonde:
            print("Failed to load application data.")
            debug("Error:",jsonde)
            sys.exit(1)


    def load_wardrobe_data(self, wardrobe_data_filename: str) -> str:
        cwd = os.getcwd()
        fp = "{0}/{1}".format(cwd, wardrobe_data_filename)
        data = None
        
        if self.is_cli and os.path.exists(fp):
            try:
                with open(wardrobe_data_filename) as wardrobe_data:
                    data = json.load(open(wardrobe_data_filename))
                return data
            except Exception as e:
                debug(e)
                print("Failed to load data from {0}".format(wardrobe_data_filename))
                wardrobe_data_filename = "---"


        while True:
            fp = "{0}/{1}".format(cwd, wardrobe_data_filename)
            if os.path.exists(fp):
                entry = robust_str_entry("Wardrobe data file detected [{0}] | Use this file?\n\t>".format(fp), ['no','yes'])
                if entry == 'no':
                    wardrobe_data_filename = "---"
                    continue
            else:
                wardrobe_data_filename = robust_str_entry("No wardrobe file found [{0}] | Enter filename\n\t>".format(fp))
            if os.path.exists(fp):
                try:
                    with open(wardrobe_data_filename) as wardrobe_data:
                        data = json.load(open(wardrobe_data_filename))
                    return data
                except Exception as e:
                    debug(e)
                    print("Failed to load data from {0}".format(wardrobe_data_filename))
                    wardrobe_data_filename = "---"


    def enforce_consistency( fixed_data ):

        for color, compatibles in fixed_data['compatibility'].items():
            for comp in compatibles:
                #debug(color, compatibles, '\n\t',comp, fixed_data['compatibility'][comp])
                if color not in fixed_data['compatibility'][comp]:
                    print("Fixing Discrepancy: ", comp,":",color,"|",color,":",comp)
                    fixed_data['compatibility'][comp].append(color)

        output = open('fixed.json','w')
        output.write( json.dumps( fixed_data, indent=4 ) )
        output.close()
        return fixed_data

    def handle_add_cli(self, args):
        debug('handle_add_cli({0})'.format(','.join(args)))
        
        if len(args) == 0:
            print('Add Help -> ',
                '\n\t[type:{{{0}}}]\n\t[subtype:{{{1}}}]\n\t[description:str]\n\t[color:str]\n\t[temperature:<{2}>]\n\t[price:<$#>]'
                .format( ','.join(self.article_map.keys()), "depends on type", ','.join(self.weather)))
        
        elif len(args) == 1:
            print('Add Help -> ',
                '\n\t[type:{{{0}}}]\n\t[subtype:{{{1}}}]\n\t[description:str]\n\t[color:str]\n\t[temperature:<{2}>]\n\t[price:<$#>]'
                .format( args[0], ','.join(self.article_map[args[0]]), ','.join(self.weather)))

        else:
            article_type, article_subtype, description, colors, temp, price = self.parse_article_cli_args(args)
            article = self.wardrobe.add_article(Article(article_type, article_subtype, description, colors, temp, price))


    def handle_delete_cli(self, args):
        debug('handle_delete_cli({0})'.format(','.join(args)))

        if len(args) == 0:
            print('Delete Help -> ',
                '\n\t[type:{{{0}}}]\n\t[subtype:{{{1}}}]\n\t[description:str]\n\t[color:str]\n\t[temperature:<{2}>]\n\t[price:<$#>]'
                .format( ','.join(self.article_map.keys()), "depends on type", ','.join(self.weather)))
        
        elif len(args) == 1:
            print('Delete Help -> ',
                '\n\t[type:{{{0}}}]\n\t[subtype:{{{1}}}]\n\t[description:str]\n\t[color:str]\n\t[temperature:<{2}>]\n\t[price:<$#>]'
                .format( args[0], ','.join(self.article_map[args[0]]), ','.join(self.weather)))

        else:
            article_type, article_subtype, description, colors, temp, price = self.parse_article_cli_args(args)

            items = self.wardrobe.list_by(article_type, article_subtype, description, colors, temp, price)

            if not items:
                print("No items found")

            else:
                for article in items:
                    debug("\t{0}".format(article.summary()))

                if len(items) > 1:
                    print("{0} items selected:".format(len(items)))
                    display_articles(items)
                else:
                    self.wardrobe.remove_article(items[0])

    def handle_list_cli(self, args):
        debug('handle_list_cli({0})'.format(','.join(args)))

        if len(args) == 0:
            print('List Help -> \n\t"all" : shows all items in wardrobe\n',
                '\n\t[type:{{{0}}}]\n\t[subtype:{{{1}}}]\n\t[color:str]\n\t[temperature:<{2}>]\n\t[price:<$#>]'
                .format( ','.join(self.article_map.keys()), "depends on type", ','.join(self.weather)))
        
        if len(args) == 1 and args[0] == 'all':
            for article_type in self.article_map.keys():
                
                articles = self.wardrobe.list_by_type(article_type)
                
                if articles:
                    display_articles(articles, article_type)


        else:
            article_type, article_subtype, description, colors, temp, price = self.parse_article_cli_args(args)
            articles = self.wardrobe.list_by(article_type, article_subtype, description, colors, temp, price)

            if not articles:
                print("No items")

            for article in articles:
                print('article:',article.summary())

    def handle_generate_cli(self, args):
        debug('handle_generate_cli({0})'.format(','.join(args)))

        generation_rule, generation_selection, articles = "","",[]

        if len(args) == 0:
            print('Generate Help:'+
                '\n\tRandom\n\tPalette: [{0}]\n\tWeather: [{1}]\n\tUse: [{2}]'
                .format( '|'.join(list(self.palettes.keys())), '|'.join(self.weather), '|'.join(self.uses)))

        elif len(args) >= 1:

            criteria = {}

            for criterium in args:
                category, selection = criterium.split(':')
                criteria[category] = selection

            articles = self.generate_by_criteria(criteria)

        if articles:
            fit = Outfit(uuid.uuid4(), self.article_map, articles)
            print(fit)
            self.wardrobe.add_outfit(fit)
            return fit


    def generate_by_criteria(self, criteria={}):
        debug('generate_by_criteria ->',criteria)

        articles = { available_type:[] for available_type in self.wardrobe.data.keys()}

        for available_type in self.wardrobe.data.keys():

            available_articles = self.wardrobe.list_by(available_type)

            if available_articles:  

                # filter by uses
                available_articles = self.filter_by_use(criteria, available_articles)

                # filter by weather
                available_articles = self.filter_by_weather(criteria, available_articles)

                # filter by color palette
                available_articles = self.filter_by_color_palette(criteria, available_articles)

                if available_articles:

                    if available_type == 'accessory':      # provide multiple options for accessories

                        num_accessories = random.randrange(1,5)

                        for i in range(num_accessories):
                            random_article = random.choice(available_articles)
                            available_articles.remove(random_article)
                            articles[available_type].append(random_article)

                    else:
                        random_article = random.choice(available_articles)
                        articles[available_type].append(random_article)

        return articles

    def filter_by_use(self, criteria, articles):

        if 'use' in criteria.keys():

            return [ article for article in articles if article.article_subtype in self.uses[criteria['use']] ]

        else: # if not filtering by use, keep items
            return articles

    def filter_by_weather(self, criteria, articles):
        
        if 'weather' in criteria.keys():

            return [ article for article in articles if ('any' in article.weather or criteria['weather'] in article.weather) ]

        else:  # if not filtering by weather, keep items
            return articles


    def filter_by_color_palette(self, criteria, articles):
        
        if 'color' in criteria.keys():

            colors_for_palette = self.palettes[criteria['color']]
            neutral_colors = self.palettes['neutral']
            colors_for_palette += neutral_colors

            return [ article for article in articles if Wardrobe.article_color_in_colors(article, colors_for_palette)]

        else:  # if not filtering by weather, keep items
            return articles


    def handle_last_cli(self, args):
        debug('handle_last_cli({0})'.format(','.join(args)))
        print("Not yet implemented")

        print('options: show(default/no option), save (to wardrobe saved outfits)')

    def handle_history_cli(self, args):
        debug('handle_history_cli({0})'.format(','.join(args)))

        if args:
            if args[0] == 'clear':
                self.wardrobe.outfit_history = []
                print('cleared')
                return

        for fit in self.wardrobe.outfit_history:
            print(fit)
            print('')


    def handle_import_cli(self, args):
        debug('handle_import_cli({0})'.format(','.join(args)))

        if len(args) == 0:
            print('Import Help:'+
                '\n\tFilename: str')

        else:
            wardrobe_data_filename = args[0]

            imported = 0

            cwd = os.getcwd()
            fp = "{0}/{1}".format(cwd, wardrobe_data_filename)

            if os.path.exists(fp):

                import_data = open(fp).readlines()

                for line in import_data:
                    line = line.strip()

                    if line == "" or line.startswith('#'):
                        continue

                    multipart_token = ""
                    tokens = []
                    for t in line.split(' '):

                        if t.startswith('"') and t.endswith('"'):
                            tokens.append(t.replace('"',''))
                            continue
                        elif t.startswith('"'):
                            t = t.replace('"','')
                        elif t.endswith('"'):
                            multipart_token += t.replace('"','')
                            tokens.append(multipart_token)
                            multipart_token = ""
                            continue
                        elif multipart_token == '':
                            tokens.append(t)
                            continue

                        multipart_token += "{0} ".format(t)

                    article_type, article_subtype, description, colors, temp, price = self.parse_article_cli_args(tokens)

                    new_article = Article(article_type, article_subtype, description, colors, temp, price)

                    imported += 1
                    debug('Importing new article: ', new_article.summary())

                    self.wardrobe.add_article( new_article )


            else:
                print("No file found at [{0}]".format(fp))

            print('Imported {0} articles'.format(imported))
            



    def parse_article_cli_args(self, args):

        article_type, article_subtype, description, colors, temp, price = "","","",[],"",0

        for arg in args:
            arg = arg.strip().lower()

            # article type
            if arg in self.article_map.keys():
                article_type = arg

            # article subtype
            elif article_type and arg in self.article_map[article_type]:
                article_subtype = arg

            elif arg in self.color_map.keys():
                colors.append(arg)

            elif arg in ['hot','cold','normal','all','wet','any']:
                temp = arg

            elif '$' in arg:
                try:
                    price = int(arg.replace('$',''))
                except ValueError as ve:
                    pass

            else:
                if description:
                    description += "|"
                description += arg

        return article_type, article_subtype, description, colors, temp, price

    def menu(self):

        help_cli()
        return

    def help_cli(*args):
        print(f""" ### Wardrobe Generator CLI ### \n\t### usages ###\n{'\n'.join(WardrobeGenerator.cli_modes)}""")


    def handle_cli_transaction(self, args):

        cli_nav = {
            'add':self.handle_add_cli,
            'list':self.handle_list_cli,
            'delete':self.handle_delete_cli,
            'search':self.handle_search_cli,
            'generate':self.handle_generate_cli,
            'import':self.handle_import_cli,
            'history':self.handle_history_cli,
            'help':WardrobeGenerator.help_cli,
            'last':self.handle_last_cli
        }

        print('')
        cli_nav[args[1]](args[2:])

        '''
        try:
            cli_nav[args[1]](args[2:])
        except Exception as e:
            debug(e)
            print('Encountered an error while processing the CLI transaction')
        '''
        print('')

        self.save(pretty=PRETTY)



def debug(*msgs):
    if DEBUG:
        print('[DEBUG]',msgs);



def display_articles(articles: List[Article], msg: str=""):
    if msg:
        print("+-|{0}|{1}+".format(msg,('-'*(100-len(msg)))))

    for article in articles:
        print("\t{0}".format(article.summary()))


def robust_str_entry(prompt, options=[]):

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
                                debug(ve)
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
        except KeyboardInterrupt as ki:
            debug(ki)
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

    return Article(article_type, article_subtype, descr, colors, temp, price, uuid.uuid4())

def clear_screen():
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", end="")


def main():

    WG = WardrobeGenerator('fixed.json', 'wardrobe.json')

    WG.menu()


def is_cli_transaction( args: List[str] ) -> bool:
    
    if len(args) > 1:
        return args[1] in WardrobeGenerator.cli_modes

    return False

def handle_cli_transaction( args: List[str] ):

    WG = WardrobeGenerator('fixed.json','wardrobe.json', True)

    WG.handle_cli_transaction(args)


if __name__ == '__main__':
    if is_cli_transaction(sys.argv):
        handle_cli_transaction(sys.argv)
    else:
        print("Starting Interactive")
        main()
