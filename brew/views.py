from flask import request, render_template, jsonify, redirect
from bson.objectid import ObjectId
from brew import app, mongo, controller, machine


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    return render_template('index.html', recipes=recipes, machine=machine)


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    if request.method == 'POST':
        mongo.db.recipes.insert(request.get_json())

    return render_template('create.html')


@app.route('/brews/prepare/<recipe_id>', methods=['GET'])
def prepare(recipe_id):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    return render_template('prepare.html', recipe=recipe)


@app.route('/brews', methods=['POST'])
def brew():
    recipe_id = request.form['recipe_id']
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))

    mash = []

    for step in recipe['mash']:
        mash.append(dict(name=step['name'],
                         time=step['time'],
                         temperature=step['temperature'],
                         state='waiting'))

    mash[0]['state'] = 'pending'

    machine.fsm.heat(temperature=mash[0]['temperature'])
    return render_template('brew.html', mash=mash, machine=machine)


@app.route('/brews/stop')
def stop_brew():
    machine.stop()
    controller.set_temperature(20.0)
    return redirect('/')


@app.route('/status/temperature', methods=['GET'])
def temperature():
    return jsonify(temperature=controller.get_temperature())
