import datetime

from flask import Blueprint
from flask import render_template, request, redirect, url_for, jsonify
from flask import g
from flask.wrappers import Request

from . import db

bp = Blueprint("pets", "pets", url_prefix="")

def format_date(d):
    if d:
        d = datetime.datetime.strptime(d, '%Y-%m-%d')
        v = d.strftime("%a - %b %d, %Y")
        return v
    else:
        return None

@bp.route("/search/<field>/<value>")
def search(field, value):
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id")
    order = request.args.get("order", "asc")
    if field=="tag":
        if order == "asc":
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id and p.id in (select pet from tags_pets where tag in (select id from tag where name=?)) order by p.id",[value])
        else:
            cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id and p.id in (select pet from tags_pets where tag in (select id from tag where name=?)) order by p.id desc",[value])
    pets = cursor.fetchall()
    return render_template('search.html', pets = pets, order="desc" if order=="asc" else "asc")

@bp.route("/")
def dashboard():
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id")
    order = request.args.get("order", "asc")
    if order == "asc":
        cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.{oby}")
    else:
        cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.{oby} desc")
    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order="desc" if order=="asc" else "asc")


@bp.route("/<pid>")
def pet_info(pid): 
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
    pet = cursor.fetchone()
    cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
    tags = (x[0] for x in cursor.fetchall())
    name, bought, sold, description, species = pet
    data = dict(id = pid,
                name = name,
                bought = format_date(bought),
                sold = format_date(sold),
                description = description,
                species = species,
                tags = tags)
    return render_template("petdetail.html", **data)

@bp.route("/<pid>/edit", methods=["GET", "POST"])
def edit(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
        pet = cursor.fetchone()
        cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
        tags = (x[0] for x in cursor.fetchall())
        name, bought, sold, description, species = pet
        data = dict(id = pid,
                    name = name,
                    bought = format_date(bought),
                    sold = format_date(sold),
                    description = description,
                    species = species,
                    tags = tags)
        return render_template("editpet.html", **data)
    elif request.method == "POST":
    	description = request.form.get('description')
    	sold = request.form.get("sold")
    	print(sold)
    	if not (sold and description):
    		resp=request.get_json(force=True)
    		print(resp)
    		if "sold" in resp.keys():
    			sold=resp['sold']
    			if sold=="on" or sold=='1':
    				cursor.execute(f"update pet set sold=?,bought=? where id = ?", [str(datetime.date.today()),str(datetime.date.today()),pid])
    				conn.commit()
    		elif "description" in resp.keys():
    			description=resp['description']
    			cursor.execute("update pet set description=? where id=?",[description, pid])
    			conn.commit()
    	elif (sold and description):
    		if (sold=="on"):
    			cursor.execute(f"update pet set sold=?,bought=? where id = ?", [str(datetime.date.today()),str(datetime.date.today()),pid])
    			conn.commit()
    		cursor.execute("update pet set description=? where id=?",[description, pid])
    		conn.commit()
    	elif sold=="on":
    		cursor.execute(f"update pet set sold=?,bought=? where id = ?", [str(datetime.date.today()),str(datetime.date.today()),pid])
    		conn.commit()
    	elif description:
    		cursor.execute("update pet set description=? where id=?",[description, pid])
    		conn.commit()
    	return redirect(url_for("pets.pet_info", pid=pid), 302)
        
    



