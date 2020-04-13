from flask import Flask, jsonify, json, request
import requests
import requests_cache

requests_cache.install_cache('hearthstone_api_cache', backend= 'sqlite', expire_after=36000)

with open('cards.json') as f:
	cards_dict = json.load(f)

app = Flask(__name__)

@app.route('/')
def info():
	return('<h1>Welcome to the hearthstone!</h1>')

@app.route('/cards', methods=['GET'])
def all_cards():
	return jsonify(cards_dict)

@app.route('/cards/<cardname>', methods=['GET'])
def get_cards_by_name(cardname):
	cards = [card for card in cards_dict if card['name'] == cardname]
	if len(cards) == 0:
		return jsonify({'error':'card name not found.'}), 404
	else:
		response = [cards[0]]
		return jsonify(response), 200

@app.route('/cards/classes/<cardclass>', methods=['GET'])
def get_cards_by_class(cardclass):
	classes = [card for card in cards_dict if 'cardClass' in card]
	if len(classes) == 0:
		return jsonify({'error':'no such class.'}), 404
	else:
		cards_by_class = [card for card in classes if card['cardClass'] == cardclass] 
		response = cards_by_class
		return jsonify(response), 200

@app.route('/cards', methods=['POST'])
def create_a_card():
	if not request.json or not 'name' in request.json:
		return jsonify({'error':'the new card needs to have a name.'}), 400
	new_card = {'attack':request.json['attack'], 'cardClass':request.json['cardClass'], 'name':request.json['name']}
	cards_dict.append(new_card)
	return jsonify({'message':'created:/cards/{}'.format(new_card['name'])}), 201

@app.route('/cards/<cardname>', methods=['DELETE'])
def delete_a_card(cardname):
	matched_cards = [card for card in cards_dict if card['name'] == cardname]
	if len(matched_cards) == 0:
		return jsonify({'error':'card name not found, delete failed.'}), 404
	cards_dict.remove(matched_cards[0])
	return jsonify({'success':True})

@app.route('/cards/<cardname>', methods=['PUT'])
def update_a_card_text(cardname):
	matched_card = [card for card in cards_dict if card['name'] == cardname]
	if len(matched_card) == 0:
		return jsonify({'error':'card not found, update failed.'}), 404
	for card in matched_card:
		if 'text' in card:
			card['text'] = request.json['text']
		else:
			return jsonify({'error':'no text info in this card, please update another one.'}), 404
		return jsonify({'name':'updates:/cards/{}'.format(matched_card[0]['name'])})

url_api = 'https://omgvamp-hearthstone-v1.p.rapidapi.com/cards'
headers = {'x-rapidapi-host': "omgvamp-hearthstone-v1.p.rapidapi.com",'x-rapidapi-key': "74eccf35camshe4b862bb55691b5p15559ajsnd6e42908471e"}
response = requests.request("GET", url_api, headers=headers)
cards_api = response.json()

cards_api_value = []
for key in cards_api.keys():
	cards_api_value.append(cards_api[key])

info = []
for i in range(len(cards_api_value)):
	for j in range(len(cards_api_value[i])):
		info.append(cards_api_value[i][j])

unique_set = []
for i in info:
	if i['cardSet'] not in unique_set:
		unique_set.append(i['cardSet'])

url_set = 'https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/sets/{}'
@app.route('/cards/sets/<set>', methods=['GET'])
def get_cards_by_set(set):
	matched_set = [i for i in unique_set if i == set]
	if len(matched_set) == 0:
		return jsonify({'error':'no such set.'}), 404
	else:
		attr = matched_set[0]
		r = requests.request("GET",url_set.format(attr),headers=headers)
		resp = r.json()
		return jsonify(resp), 200


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=80)
