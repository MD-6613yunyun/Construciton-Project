from flask import Blueprint,render_template,redirect,request
from website import db_connect

site_imports = Blueprint('site_imports',__name__)

@site_imports.route("/")
def home():
    return "Hello"

@site_imports.route("income-expense/<typ>")
def income_expense(typ):
    conn = db_connect()
    cur = conn.cursor()
    if typ == 'create':
        cur.execute("SELECT CURRENT_DATE;")
        cur_date = cur.fetchone()[0]
        cur.execute("SELECT code || ' | ' || name FROM analytic_project_code WHERE id IN (SELECT project_id FROM project_statistics);")
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("income_expense.html",cur_date = cur_date,project_datas = project_datas,template_type = 'Import')
    else:
        cur.execute("""SELECT form.id,form.set_date,MAX(pj.code),MAX(pj.name),form.income_expense_no,
                        CASE WHEN form.income_status = 't' THEN 'INCOME' ELSE 'EXPENSE' END,
                        SUM(line.amt)
                        FROM income_expense AS form 
                        INNER JOIN income_expense_line AS line 
                        ON line.income_expense_id = form.id
                        INNER JOIN analytic_project_code AS pj
                        ON pj.id = form.project_id
                        GROUP BY form.id
                        ORDER BY MAX(pj.id),form.set_date DESC;""")
        result = cur.fetchall()
        print(result)
        cur.close()
        conn.close()
        return render_template("income_expense.html",result=result,template_type = 'Report List')

@site_imports.route("daily-activity/<typ>",methods=['GET','POST'])
def daily_activity(typ):
    conn = db_connect()
    cur = conn.cursor()
    if typ == 'create' and request.method == 'POST':
        pj_id = request.form.get("pj_id")
        cur.execute(""" SELECT pj.code,emp_one.name,pj.name,stat.location,stat.pj_start_date,emp_two.name,estimate_day,estimate_feet,estimate_sud,estimate_fuel,estimate_expense
                        FROM  analytic_project_code pj
                        LEFT JOIN project_statistics stat
                        ON pj.id = stat.project_id
                        LEFT JOIN employee emp_one
                        ON emp_one.id = stat.ho_acc_id
                        LEFT JOIN employee emp_two
                        ON emp_two.id = stat.supervisor_id
                        WHERE pj.id = %s;""",(pj_id,))
        form_datas = cur.fetchone()
        cur.execute("SELECT CURRENT_DATE;")
        cur_date = cur.fetchone()[0]
        cur.execute("SELECT code || ' | ' || name FROM analytic_project_code WHERE id IN (SELECT project_id FROM project_statistics);")
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("daily-table.html",cur_date = cur_date,project_datas = project_datas,template_type = 'create')
    else:
        result = []
        cur.execute("SELECT code || ' | ' || name FROM analytic_project_code WHERE id IN (SELECT project_id FROM project_statistics);")
        project_datas = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("daily-table.html",project_datas=project_datas,result=result,template_type='view')