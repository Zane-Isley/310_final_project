from flask import Flask, render_template, request
import urllib.parse, urllib.request, urllib.error, json
import keys
import random
import html

app = Flask(__name__)

baseurl = "https://www.thecocktaildb.com/api/json/v1/" + keys.API_KEY + "/"

@app.route("/", methods=['POST', 'GET'])
def hello_world():
    return render_template('index.html')


@app.route("/drink/<liqour>", methods=['POST'])
def get_drink(liqour):
    if (liqour == "None"):
        spirit = request.form.get('spirits')
        ingredient_list = request.form.getlist('ingredients')
    else:
        spirit = html.unescape(liqour)

    ingredient_list = [ingredient.upper() for ingredient in ingredient_list]
    potential_drink = get_drink_from_spirit(spirit, ingredient_list)

    if potential_drink is None:
        return render_template('index.html', error=True)
    return render_template('index.html', potential_drink=potential_drink)


@app.route("/recipe/<cocktail>", methods=['POST'])
def recipe(cocktail):
    recipe = get_recipe(cocktail)

    if not recipe:
        return "<h1> Oops we cannot find a recipe for that, try again! </h1>"
    ingredient_csv = ""
    for ingredient in get_ingredients(cocktail=cocktail):
        ingredient_csv += ingredient + ","
    ingredient_csv = ingredient_csv[:-1]
    return render_template('index.html', recipe=recipe, ingredients=ingredient_csv)


def get_recipe(cocktail):
    drink_array = make_api_call(cocktail, "/search.php?s=")
    recipe = "Woops! Looks like there isn't a recipe for this beverage..."
    if drink_array is None:
        return None
    for drink in drink_array['drinks']:
        if drink["strDrink"].lower() == cocktail.lower():
            recipe = drink["strInstructions"]
    return recipe


def user_to_apiFormatting(cocktail):
    return cocktail.strip().replace(" ", "_").lower()


def make_api_call(cocktail, extension):
    # Make API call
    cocktail = user_to_apiFormatting(cocktail)
    new_url = baseurl + extension + user_to_apiFormatting(cocktail)

    cocktail_response_str = ""
    try:
        with urllib.request.urlopen(new_url) as response:
            cocktail_response_str = response.read()
    except urllib.error.HTTPError as e:
        return None

    # loads json
    return json.loads(cocktail_response_str)


def get_drink_from_spirit(cocktail, user_ingredients):
    list_of_drinks = make_api_call(cocktail, "/filter.php?i=")["drinks"]
    if list_of_drinks is None:
        return None
    suggested_drink = random.choice(list_of_drinks)
    return suggested_drink


def get_ingredients(drink_id):
    ingredients = []

    i = 1
    while True:
        ingredient = make_api_call(drink_id, "/lookup.php?i=")['drinks'][0]['strIngredient' + str(i)]
        if ingredient is None:
            break
        ingredients.append(ingredient.upper())
        i = i + 1
        if i == 15:
            break

    return ingredients

def get_ingredients(cocktail):
    ingredients = []

    i = 1
    while True:
        ingredient = make_api_call(cocktail, "/search.php?s=")['drinks'][0]['strIngredient'+str(i)]
        if ingredient is None:
            break
        ingredients.append(ingredient.upper())
        i = i + 1
        if i == 15:
            break
    return ingredients

# to run, enter this in terminal: flask --app final-project run
