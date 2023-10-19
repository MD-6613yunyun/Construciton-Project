from flask import Blueprint,render_template,request,redirect,url_for,jsonify
from website import db_connect,catch_db_insert_error
from psycopg2 import IntegrityError
from itertools import zip_longest
from decimal import Decimal

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
    role = request.cookies.get('cpu_role')
    user_id = request.cookies.get('cpu_user_id')
    if not role:
        return redirect(url_for('views.home'))
    else:
        if int(role) not in (1,3,4,5):
            return render_template('access_error.html')
    conn = db_connect()
    cur = conn.cursor()
    data = {}
    if request.method == 'POST':
        if what == 'project_stat_form':
            pj_id = request.form.get("project_id")
            if pj_id:
                cur.execute(""" SELECT pj.code , stat.location , stat.pj_start_date , emp_sup.name , 
                            stat.estimate_feet , stat.will_sud , stat.estimate_sud , stat.estimate_duty , 
                            stat.estimate_fuel , stat.estimate_expense , stat.estimate_day , emp_acc.name ,
                            pj.id , emp_sup.id , emp_acc.id , status.name
                            FROM project_statistics stat 
                            INNER JOIN analytic_project_code pj ON stat.project_id = pj.id 
                            LEFT JOIN employee emp_sup ON emp_sup.id = stat.supervisor_id 
                            LEFT JOIN employee emp_acc ON emp_acc.id = stat.ho_acc_id 
                            LEFT JOIN project_status status ON status.id = pj.project_status_id
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
                cur.execute("SELECT machine_name FROM fleet_vehicle WHERE id IN (SELECT machine_id FROM machines_history WHERE end_time is NULL AND project_id = 1669);")
                data['Machine'] = cur.fetchall()
                cur.execute("SELECT name FROM employee_group;")
                data['group'] = cur.fetchall()
                cur.execute("SELECT emp.id,emp.name FROM employee emp INNER JOIN employee_group emp_gp ON emp.employee_group_id = emp_gp.id WHERE emp_gp.name = 'ACCOUNTANT';")
                data['accountants'] = cur.fetchall()
                cur.execute("SELECT id,name FROM employee;")        
                data['supervisors'] = cur.fetchall()
                return render_template("import_data.html",name='Project Statistics Edit',data=data,stat_datas=stat_datas,history_datas=history_datas,emp_datas=emp_datas,project_stat_edit=True,mgs=mgs)
        elif what == 'income_expense_edit_form':
            income_expense_id = request.form.get('income_expense_id')
            if income_expense_id:
                cur.execute(""" SELECT form.income_status,form.income_expense_no,form.set_date,pj.code,emp_one.name,pj.name,stat.location,stat.pj_start_date,emp_two.name,form.id,pj.id
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
                cur.execute("SELECT line.id,income_expense_id,description,invoice_no,qty,price,amt,remark,COALESCE(car.machine_name,'') FROM income_expense_line AS line LEFT JOIN fleet_vehicle AS car ON line.machine_id = car.id WHERE income_expense_id = %s;",(income_expense_id,))
                line_datas = cur.fetchall()
                cur.execute("SELECT car.machine_name,car.id FROM machines_history LEFT JOIN fleet_vehicle AS car ON car.id = machines_history.machine_id WHERE project_id = %s AND end_time IS NULL;",(form_datas[10],))
                machine_datas = cur.fetchall()
                if role in ('3','4'):
                    cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
                else:
                    cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
                project_datas = cur.fetchall()
            return render_template("income_expense.html",form_datas=form_datas,line_datas=line_datas,machine_datas=machine_datas,template_type = 'Edit List',project_datas = project_datas)
        elif what == 'daily_activity_edit_form':
            daily_activity_id =  request.form.get('income_expense_id')
            cur.execute(""" SELECT pj.code,emp_one.name,pj.name,stat.location,stat.pj_start_date,emp_two.name,estimate_day,estimate_feet,estimate_sud,estimate_duty,estimate_fuel,estimate_expense,pj.id,
                            activity.daily_activity_no,activity.set_date,activity.working_status,activity.remark_for_not_working,activity.wealther_effect_percent,activity.complete_feet,activity.complete_sud,
							COALESCE(calculated_table.hour,'0.0'),COALESCE(calculated_table.fuel,'0.0')
                        FROM daily_activity activity
                        LEFT JOIN analytic_project_code pj
                        ON activity.project_id = pj.id
                        LEFT JOIN project_statistics stat
                        ON pj.id = stat.project_id
                        LEFT JOIN employee emp_one
                        ON emp_one.id = stat.ho_acc_id
                        LEFT JOIN employee emp_two
                        ON emp_two.id = stat.supervisor_id
						LEFT JOIN (
							SELECT daily_activity_id,ROUND(EXTRACT(hour FROM sum(duty_hour)) + EXTRACT(minute FROM sum(duty_hour)) / 60,2) AS hour,sum(used_fuel) AS fuel FROM daily_activity_lines  
							WHERE daily_activity_id = %s GROUP BY daily_activity_id
						) AS calculated_table
						ON calculated_table.daily_activity_id = activity.id
                        WHERE activity.id = %s;""",(daily_activity_id,daily_activity_id))
            form_datas = cur.fetchone()
            pj_id = form_datas[12]
            line_datas = []
            cur.execute("""SELECT line.id,car.id,car.machine_name,ajt.id,ajt.name,ajf.id,ajf.name,EXTRACT(HOUR FROM line.duty_hour),EXTRACT(MINUTE FROM line.duty_hour),line.used_fuel,line.description,COALESCE(line.way,'0.0')
                        FROM daily_activity_lines AS line
                        LEFT JOIN fleet_vehicle AS car
                        ON car.id = line.machine_id
                        LEFT JOIN activity_job_type AS ajt
                        ON ajt.id = line.job_type_id
                        LEFT JOIN activity_job_function AS ajf
                        ON ajf.id = line.job_function_id
                        WHERE line.daily_activity_id = %s;""",(daily_activity_id,))
            line_datas.append(cur.fetchall())
            cur.execute(""" SELECT line.id,car.id,car.machine_name,line.description,line.accident_status
                        FROM daily_activity_accident_lines AS line
                        LEFT JOIN fleet_vehicle AS car
                        ON car.id = line.machine_id WHERE line.daily_activity_id = %s;""",(daily_activity_id,))
            line_datas.append(cur.fetchall())
            cur.execute(""" SELECT type.name,count(*),MIN(type.id),MAX(machines_table.present_machines) FROM machines_history AS his
                            LEFT JOIN fleet_vehicle AS car
                            ON car.id = his.machine_id
                            LEFT JOIN machine_type type
                            ON type.id = car.machine_type_id
                            LEFT JOIN (
                                SELECT activity.project_id,present_machines FROM machines_history_project his
                                LEFT JOIN daily_activity activity
                                ON activity.id = his.daily_activity_id
                                WHERE daily_activity_id = %s
                            ) AS machines_table
                            ON machines_table.project_id = his.project_id
                            WHERE his.project_id = %s AND his.end_time IS  NULL
                            GROUP BY type.name; """,(daily_activity_id,pj_id))
            emp_datas = cur.fetchall()
            cur.execute(""" SELECT emp.name,emp_pj.assigned_people,emp_pj.id,emp_line.present_people FROM employee_group_project emp_pj
                            LEFT JOIN employee_group emp
                            ON emp.id = emp_pj.employee_group_id
                            LEFT JOIN employee_group_project_line emp_line
                            ON emp_line.employee_group_project_id = emp_pj.id
                            WHERE emp_line.daily_activity_id  = %s""",(daily_activity_id,))
            machine_type_datas = cur.fetchall()
            extra_datas = []
            cur.execute("SELECT CURRENT_DATE;")
            extra_datas.append(cur.fetchone()[0])
            zipped_machine_employee = list(zip_longest(machine_type_datas,emp_datas,fillvalue=("",0,0)))
            zipped_machine_employee.append([["Total",0,0],["Total",0,0]])
            for data in zipped_machine_employee[:-1]:
                zipped_machine_employee[-1][0][1] += data[0][1]
                zipped_machine_employee[-1][1][1] += data[1][1]
            extra_datas.append(zipped_machine_employee)
            cur.execute("SELECT car.machine_name,car.id FROM machines_history AS his LEFT JOIN fleet_vehicle AS car ON his.machine_id = car.id WHERE his.project_id = %s AND his.end_time IS NULL;",(pj_id,))
            machine_datas = cur.fetchall()
            cur.execute("SELECT name,id FROM activity_job_type;")
            activity_job_types = cur.fetchall()
            cur.execute("SELECT name,id FROM activity_job_function;")
            activity_job_functions = cur.fetchall()
            cur.execute(""" WITH form_table AS ( SELECT project_id,sum(complete_feet) AS feet,sum(complete_sud) AS sud
                            FROM daily_activity GROUP BY project_id ) ,
                            line_table AS (
                            SELECT form.project_id,ROUND((EXTRACT(HOUR FROM sum(duty_hour)) + EXTRACT(MINUTE FROM sum(duty_hour))/60),2) AS hour,sum(used_fuel) AS fuel FROM daily_activity_lines AS line
                            LEFT JOIN daily_activity AS FORM 
                            ON line.daily_activity_id = form.id
                            GROUP BY form.project_id ) ,
                            expense_table AS (
                            SELECT form.project_id,sum(line.amt) AS expense FROM income_expense_line AS line
                            LEFT JOIN income_expense AS form 
                            ON form.id = line.income_expense_id
                            WHERE form.income_status = 'f'
                            GROUP BY form.project_id
                            )
                            SELECT COALESCE(form_table.feet,0.0),COALESCE(form_table.sud,0.0),COALESCE(line_table.hour,0.0),COALESCE(line_table.fuel,0.0),COALESCE(expense_table.expense,0.0) FROM form_table 
                            LEFT JOIN line_table 
                            ON form_table.project_id = line_table.project_id
                            LEFT JOIN expense_table
                            ON form_table.project_id = expense_table.project_id
                            WHERE form_table.project_id = %s;""",(pj_id,))
            history_datas = cur.fetchone()
            if role in ('3','4'):
                cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
            else:
                cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
            project_datas = cur.fetchall()
            return render_template("daily-table.html",extra_datas = extra_datas,form_datas = form_datas,machine_datas=machine_datas,activity_jobs=[activity_job_types,activity_job_functions],history_datas=history_datas,line_datas = line_datas,template_type = 'Edit List',project_datas = project_datas)
        elif what == 'emp':
            code = request.form.get("code")
            name = request.form.get("empName")
            emp_gp_id = request.form.get("emp_gp")
            try:
                cur.execute("INSERT INTO employee (code,name,employee_group_id) VALUES(LPAD(%s,4,'0'),UPPER(%s),%s);",(code,name.upper(),emp_gp_id))
                conn.commit()
            except IntegrityError as err:
                mgs = str(err)
                conn.rollback()
            return redirect(url_for('views.configurations',what='employee'))
        elif what == 'employee-group':
            name = request.form.get("group").upper()
            try:
                cur.execute("INSERT INTO employee_group (name) VALUES (%s) ON CONFLICT(name) DO NOTHING;",(name,))
                conn.commit()
            except IntegrityError as err:
                mgs = str(err)
                conn.rollback()
            return redirect(url_for('views.configurations',what='employee-group'))
        elif what == 'fuel-price':
            price = request.form.get("sthPrice")
            start_dt = request.form.get("sthDate")
            try:
                cur.execute("SELECT %s::date - 1;",(start_dt,))
                end_date_for_other = cur.fetchone()
                cur.execute("UPDATE fuel_price_history SET end_date = %s WHERE end_date IS NULL;",(end_date_for_other,))
                cur.execute("INSERT INTO fuel_price_history (fuel_price,start_date) VALUES(%s,%s);",(price,start_dt))
                conn.commit()
            except IntegrityError as err:
                mgs = str(err)
                conn.rollback()
            return redirect(url_for('views.configurations',what='fuel-price'))
        elif what in ('ajt','ajf','type','class','unit','capacity','brand','owner'):
            sth_name = request.form.get("sthName")
            sth_edit_id = request.form.get("sthId")
            crud = request.form.get("crud")
            db = {'ajt':'activity_job_type','ajf':'activity_job_function','type':'machine_type',
                  'class':'machine_class','brand':'fleet_vehicle_model_brand','unit':'res_company',
                  'capacity':'vehicle_machine_config','owner':'vehicle_owner'}
            try:
                if crud == 'create':
                    cur.execute(f"INSERT INTO {db[what]} (name) VALUES('{sth_name.upper()}');")
                elif crud == 'update':
                    cur.execute(f"UPDATE {db[what]}  SET name = '{sth_name}' WHERE id = '{sth_edit_id}';")
                elif crud == 'delete':
                    cur.execute(f"DELETE FROM {db[what]} WHERE id =  '{sth_edit_id}';")
                conn.commit()
            except IntegrityError as err:
                mgs = str(err)
                conn.rollback()
            return redirect(url_for('views.configurations',what=what,mgs=mgs))
        else:
            return render_template('not_found.html')
    else:
        if role == '5':
            return render_template('access_error.html')
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
        elif what == 'project_stat' or what == 'project-stat':
            cur.execute("SELECT code || ' | ' || name FROM analytic_project_code AS pj LEFT JOIN project_statistics AS stat ON pj.id = stat.project_id WHERE stat.project_id is NULL;")
            data['Project Code'] = cur.fetchall()
            cur.execute(""" 
                SELECT car.id,car.machine_name,type.name FROM machines_history AS his
                INNER JOIN fleet_vehicle AS car
                ON his.machine_id = car.id
                LEFT JOIN machine_type AS type
                ON type.id = car.machine_type_id
                WHERE his.project_id = 1669 AND his.end_time IS NULL;
            """)
            data['Machine'] = cur.fetchall()
            cur.execute("SELECT id,name FROM employee_group;")
            data['group'] = cur.fetchall()
            cur.execute("SELECT emp.id,emp.name FROM employee emp INNER JOIN employee_group emp_gp ON emp.employee_group_id = emp_gp.id WHERE emp_gp.name = 'ACCOUNTANT';")
            data['accountants'] = cur.fetchall()
            cur.execute("SELECT id,name FROM employee;")        
            data['supervisors'] = cur.fetchall()
            name = 'Project Statistics Line'
        else:
            return render_template('not_found.html')
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
        conn = db_connect()
        cur = conn.cursor()
        query = ""
        if db == 'analytic_project_code':
            pj_datas = request.form.getlist('pj-datas')
            print(pj_datas)
            cur.execute("SELECT id FROM res_company where name = %s",(pj_datas[-1],))
            bi_id = cur.fetchall()
            if not bi_id:
                return redirect(url_for('views.configurations',what='project',mgs="Invalid Business Unit Name"))
            cur.execute("INSERT INTO project_type (name) VALUES (%s) ON CONFLICT (name) DO UPDATE set name = EXCLUDED.name RETURNING id;",(pj_datas[3],))
            pj_type_id = cur.fetchone()[0]
            cur.execute("INSERT INTO project_group (name) VALUES (%s) ON CONFLICT (name) DO UPDATE set name = EXCLUDED.name RETURNING id;",(pj_datas[2],))
            pj_group_id = cur.fetchone()[0]
            pj_datas[2] = pj_group_id
            pj_datas[3] = pj_type_id
            query = f""" INSERT INTO {db} (code,name,pj_group_id,pj_type_id,business_unit_id) VALUES ({",".join(["'{}'".format(item) for item in pj_datas[:-1]])},'{bi_id[0][0]}');"""
            what = 'project'
        elif db == 'duty_odoo_report':
            dty_datas = request.form.getlist('duty-datas')
            print(dty_datas)
        elif db == 'fleet_vehicle':
            edit_id = request.form.get("edit-id")
            vehicle_datas = request.form.getlist('vehicle-datas')
            tables_list = ['machine_type','machine_class','vehicle_machine_config','fleet_vehicle_model_brand','res_company','vehicle_owner'] if not edit_id else ['machine_class','vehicle_machine_config','fleet_vehicle_model_brand','res_company','vehicle_owner']
            inserted_values = [vehicle_datas[0]]
            for idx,table_name in enumerate(tables_list,start=1):
                idd = get_id_from_table(cur,table_name,vehicle_datas[idx])
                if not idd:
                    return redirect(url_for('views.configurations',what='machine',mgs=f"Invalid {change_db_to_field_name(table_name)}"))
                else:
                    inserted_values.append(idd)
            query = f""" INSERT INTO {db} (machine_name,machine_type_id,machine_class_id,machine_config_id,brand_id,business_unit_id,owner_name_id) VALUES {tuple(inserted_values)};"""
            if edit_id:
                query = f""" UPDATE  {db} SET machine_name = '{inserted_values[0]}'  , machine_class_id = '{inserted_values[1]}' , machine_config_id = '{inserted_values[2]}' , brand_id = '{inserted_values[3]}' , business_unit_id = '{inserted_values[4]}' , owner_name_id = '{inserted_values[5]}' WHERE id = {edit_id};"""
            print(query)
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
                cur.execute("UPDATE analytic_project_code SET project_status_id = (SELECT id FROM project_status WHERE name = 'IN PROGRESS') WHERE id = %s;",(pj_id,))
                if machine_ids != []:
                    for machine_id in machine_ids:
                        cur.execute("UPDATE machines_history SET end_time = NOW() WHERE machine_id =  %s AND end_time IS NULL;",(machine_id,))
                        cur.execute("INSERT INTO machines_history (project_id,machine_id) VALUES (%s,%s);",(pj_id,machine_id))
                if employee_group_ids != [] and employee_powers != []:
                    for data in zip(employee_group_ids,employee_powers):
                        cur.execute("INSERT INTO employee_group_project (project_id,employee_group_id,assigned_people) VALUES (%s,%s,%s);",(pj_id,data[0],data[1]))
                conn.commit()
            except IntegrityError as err:
                mgs = str(err).title()
                conn.rollback()
        elif db == 'terminate_project':
            pj_id = request.form.get("pj_id")
            status_name = request.form.get("status_name")
            cur.execute("UPDATE analytic_project_code SET project_status_id = (SELECT id FROM project_status WHERE name = %s) WHERE id = %s;",(status_name,pj_id))
            conn.commit()
            what = 'project-stat'
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
            print(update_query)
            try:
                cur.execute(update_query,list(input_values.values()))
                if machine_ids != []:
                    for machine_id in machine_ids:
                        cur.execute("UPDATE machines_history SET end_time = NOW() WHERE machine_id =  %s AND end_time IS NULL;",(machine_id,))
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
    created_username = request.cookies.get("cpu_username")
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
            cur.execute("INSERT INTO income_expense (income_status,income_expense_no,set_date,project_id,created_name) VALUES (%s,%s,%s,%s,%s) RETURNING id;",(income_status,report_no,import_date,pj_id,created_username))
            income_expense_id = cur.fetchone()[0]
            descriptions = request.form.getlist("description")[:-1]
            invoice_nos = request.form.getlist("invoice_no")[:-1]
            qtys = request.form.getlist("qty")[:-1]
            prices = request.form.getlist("price")[:-1]
            amts = request.form.getlist("amt")[:-1]
            remarks = request.form.getlist("remark")[:-1]
            machine_ids = request.form.getlist("machine_id")[:-1]
            query = "INSERT INTO income_expense_line (income_expense_id,description,invoice_no,qty,price,amt,remark,machine_id) VALUES "
            for data in zip(descriptions,invoice_nos,qtys,prices,amts,remarks,machine_ids):
                query += f"('{income_expense_id}','{data[0]}','{data[1]}','{data[2] if data[2] != '' else 0.0}','{data[3] if data[3] != '' else 0.0}','{data[4]}','{data[5]}',{data[6] if data[6] != '' else 'Null'}),"
            cur.execute(query[:-1]+';')
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("site_imports.income_expense",typ='view'))
        elif typ == 'income-expense-edit':
            form_id = request.form.get("form_id")
            descriptions = request.form.getlist("description")[:-1]
            invoice_nos = request.form.getlist("invoice_no")[:-1]
            qtys = request.form.getlist("qty")[:-1]
            prices = request.form.getlist("price")[:-1]
            amts = request.form.getlist("amt")[:-1]
            remarks = request.form.getlist("remark")[:-1]
            machine_ids = request.form.getlist("machine_id")[:-1]
            print(form_id)
            cur.execute("DELETE FROM income_expense_line WHERE income_expense_id = %s;",(form_id,))
            query = "INSERT INTO income_expense_line (income_expense_id,description,invoice_no,qty,price,amt,remark,machine_id) VALUES "
            for data in zip(descriptions,invoice_nos,qtys,prices,amts,remarks,machine_ids):
                query += f"('{form_id}','{data[0]}','{data[1]}','{data[2] if data[2] != '' else 0.0}','{data[3] if data[3] != '' else 0.0}','{data[4]}','{data[5]}',{data[6] if data[6] != '' else 'Null'}),"
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
            cur.execute("SELECT id FROM daily_activity")
            cur.execute("INSERT INTO daily_activity (daily_activity_no,working_status,remark_for_not_working,set_date,project_id,wealther_effect_percent,complete_feet,complete_sud,created_name) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;",(report_no,work_staus,reason_for_not_working,set_date,pj_id,wealther_affect,complete_feet,complete_sud,created_username))
            daily_activity_id = cur.fetchone()[0]

            machine_ids = request.form.getlist("machine_id")[:-1]
            job_type_ids = request.form.getlist("job_type_id")[:-1]
            job_function_ids = request.form.getlist("job_function_id")[:-1]
            duty_hr = request.form.getlist("dutyHour")[:-1]
            duty_min = request.form.getlist("dutyMin")[:-1]
            used_fuel = request.form.getlist("used_fuel")[:-1]
            descriptions = request.form.getlist("description")[:-1]
            ways = request.form.getlist('ways')[:-1]
            cur.execute("SELECT fuel_price FROM fuel_price_history WHERE %s BETWEEN start_date AND COALESCE(end_date,%s);",(set_date,set_date))
            fuel_price = cur.fetchone()[0]
            for data in zip(machine_ids,job_type_ids,job_function_ids,duty_hr,duty_min,used_fuel,descriptions,ways):
                print(data)
                if data != ('', '', '', '', '', '', '',''):
                    cur.execute(""" SELECT ROUND(CASE WHEN type.name = 'Per Duty' THEN ROUND((duty_price / 8),2) * %s + ROUND((duty_price/8) / 60,2) * %s WHEN type.name = 'Per Month' THEN (duty_price / 30) END,2) AS price
                                    FROM duty_price_history AS his
                                    INNER JOIN duty_price_type AS type
                                    ON his.duty_price_type_id = type.id WHERE machine_id = %s AND %s BETWEEN start_date AND COALESCE(end_date,%s);""",(data[3],data[4],data[0],set_date,set_date))
                    duty_amt = cur.fetchone()[0]
                    fuel_amt = round(fuel_price*(Decimal(data[5])*Decimal('4.54')),2)
                    print(duty_amt)
                    print(fuel_amt)
                    cur.execute("INSERT INTO daily_activity_lines(daily_activity_id,machine_id,job_type_id,job_function_id,duty_hour,used_fuel,description,duty_amt,fuel_amt,way) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(daily_activity_id,data[0],data[1],data[2],f'{data[3]} hours {data[4]}  minutes',data[5],data[6],duty_amt,fuel_amt,data[7]))
            # manpower & equipment
            man_amt = request.form.getlist("manpower_amt")
            man_id = request.form.getlist("manpower_id")
            type_amt = request.form.getlist("type_amt")
            type_id = request.form.getlist("type_id")
            for data in zip(man_id,man_amt):
                cur.execute("INSERT INTO employee_group_project_line(daily_activity_id,employee_group_project_id,present_people) VALUES (%s,%s,%s);",(daily_activity_id,data[0],data[1]))
            for data in zip(type_id,type_amt):
                cur.execute("INSERT INTO machines_history_project(daily_activity_id,machine_type_id,present_machines) VALUES (%s,%s,%s);",(daily_activity_id,data[0],data[1]))
            # accidents
            acc_machine_ids = request.form.getlist("acc_machine_id")[:-1]
            acc_descriptions = request.form.getlist("acc_description")[:-1]
            hasAccidents = request.form.getlist("hasAccident")[:-1]
            for data in zip(acc_machine_ids,acc_descriptions,hasAccidents):
                if data[0].strip() != '' and data[1].strip() != '':
                    cur.execute("INSERT INTO daily_activity_accident_lines(daily_activity_id,machine_id,description,accident_status) VALUES(%s,%s,%s,%s);",(daily_activity_id,data[0],data[1],int(data[2])))
            print(man_amt)
            print(man_id)
            print(type_amt)
            print(type_id)
            print(ways)
            print(acc_machine_ids)
            print(acc_descriptions)
            print(hasAccidents)

            print(machine_ids)
            print(job_type_ids)
            print(job_function_ids)
            print(duty_hr)
            print(duty_min)
            print(used_fuel)
            print(descriptions)
            conn.commit()
            return redirect(url_for('site_imports.daily_activity',typ='view'))
    else:
        return redirect(url_for("views.home"))
    


