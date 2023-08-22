from flask import Blueprint,render_template,request,redirect,url_for,jsonify
from website import db_connect,catch_db_insert_error
from psycopg2 import IntegrityError

imports = Blueprint("imports",__name__)

data_tables = {"Machine Type":"machine_type","Machine Class":"machine_class","Business Unit":"res_company","Machine Capacity":"vehicle_machine_config","Machine Brand":"fleet_vehicle_model_brand","Owner":"vehicle_owner"}


def change_db_to_field_name(text):
    return " ".join(name.capitalize() for name in text.split("_"))

def get_id_from_table(cur, table_name,value):
    cur.execute(f"SELECT id FROM {table_name} WHERE name = %s", (value,))
    idd = cur.fetchone()
    return idd[0] if idd else None

@imports.route("/<mgs>")
@imports.route("")
def form_view(mgs=None):
    role = request.cookies.get('role')
    if not role:
        return redirect(url_for('views.home'))
    else:
        if int(role) not in (1,3,4):
            return render_template('access_error.html')
    conn = db_connect()
    cur = conn.cursor()
    data = {}

    cur.execute("SELECT id,name FROM machine_type")
    datas = cur.fetchall()
    data["Machine Type"] = datas

    cur.execute("SELECT id,name FROM machine_class")
    datas = cur.fetchall()
    data["Machine Class"] = datas

    cur.execute("SELECT id,name FROM res_company")
    datas = cur.fetchall()
    data["Business Unit"] = datas

    cur.execute("SELECT id,name FROM vehicle_machine_config")
    datas = cur.fetchall()
    data["Machine Capacity"] = datas

    cur.execute("SELECT id,name FROM fleet_vehicle_model_brand")
    datas = cur.fetchall()
    data["Machine Brand"] = datas

    cur.execute("SELECT id,name FROM vehicle_owner")
    datas = cur.fetchall()
    data["Owner"] = datas

    return render_template("import_data.html",data = data,mgs=mgs)

@imports.route("/upload-each-machine-details",methods=['GET','POST'])
def upload_each():
    mgs = None
    if request.method == 'POST':
        tb = request.form.get("table")
        data = request.form.get("data")
        conn = db_connect()
        cur = conn.cursor()
        insert_query = 'INSERT INTO "{table}" (name) VALUES (%s)'.format(table=data_tables[tb])
        try:
            cur.execute(insert_query,(data.strip(),))
            conn.commit()
        except IntegrityError as e:
            print(e)
            mgs = str(e).title()
        cur.close()
        conn.close()
    return redirect(url_for('imports.form_view',mgs=mgs))
    
@imports.route("/update-each-machine-details/<table>/<idd>/<val>")
def update_machine_details(table,idd,val):
    mgs = None
    conn = db_connect()
    cur = conn.cursor()
    query = f"UPDATE {data_tables[table]} SET name = '{val}' WHERE id = {idd};"
    mgs = catch_db_insert_error(cur,conn,[query]) 
    return "Finished" if not mgs else mgs

@imports.route("/upload",methods=['GET','POST'])
def upload_each_data():
    if request.method == 'POST':
        db = request.form.get("db")
        print(db)
        conn = db_connect()
        cur = conn.cursor()
        query = ""
        if db == 'analytic_project_code':
            pj_datas = request.form.getlist('pj-datas')
            print(",".join(pj_datas))
            cur.execute("SELECT id FROM res_company where name = %s",(pj_datas[-1],))
            bi_id = cur.fetchall()
            if not bi_id:
                return redirect(url_for('imports.form_view',mgs="Invalid Business Unit Name"))
            query = f""" INSERT INTO {db} (code,name,pj_group,type,business_unit_id) VALUES ({",".join(["'{}'".format(item) for item in pj_datas[:-1]])},'{bi_id[0][0]}');"""
        elif db == 'duty_odoo_report':
            dty_datas = request.form.getlist('duty-datass')
            print(dty_datas)
        elif db == 'fleet_vehicle':
            vehicle_datas = request.form.getlist('vehicle-datas')
            tables_list = ['machine_type','machine_class','vehicle_machine_config','fleet_vehicle_model_brand','res_company','vehicle_owner']
            inserted_values = [vehicle_datas[0]]
            for idx,table_name in enumerate(tables_list,start=1):
                idd = get_id_from_table(cur,table_name,vehicle_datas[idx])
                if not idd:
                    return redirect(url_for('imports.form_view',mgs=f"Invalid {change_db_to_field_name(table_name)}"))
                else:
                    inserted_values.append(idd)
            query = f""" INSERT INTO {db} (machine_name,machine_type_id,machine_class_id,machine_config_id,brand_id,business_unit_id,owner_name_id) VALUES {tuple(inserted_values)};"""
        if query != "":
            try:
                cur.execute(query)
                conn.commit()
            except IntegrityError as err:
                print(err)
                conn.rollback()
    return redirect(url_for('imports.form_view'))

@imports.route("/return-dropdown-data/<mgs>",methods=['GET','POST'])
def return_dropdown_data(mgs):
    table_list = mgs.split(",")
    conn = db_connect()
    cur = conn.cursor()
    result = []
    for table_name in table_list:
        try:
            cur.execute(f"SELECT id,name FROM {table_name};")
            result.append(cur.fetchall())
        except IntegrityError as err:
            print(err)
    return jsonify(result)

@imports.route("/upload-each-duty",methods=['GET','POST'])
def upload_each_duty():
    if request.method == 'POST':
        all_duty_datas = request.form.getlist('duty-datas')
        print(all_duty_datas)

    return redirect(url_for('imports.form_view'))

@imports.route("duty-line")
def duty_line():
    print("nani")
    return render_template("duty_line_import.html")

# pj-code
# pj-name
# duty-date
# machine-name
# operator-name
# morn-st
# morn-ed
# noon-st
# noon-ed
# even-st
# even-ed
# total-hr
# par-per-duty
# duty-cost
# total-fuel
# pay-per-litre
# fuel-cost
# total-cost
# way
# com-feet
# com-sud