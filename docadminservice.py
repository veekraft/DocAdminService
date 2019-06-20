#!flask/bin/python
import os, pymongo
import models
from flask import Flask, jsonify, abort, request, make_response, url_for
    
app = Flask(__name__)

# Error Handler for 400: Bad Request
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

# Error Handler for 404: Not Found 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)
    
# Service Call for retrieving list of documents
@app.route('/api/v1.0/documents', methods = ['GET'])
def get_documents():
    documents = models.get_documents()
    return jsonify( { 'documents': documents } ), 201

# Service Call for retrieving a single document's details using mongo unique index id
@app.route('/api/v1.0/doco/<string:d_id>', methods = ['GET'])
def get_doco(d_id):
    doco = models.get_doco(d_id)

    if not doco:
        # No dog with that id found
        abort(404)

    return jsonify( { 'doco': doco })

# Service Call for creating a new document
@app.route('/api/v1.0/doco', methods = ['POST'])
def create_doco():
    # Check for JSON input, plus:
    # Mandatory document name, doc_id must be unique
    if not request.json or not 'name' in request.json:
        abort(400)
    doco = {
        'doc_id': str(request.json['doc_id']).strip().lower(),
        'doco_type': str(request.json['doco_type']).strip().upper(),
        'name': str(request.json['name']).strip().capitalize(),
        'status': request.json.get('status', "").strip().upper(),
        'handler_id': request.json.get('handler_id', None).strip().lower(),
        'dog_id': str(request.json.get('dog_id', "")).strip().lower()
    }
    id = models.new_doco(doco)
    doco['id'] = id

    return jsonify( { 'doco': doco } ), 201

# Service Call for updating a document
@app.route('/api/v1.0/doco/<string:d_id>', methods = ['PUT'])
def update_doco(d_id):
    doco = models.get_doco(d_id)
    if len(doco) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) is not unicode:
        abort(400)
    if 'status' in request.json and type(request.json['status']) is not unicode:
        abort(400)
    if 'doc_id' in request.json and type(request.json['doc_id']) is not unicode:
        abort(400)
    if 'doco_type' in request.json and type(request.json['doco_type']) is not unicode:
        abort(400)
    if 'handler_id' in request.json and type(request.json['handler_id']) is not unicode:
        abort(400)
    if 'dog_id' in request.json and type(request.json['dog_id']) is not unicode:
        abort(400)
    doco['name'] = str(request.json.get('name', doco['name'])).strip().capitalize()
    doco['doc_id'] = str(request.json.get('doc_id', doco['doc_id'])).strip().lower()
    doco['doco_type'] = str(request.json.get('doco_type', doco['doco_type'])).strip().upper()
    doco['status'] = str(request.json.get('status', doco['status'])).strip().upper()
    doco['handler_id'] = str(request.json.get('handler_id', doco['handler_id'])).strip().lower()
    doco['dog_id'] = str(request.json.get('dog_id', doco['dog_id'])).strip().lower()
    models.update_doco(doco)

    return jsonify( { 'doco': doco } )

### Service Call for deleting a document
##@app.route('/api/v1.0/doco/<string:d_id>', methods = ['DELETE'])
##def delete_doco(d_id):
##    doco = models.get_doco(d_id)
##    if doco is None:
##        abort(404)
##    models.delete_doco(d_id)
##    return jsonify( { 'result': True } )

# Service Call for search by criteria (similar to Update Handler method)
# Accepts a single field or multiple fields which are then AND'ed
@app.route('/api/v1.0/search', methods = ['PUT'])
def search():
    if not request.json:
        abort(400)

    criteria = {}

    if 'doc_id' in request.json:
        doc_id = str(request.json['doc_id']).strip().lower()
        criteria['doc_id'] = doc_id

    if 'doco_type' in request.json:
        doco_type = str(request.json['doco_type']).strip().upper()
        criteria['doco_type'] = doco_type

    if 'name' in request.json:
        name = str(request.json['name']).strip().capitalize()
        criteria['name'] = name

    if 'handler_id' in request.json:
        handler_id = request.json['handler_id']
        if not (handler_id is None):
            str(handler_id).strip().lower()
        criteria['handler_id'] = handler_id

    if 'dog_id' in request.json:
        dog_id = request.json['dog_id']
        if not (dog_id is None):
            str(dog_id).strip().lower()
        criteria['dog_id'] = dog_id
        
    if 'status' in request.json:
        status = str(request.json['status']).strip().upper()
        criteria['status'] = status        

    documents = models.search(criteria)
    return jsonify( {'documents': documents} )

# Initialise DB before starting web service
models.init_db()
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', '5050')), threaded=True)
