from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = None

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
@app.route('/entry', methods=['POST'])
def create_entry():
	# TODO: implement me
	return 'not implemented', 500


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	# TODO: implement me
	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
