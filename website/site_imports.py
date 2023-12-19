from flask import Blueprint,render_template,redirect,request,url_for
from itertools import zip_longest
from website import db_connect
from decimal import Decimal

site_imports = Blueprint('site_imports',__name__)

@site_imports.route("/")
def home():
    return "Hello"

@site_imports.route("income-expense/<typ>/<mgs>",methods=['GET','POST'])
@site_imports.route("income-expense/<typ>",methods=['GET','POST'])
def income_expense(typ,mgs=None):
    conn = db_connect()
    cur = conn.cursor()
    user_id = request.cookies.get("cpu_user_id")
    current_role = request.cookies.get("cpu_role")
    if current_role not in ('1','3','4','5'):
        return render_template('access_error.html')
    elif not user_id:
        return redirect(url_for('auth.authenticate',typ='log'))
    if typ == 'create' and request.method == 'POST':
        cur.execute("SELECT CURRENT_DATE;")
        cur_date = cur.fetchone()[0]
        pj_id = request.form.get("pj_id")
        cur.execute(""" SELECT pj.code,emp_one.name,pj.name,stat.location,stat.pj_start_date,emp_two.name,pj.id
                        FROM  analytic_project_code pj
                        LEFT JOIN project_statistics stat
                        ON pj.id = stat.project_id
                        LEFT JOIN employee emp_one
                        ON emp_one.id = stat.ho_acc_id
                        LEFT JOIN employee emp_two
                        ON emp_two.id = stat.supervisor_id
                        WHERE pj.id = %s;""",(pj_id,))
        form_datas = cur.fetchone()
        cur.execute("SELECT car.machine_name,car.id FROM machines_history LEFT JOIN fleet_vehicle AS car ON car.id = machines_history.machine_id WHERE project_id = %s AND end_time IS NULL;",(pj_id,))
        machine_datas = cur.fetchall()
        if current_role in ('3','4'):
            cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
        else:
            cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("income_expense.html",cur_date = cur_date,form_datas = form_datas,machine_datas = machine_datas,template_type = 'Import',project_datas = project_datas)
    else:
        ##
        if current_role in ('4', '3'):
            project_filter_query = ''
        else:
            project_filter_query = """
                INNER JOIN project_user_access AS access 
                ON access.project_id = pj.id 
                WHERE access.user_id = %s
            """
        query = f""" SELECT form.id,form.set_date,MAX(pj.code),MAX(pj.name),form.income_expense_no,
                        CASE WHEN form.income_status = 't' THEN 'INCOME' ELSE 'EXPENSE' END,
                        SUM(line.amt)
                        FROM income_expense AS form 
                        INNER JOIN income_expense_line AS line 
                        ON line.income_expense_id = form.id
                        INNER JOIN analytic_project_code AS pj
                        ON pj.id = form.project_id
                        {project_filter_query}
                        GROUP BY form.id
                        ORDER BY MAX(pj.id),form.set_date DESC
                        LIMIT 81; """
        cur.execute(query,(user_id,))
        result = cur.fetchall()
        extra_datas = []
        cur.execute("SELECT count(id) FROM income_expense_line;")
        extra_datas.append(cur.fetchone())
        query = f"SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj {project_filter_query};"
        cur.execute(query,(user_id,))
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("income_expense.html",result=result,template_type = 'Report List',extra_datas=extra_datas,project_datas=project_datas,mgs=mgs)

@site_imports.route("daily-activity/<typ>/<mgs>",methods=['GET','POST'])
@site_imports.route("daily-activity/<typ>",methods=['GET','POST'])
def daily_activity(typ,mgs=None):
    conn = db_connect()
    cur = conn.cursor()
    user_id = request.cookies.get("cpu_user_id")
    current_role = request.cookies.get("cpu_role")
    if current_role not in ('1','3','4','5'):
        return render_template('access_error.html')
    elif not user_id:
        return redirect(url_for('auth.authenticate',typ='log'))
    if typ == 'create' and request.method == 'POST':
        pj_id = request.form.get("pj_id")
        cur.execute(""" SELECT pj.code,emp_one.name,pj.name,stat.location,stat.pj_start_date,emp_two.name,estimate_day,estimate_feet,estimate_sud,estimate_duty,estimate_fuel,estimate_expense,pj.id
                        FROM  analytic_project_code pj
                        LEFT JOIN project_statistics stat
                        ON pj.id = stat.project_id
                        LEFT JOIN employee emp_one
                        ON emp_one.id = stat.ho_acc_id
                        LEFT JOIN employee emp_two
                        ON emp_two.id = stat.supervisor_id
                        WHERE pj.id = %s;""",(pj_id,))
        form_datas = cur.fetchone()
        if form_datas[7] == None:
            return redirect(url_for('site_imports.daily_activity',typ='view'))
        cur.execute(""" SELECT type.name,count(*),MIN(type.id) FROM machines_history AS his
                        LEFT JOIN fleet_vehicle AS car
                        ON car.id = his.machine_id
                        LEFT JOIN machine_type type
                        ON type.id = car.machine_type_id
                        WHERE his.project_id = %s AND his.end_time IS  NULL
                        GROUP BY type.name; """,(pj_id,))
        emp_datas = cur.fetchall()
        cur.execute(""" SELECT emp.name,emp_pj.assigned_people,emp_pj.id FROM employee_group_project emp_pj
                        LEFT JOIN employee_group emp
                        ON emp.id = emp_pj.employee_group_id
                        WHERE emp_pj.project_id  = %s""",(pj_id,))
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
        cur.execute(""" SELECT car.machine_name,car.id FROM machines_history AS his 
                        LEFT JOIN fleet_vehicle AS car ON his.machine_id = car.id
                        LEFT JOIN duty_price_history AS duty_his ON duty_his.machine_id = car.id
                        WHERE his.project_id = %s AND his.end_time IS NULL AND duty_his.duty_price IS NOT NULL AND duty_his.end_date IS NULL;""",(pj_id,))
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
        if current_role in ('3','4'):
            cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
        else:
            cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        if not history_datas:
            history_datas = (Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'))
        print(history_datas)
        return render_template("daily-table.html",extra_datas = extra_datas,form_datas = form_datas,machine_datas=machine_datas,activity_jobs=[activity_job_types,activity_job_functions],history_datas=history_datas,template_type = 'create',project_datas = project_datas,mgs=mgs)
    else:
        if current_role in ('4', '3'):
            project_filter_query = ''
        else:
            project_filter_query = """
                INNER JOIN project_user_access AS access 
                ON access.project_id = das.pj_id 
                WHERE access.user_id = %s
            """
        query = f""" WITH daily_activity_summary AS (
                            SELECT 
                                da.id,
                                da.set_date,
                                pj.code,
                                pj.name,
                                da.daily_activity_no,
                                CASE WHEN da.working_status = 't' THEN 'Working' ELSE 'Not Working' END AS working_status,
                                da.remark_for_not_working,
                                da.wealther_effect_percent,
                                da.complete_feet,
                                da.complete_sud,
                                pj.id AS pj_id
                            FROM daily_activity da
                            JOIN analytic_project_code pj ON da.project_id = pj.id
                        ),
                        duty_hours_summary AS (
                            SELECT daily_activity_id, SUM(duty_hour) AS total_duty_hour, SUM(used_fuel)  AS total_used_fuel, SUM(way) AS ways
                            FROM daily_activity_lines
                            GROUP BY daily_activity_id
                        ),
                        present_people_summary AS (
                            SELECT daily_activity_id, SUM(present_people) AS total_present_people
                            FROM employee_group_project_line
                            GROUP BY daily_activity_id
                        ),
                        present_machines_summary AS (
                            SELECT daily_activity_id, SUM(present_machines) AS total_present_machines
                            FROM machines_history_project
                            GROUP BY daily_activity_id
                        ),
                        accident_summary AS (
                            SELECT daily_activity_id, COUNT(machine_id) AS machine_count, bool_or(accident_status) AS any_accident
                            FROM daily_activity_accident_lines
                            GROUP BY daily_activity_id
                        )
                        SELECT
                            das.id,
                            das.set_date,
                            das.code,
                            das.name,
                            das.daily_activity_no,
                            das.working_status,
                            das.remark_for_not_working,
                            das.wealther_effect_percent,
                            das.complete_feet,
                            das.complete_sud,
                            COALESCE(dh.total_duty_hour,'0:00:00'),
                            COALESCE(dh.total_used_fuel,'0.0'),
                            pp.total_present_people,
                            pm.total_present_machines,
                            COALESCE(a.machine_count,0),
                            COALESCE(a.any_accident,'FALSE'),
                            COALESCE(dh.ways,'0.0')
                        FROM daily_activity_summary das
                        LEFT JOIN duty_hours_summary dh ON das.id = dh.daily_activity_id
                        LEFT JOIN present_people_summary pp ON das.id = pp.daily_activity_id
                        LEFT JOIN present_machines_summary pm ON das.id = pm.daily_activity_id
                        LEFT JOIN accident_summary a ON das.id = a.daily_activity_id
                        {project_filter_query}
                        ORDER BY das.pj_id,das.set_date DESC,das.daily_activity_no DESC; """
        cur.execute(query,(user_id,))
        result = cur.fetchall()
        extra_datas = []
        cur.execute("SELECT count(*) FROM daily_activity;")
        extra_datas.append(cur.fetchone())
        if current_role in ('3','4'):
            cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
        else:
            cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        print(result)
        return render_template("daily-table.html",project_datas=project_datas,result=result,extra_datas = extra_datas,template_type='view',mgs=mgs)
    