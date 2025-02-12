from typing import List, Dict, Union, Literal, Any
from flask import Flask, request, jsonify
import re

from pydantic import RootModel, BaseModel, Field, ValidationError, model_validator
from collections import Counter
from sys import stderr

# ==== Type Definitions, feel free to add or modify ===========================

# all entries have a name
class BaseEntry(BaseModel):
	name: str

class Ingredient(BaseEntry):
	type: Literal['ingredient']
	cook_time: int = Field(ge=0, alias='cookTime')
		
class RequiredItem(BaseModel):
	name: str
	quantity: int = Field(gt=0)

class Recipe(BaseEntry):
	type: Literal['recipe']
	required_items: List[RequiredItem] = Field(alias='requiredItems', min_length=1)

	@model_validator(mode='after')
	def validate_required_items(self):
		seen: set[str] = set()
		for item in self.required_items:
			if item.name == self.name:
				raise ValueError("A requiredItem cannot be the recipe itself")
			
			if item.name in seen:
				raise ValueError("Cannot have two or more requiredItems with the same name")
			
			seen.add(item.name)

		return self


# Ingredient, Recipe tagged union by discriminating on `type`
CookbookEntry = RootModel[Union[Ingredient, Recipe]]


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook: Dict[str, CookbookEntry] = {}

# Helpful in testing...
@app.route('/clear', methods=['DELETE'])
def clear_cookbook():
	cookbook.clear()
	return "", 200

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and formats it
def parse_handwriting(recipeName: str) -> Union[str, None]:
	""" Formats a given `recipeName`:
		- Whitespace: '-' and '_' replaced by space ' '
		- Malformed: exclude chars not in [a-zA-Z ]
		- Capitalisation: the first letter of each word is capitalised and the rest in lowercase
		- Shrinking: of multiple whitespaces between words to one space
		- Stripping: of leading and trailing whitespace

		Output: sanitised string if length is non-zero, otherwise None
	"""
	# remove non letter or space characters
	filter_illegal = "".join(char for char in recipeName if char.isalpha() or char in '_- ')

	# squash multiple "whitespace" characters, and remove any leading and/or trailing whitespace
	handle_whitespaces = re.sub('[-_ ]+', ' ', filter_illegal).strip()
	capitalised = " ".join(word.capitalize() for word in handle_whitespaces.split())

	if capitalised:
		return capitalised
	return None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
# Requirements:
# - type can only be "recipe" or "ingredient".
# - cookTime can only be greater than or equal to 0
# - entry names must be unique
# - Recipe requiredItems can only have one element per name.

@app.route('/entry', methods=['POST'])
def create_entry():
	entry_json = request.get_json()

	# handle uniqueness of entry names
	if entry_json["name"] in cookbook:
		return "", 400

	try:
		# parse entry_json as a CookbookEntry
		entry = CookbookEntry(**entry_json)
		cookbook[entry_json["name"]] = entry
		return "", 200
	except ValidationError as e:
		print(e, file=stderr)
		return "", 400


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	name = request.args.get('name')

	if name not in cookbook:
		return f'recipe of {name} not found in cookbook', 400
	
	
	entry = cookbook[name].root
	if entry.type == "ingredient":
		return f'{name} is an ingredient and not a recipe', 400
	
	summary: Dict[str, Any] = {
		"name": name,
		"cookTime": 0,
		"ingredients": []
	}

	# map of entry names (ingredients ONLY) to their count
	ingredients: Counter[str] = Counter()

	# assuming that an eventual requiredItem of a recipe is not the recipe itself
	def dfs(entry: Recipe, multiplier: int):
		for req_item in entry.required_items:
			if (req_name := req_item.name) not in cookbook:
				raise ValueError(f'required item {req_name} not found in cookbook')
			
			req_entry = cookbook[req_name].root
			if (req_entry.type) == "ingredient":
				ingredients[req_name] += multiplier * req_item.quantity
				summary["cookTime"] += multiplier * req_item.quantity * req_entry.cook_time

			else:
				dfs(req_entry, multiplier * req_item.quantity)

	try:
		dfs(entry, 1)
		for ingredient, count in ingredients.items():
			summary['ingredients'].append({
				"name": ingredient,
				"quantity": count
			})

		return summary, 200
	except ValueError as e:
		return str(e), 400


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
