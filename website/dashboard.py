from flask import Blueprint,render_template, request, redirect , url_for , jsonify, session
from website import db_connect,catch_db_insert_error
from openpyxl import load_workbook
from psycopg2 import IntegrityError

dash = Blueprint('dash',__name__)

@dash.route("")
def dash_home():

    conn = db_connect()
    cur = conn.cursor()

    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))

    user_id = session["cpu_user_id"]
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]

    if not role:
        return redirect(url_for('views.home'))
    else:
        if role not in (1,2,3,4):
            return render_template('access_error.html')
    if role in (4, 3):
        project_filter_query = ''
    else:
        project_filter_query = """
            LEFT JOIN project_user_access AS access 
            ON access.project_id = pj.id 
            WHERE access.user_id = %s 
        """
    query = f""" WITH stat_table AS (
            SELECT stat.project_id,status.name AS status,pj.code,pj.name AS pj_name,emp.name AS emp_name,stat.pj_start_date
            FROM project_statistics AS stat
            LEFT JOIN analytic_project_code AS pj 
            ON stat.project_id = pj.id
            LEFT JOIN employee AS emp
            ON emp.id = stat.supervisor_id
            LEFT JOIN project_status AS status
            ON status.id = pj.project_status_id
            {project_filter_query}
                ),
            form_table AS 
            ( SELECT project_id,sum(complete_feet) AS feet,sum(complete_sud) AS sud
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
            ),
            working AS (
            SELECT project_id,count(DISTINCT set_date) AS working_days FROM daily_activity
            WHERE working_status = 't' GROUP BY project_id
            )
            SELECT stat_table.project_id,stat_table.status,stat_table.code,stat_table.pj_name,stat_table.emp_name,
            COALESCE(form_table.feet,0),COALESCE(form_table.sud,0),COALESCE(line_table.hour,0),COALESCE(line_table.fuel,0),COALESCE(expense_table.expense,0),CURRENT_DATE - stat_table.pj_start_date,COALESCE(working.working_days,0) FROM stat_table
            LEFT JOIN form_table
            ON form_table.project_id = stat_table.project_id 
            LEFT JOIN line_table 
            ON form_table.project_id = line_table.project_id
            LEFT JOIN expense_table
            ON stat_table.project_id = expense_table.project_id
            LEFT JOIN working
            ON working.project_id = stat_table.project_id
            WHERE stat_table.status <> 'FINISHED'; """
    cur.execute(query,(user_id,))
    all_pj_datas = cur.fetchall()
    query = f"SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj {project_filter_query};"
    cur.execute(query,(user_id,))
    project_datas = cur.fetchall()
    return render_template('dashboard.html',all_pj_datas = all_pj_datas,project_datas = project_datas,current_role = role)