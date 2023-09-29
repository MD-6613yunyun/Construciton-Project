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

@imports.route("/<what>/<mgs>")
@imports.route("/<what>",methods=['GET','POST'])
def import_data(what,mgs=None):
    role = request.cookies.get('role')
    if not role:
        return redirect(url_for('views.home'))
    else:
        if int(role) not in (1,3,4):
            return render_template('access_error.html')
    conn = db_connect()
    cur = conn.cursor()
    data = {}
    if what == 'machine':
        cur.execute("SELECT name FROM machine_type")
        datas = cur.fetchall()
        data["Machine Type"] = datas

        cur.execute("SELECT name FROM machine_class")
        datas = cur.fetchall()
        data["Machine Class"] = datas

        cur.execute("SELECT name FROM res_company")
        datas = cur.fetchall()
        data["Business Unit"] = datas

        cur.execute("SELECT name FROM vehicle_machine_config")
        datas = cur.fetchall()
        data["Machine Capacity"] = datas

        cur.execute("SELECT name FROM fleet_vehicle_model_brand")
        datas = cur.fetchall()
        data["Machine Brand"] = datas

        cur.execute("SELECT name FROM vehicle_owner")
        datas = cur.fetchall()
        data["Owner"] = datas
        name = 'Machine Line'
    elif what == 'project':
        cur.execute("SELECT name FROM res_company;")
        data["Business Unit"] = cur.fetchall()

        cur.execute("SELECT name FROM project_group;")
        data["Project Group"] = cur.fetchall()

        cur.execute("SELECT name FROM project_type;")
        data["Project Type"] = cur.fetchall()
        name = 'Project Line'
    elif what == 'project_stat':
        cur.execute("SELECT code || ' | ' || name FROM analytic_project_code AS pj LEFT JOIN project_statistics AS stat ON pj.id = stat.project_id WHERE stat.project_id is NULL;")
        data['Project Code'] = cur.fetchall()
        cur.execute("SELECT machine_name FROM fleet_vehicle WHERE id NOT IN (SELECT id FROM machines_history WHERE end_time is NULL);")
        data['Machine'] = cur.fetchall()
        cur.execute("SELECT name FROM employee_group;")
        data['group'] = cur.fetchall()
        name = 'Project Statistics Line'
    elif what == 'project_stat_form':
        if request.method == 'POST':
            pj_id = request.form.get("project_id")
            if pj_id:
                cur.execute(""" SELECT pj.code , stat.location , stat.pj_start_date , emp_sup.name , 
                            stat.estimate_feet , stat.will_sud , stat.estimate_sud , stat.estimate_duty , 
                            stat.estimate_fuel , stat.estimate_expense , stat.estimate_day , emp_acc.name , pj.id 
                            FROM project_statistics stat INNER JOIN analytic_project_code pj ON 
                            stat.project_id = pj.id LEFT JOIN employee emp_sup ON emp_sup.id = 
                            stat.supervisor_id LEFT JOIN employee emp_acc ON emp_acc.id = stat.ho_acc_id 
                            WHERE pj.id = %s ; """,(pj_id,))
                stat_datas = cur.fetchone()
                cur.execute(""" SELECT  his.id , car.id , car.machine_name , type.name FROM machines_history his 
                            INNER JOIN fleet_vehicle car ON car.id = his.machine_id INNER JOIN machine_type 
                            type ON car.machine_type_id = type.id WHERE his.project_id = %s AND 
                            his.end_time IS NULL;""",(pj_id,))
                history_datas = cur.fetchall()
                cur.execute(""" SELECT emp.id , emp_gp.id , emp_gp.name , emp.assigned_people FROM employee_group_project 
                            emp INNER JOIN employee_group emp_gp ON emp_gp.id = emp.employee_group_id 
                            WHERE emp.project_id = %s;""",(pj_id,))
                emp_datas = cur.fetchall()
                cur.execute("SELECT code || ' | ' || name FROM analytic_project_code AS pj LEFT JOIN project_statistics AS stat ON pj.id = stat.project_id WHERE stat.project_id is NULL;")
                data['Project Code'] = cur.fetchall()
                cur.execute("SELECT code || ' | ' || name FROM analytic_project_code;")
                data['All Project Code'] = cur.fetchall()
                cur.execute("SELECT machine_name FROM fleet_vehicle WHERE id NOT IN (SELECT id FROM machines_history WHERE end_time is NULL);")
                data['Machine'] = cur.fetchall()
                cur.execute("SELECT name FROM employee_group;")
                data['group'] = cur.fetchall()
                return render_template("import_data.html",name='Project Statistics Edit',data=data,stat_datas=stat_datas,history_datas=history_datas,emp_datas=emp_datas,project_stat_edit=True,mgs=mgs)
    elif what == 'income_expense_edit_form':
        if request.method == 'POST':
            income_expense_id = request.form.get('income_expense_id')
            if income_expense_id:
                cur.execute(""" SELECT form.income_status,form.income_expense_no,form.set_date,pj.code,emp_one.name,pj.name,stat.location,stat.pj_start_date,emp_two.name
                                FROM income_expense form
                                LEFT JOIN analytic_project_code pj
                                ON form.project_id = pj.id
                                LEFT JOIN project_statistics stat
                                ON form.project_id = stat.project_id
                                LEFT JOIN employee emp_one
                                ON emp_one.id = stat.ho_acc_id
                                LEFT JOIN employee emp_two
                                ON emp_two.id = stat.supervisor_id
                                WHERE form.id = %s;""",(income_expense_id,))
                form_datas = cur.fetchone()
                cur.execute("SELECT * FROM income_expense_line WHERE income_expense_id = %s;",(income_expense_id,))
                line_datas = cur.fetchall()
            return render_template("income_expense.html",form_datas=form_datas,line_datas=line_datas,template_type = 'Edit List')
    return render_template("import_data.html",data = data,name=name,mgs=mgs)

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
    return redirect(url_for('views.configurations',what='details',mgs=mgs))
    
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
    mgs = None
    if request.method == 'POST':
        db = request.form.get("db")
        print(db)
        conn = db_connect()
        cur = conn.cursor()
        query = ""
        if db == 'analytic_project_code':
            pj_datas = request.form.getlist('pj-datas')
            cur.execute("SELECT id FROM res_company where name = %s",(pj_datas[-1],))
            bi_id = cur.fetchall()
            if not bi_id:
                return redirect(url_for('views.configurations',what='project',mgs="Invalid Business Unit Name"))
            query = f""" INSERT INTO {db} (code,name,pj_group,type,business_unit_id) VALUES ({",".join(["'{}'".format(item) for item in pj_datas[:-1]])},'{bi_id[0][0]}');"""
            what = 'project'
        elif db == 'duty_odoo_report':
            dty_datas = request.form.getlist('duty-datas')
            print(dty_datas)
        elif db == 'fleet_vehicle':
            vehicle_datas = request.form.getlist('vehicle-datas')
            tables_list = ['machine_type','machine_class','vehicle_machine_config','fleet_vehicle_model_brand','res_company','vehicle_owner']
            inserted_values = [vehicle_datas[0]]
            for idx,table_name in enumerate(tables_list,start=1):
                idd = get_id_from_table(cur,table_name,vehicle_datas[idx])
                if not idd:
                    return redirect(url_for('views.configurations',what='machine',mgs=f"Invalid {change_db_to_field_name(table_name)}"))
                else:
                    inserted_values.append(idd)
            query = f""" INSERT INTO {db} (machine_name,machine_type_id,machine_class_id,machine_config_id,brand_id,business_unit_id,owner_name_id) VALUES {tuple(inserted_values)};"""
            what = 'machine'
        elif db == 'project_stats':
            pj_id = request.form.get('pj_id')
            loc = request.form.get('location')
            start_date = request.form.get('pj-start-date')
            supervisior = request.form.get('supervisior')
            feet = request.form.get('feet')
            will_sud = request.form.get('will-sud')
            sud = request.form.get('sud')
            duty = request.form.get('duty')
            fuel = request.form.get('fuel')
            expense = request.form.get('expense')
            estimate_day = request.form.get('estimate_day')
            acc = request.form.get('hoAccount')
            
            machine_ids = request.form.getlist("machine_id")
            employee_group_ids = request.form.getlist("employee_group_id")
            employee_powers = request.form.getlist("employee_power")

            what = 'project-stat'

            try:
                cur.execute("""INSERT INTO project_statistics(project_id,supervisor_id,estimate_feet,
                            will_sud,estimate_sud,estimate_duty,estimate_fuel,estimate_expense,
                            estimate_day,location,pj_start_date,ho_acc_id) VALUES 
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",(pj_id,supervisior,feet,will_sud,sud,duty,fuel,expense,estimate_day,loc,start_date,acc))
                if machine_ids != []:
                    for machine_id in machine_ids:
                        cur.execute("INSERT INTO machines_history (project_id,machine_id) VALUES (%s,%s);",(pj_id,machine_id))
                if employee_group_ids != [] and employee_powers != []:
                    for data in zip(employee_group_ids,employee_powers):
                        cur.execute("INSERT INTO employee_group_project (project_id,employee_group_id,assigned_people) VALUES (%s,%s,%s);",(pj_id,data[0],data[1]))
                conn.commit()
            except IntegrityError as err:
                mgs = str(err).title()
                conn.rollback()
        elif db == 'project_stats_edit':
            input_values = {}
            for key,value in request.form.items():
                if key not in ('db','project_id','machine_id','employee_group_id','employee_power'):
                    input_values[key] = value
            update_query = "UPDATE project_statistics SET "
            for column_name in input_values.keys():
                update_query += f"{column_name} = %s, "
            pj_id = request.form.get("project_id")
            machine_ids = request.form.getlist("machine_id")
            employee_group_ids = request.form.getlist("employee_group_id")
            employee_powers = request.form.getlist("employee_power")
            update_query = update_query[:-2] + f" WHERE project_id = {pj_id};"
            what = 'project-stat'
            try:
                cur.execute(update_query,list(input_values.values()))
                if machine_ids != []:
                    for machine_id in machine_ids:
                        cur.execute("INSERT INTO machines_history (project_id,machine_id) VALUES (%s,%s);",(pj_id,machine_id))
                if employee_group_ids != [] and employee_powers != []:
                    for data in zip(employee_group_ids,employee_powers):
                        cur.execute("INSERT INTO employee_group_project (project_id,employee_group_id,assigned_people) VALUES (%s,%s,%s);",(pj_id,data[0],data[1]))
                conn.commit()
            except IntegrityError as err:
                mgs = str(err).title()
                conn.rollback()
            
        if query != "":
            try:
                cur.execute(query)
                conn.commit()
            except IntegrityError as err:
                mgs = str(err).title()
                conn.rollback()
    return redirect(url_for('views.configurations',what=what,mgs=mgs))

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

@imports.route("/site-imports/<typ>",methods=['POST'])
def site_imports(typ):
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()
        if typ == 'income-expense':
            income_expense = request.form.get("work")
            income_status = True if  income_expense == 'incomes' else False
            if income_status:
                cur.execute("SELECT 'DCI/' || RIGHT(EXTRACT(YEAR FROM NOW())::TEXT,2) || '/' || TO_CHAR(EXTRACT(MONTH FROM NOW()),'FM00') || '/' || COALESCE((SELECT TO_CHAR(id + 1, 'FM000000') FROM income_expense WHERE income_status = TRUE ORDER BY id DESC LIMIT 1),'000001');")
            else:
                cur.execute("SELECT 'DCO/' || RIGHT(EXTRACT(YEAR FROM NOW())::TEXT,2) || '/' || TO_CHAR(EXTRACT(MONTH FROM NOW()),'FM00') || '/' || COALESCE((SELECT TO_CHAR(id + 1, 'FM000000') FROM income_expense WHERE income_status = FALSE ORDER BY id DESC LIMIT 1),'000001');")
            report_no = cur.fetchone()[0]
            import_date = request.form.get("import_date")
            pj_id = request.form.get("pj_id")
            cur.execute("INSERT INTO income_expense (income_status,income_expense_no,set_date,project_id) VALUES (%s,%s,%s,%s) RETURNING id;",(income_status,report_no,import_date,pj_id))
            income_expense_id = cur.fetchone()[0]
            descriptions = request.form.getlist("description")[:-1]
            invoice_nos = request.form.getlist("invoice_no")[:-1]
            qtys = request.form.getlist("qty")[:-1]
            prices = request.form.getlist("price")[:-1]
            amts = request.form.getlist("amt")[:-1]
            remarks = request.form.getlist("remark")[:-1]
            query = "INSERT INTO income_expense_line (income_expense_id,description,invoice_no,qty,price,amt,remark) VALUES "
            for data in zip(descriptions,invoice_nos,qtys,prices,amts,remarks):
                query += f"('{income_expense_id}','{data[0]}','{data[1]}','{data[2] if data[2] != '' else 0.0}','{data[3] if data[3] != '' else 0.0}','{data[4]}','{data[5]}'),"
            cur.execute(query[:-1]+';')
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("site_imports.income_expense",typ='view'))
        elif typ == 'daily-activity':
            work_not_work = request.form.get("work")
            work_staus = True if work_not_work == 'working' else False
            reason_for_not_working = request.form.get("reason-for-not-working")
            pj_id = request.form.get("pj_id")
            set_date = request.form.get('set_date')
            wealther_affect = request.form.get("wealtherAff")
            complete_feet = request.form.get("completeFeet")
            complete_sud = request.form.get("completeSud")
            cur.execute("SELECT 'DCA/' || RIGHT(EXTRACT(YEAR FROM NOW())::TEXT,2) || '/' || TO_CHAR(EXTRACT(MONTH FROM NOW()),'FM00') || '/' || COALESCE((SELECT TO_CHAR(id + 1, 'FM000000') FROM daily_activity ORDER BY id DESC LIMIT 1),'000001');")
            report_no = cur.fetchone()[0]
            cur.execute("INSERT INTO daily_activity (daily_activity_no,working_status,remark_for_not_working,set_date,project_id,wealther_effect_percent,complete_feet,complete_sud) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);",(report_no,work_staus,reason_for_not_working,set_date,pj_id,wealther_affect,complete_feet,complete_sud))

    else:
        return redirect(url_for("views.home"))

@imports.route("/daily-acitvity")
def daily_activities_report():
    return render_template("daily-table.html")
