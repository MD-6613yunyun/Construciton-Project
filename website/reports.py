from flask import Blueprint,render_template, request, redirect , url_for , jsonify,send_file, session
from website import db_connect
from datetime import datetime,timedelta
import decimal
from decimal import Decimal
from psycopg2 import IntegrityError
import subprocess
import os
import xlsxwriter
from fpdf import FPDF

# Get the base directory of your project
base_directory = os.path.dirname(os.path.abspath(__file__))

# Combine the base directory and relative path to get the full file path
excel_path = os.path.join(base_directory, "static/downloadable_files/IncomeExpesneReport.xlsx")
pdf_path = os.path.join(base_directory, "static/downloadable_files/IncomeExpenseReport.pdf")
output_path = os.path.join(base_directory, "static/php/output.txt")
input_path = os.path.join(base_directory, "static/php/input.txt")

# some php
php_script = os.path.join(base_directory, "static/php/test_rabbit_text.php")
## for linux
# php_exe = r'/usr/bin/php'
php_exe = r'C:\xampp\php\php.exe'

# font path
zawgyi_font_path = os.path.join(base_directory,"static/fonts/Zawgyi.ttf")

reports = Blueprint('reports',__name__)

@reports.route("/check-supervisior/<name>")
def check_supervisior(name:str):
    conn = db_connect()
    cur = conn.cursor()
    not_included_supervisor = []
    for each_supervisor in name.split(","):
        cur.execute("SELECT id FROM project_statistics WHERE supervisior = %s;",(each_supervisor,))
        if cur.fetchall() == []:
            not_included_supervisor.append(each_supervisor)
    return jsonify(not_included_supervisor)

## This is with duty_odoo_report
# @reports.route('/summary-duty-report',methods=['GET','POST'])
# def summary_duty_report(mgs=None):
#     conn = db_connect()
#     cur = conn.cursor()
#     user_id = request.cookies.get('cpu_user_id')
#     role = request.cookies.get('cpu_role')
#     if not role:
#         return redirect(url_for('views.home'))
#     else:
#         if int(role) not in (2,3,4):
#             return render_template('access_error.html')

#     if request.method == 'POST':
#         pj_summary_id = request.form.get('pj_id')
#         pj_summary_name = request.form.get('pj_name')
#         if pj_summary_name:
#             print(pj_summary_id)
#             cur.execute("""
#                 WITH sum_dty AS (
#                     SELECT report.project_id AS p_id,emp.name AS person,SUM(total_hr) AS a_duty,SUM(totaluse_fuel) AS a_fuel,
#                     SUM(ROUND(EXTRACT(HOUR FROM total_hr) + EXTRACT(MINUTE FROM total_hr) / 60.0, 2)) AS balance_duty,
#                     ps.estimate_feet AS e_feet,ps.will_sud AS e_sud_1,
#                     ps.estimate_duty AS e_duty,ps.estimate_fuel AS e_fuel,ps.estimate_expense AS e_expense,ps.estimate_sud As e_sud
#                     FROM duty_odoo_report report
#                     LEFT JOIN project_statistics ps
#                     ON report.project_id = ps.project_id
#                     LEFT JOIN employee emp
#                     ON emp.id = ps.supervisor_id
#                     WHERE report.project_id = %s
#                     GROUP BY ps.estimate_feet,ps.will_sud,ps.estimate_sud,ps.estimate_duty,ps.estimate_fuel,ps.estimate_expense,report.project_id,emp.name )
#                 SELECT pj.name,pj.code,person,e_feet,e_sud_1,e_sud,e_duty,balance_duty,e_duty-balance_duty,e_fuel,ROUND(a_fuel/4.54,2) AS a_fuel_gl,e_fuel-ROUND(a_fuel/4.54,2),e_expense,e_sud,SUM(pd.work_done),e_sud - SUM(pd.work_done) AS balance_sud,status.name
#                     FROM project_each_day_work_done pd
#                     INNER JOIN sum_dty 
#                     ON sum_dty.p_id = pd.project_id
#                     LEFT JOIN analytic_project_code pj
#                     ON pj.id = sum_dty.p_id
#                     LEFT JOIN project_status status
#                     ON status.id = pj.project_status_id
#                     GROUP BY pj.name,balance_duty,pj.code,person,e_feet,e_sud_1,e_sud,a_duty,a_fuel,e_duty,e_fuel,e_expense,status.name;
#             """,(pj_summary_id,))
#             result_data = cur.fetchall()
#             if result_data == []:
#                 cur.execute(f""" SELECT
#                                     ROUND(SUM(totaluse_fuel) / 4.54, 2) AS a_fuel,
#                                     SUM(ROUND(EXTRACT(HOUR FROM total_hr) + EXTRACT(MINUTE FROM total_hr) / 60.0, 2)) AS balance_duty,
#                                     COALESCE(work_done_sum, 0) AS actual_workdone,
#                                     COALESCE(total_sum, 0) AS total_expenses,
#                                     COALESCE(project_code, 'Unassigned Project Code') AS pj_code,
#                                     COALESCE(project_name, 'Unassigned Project Name') AS pj_name,
#                                     COALESCE(project_state,'Unassigned') AS pj_state
#                                 FROM
#                                     duty_odoo_report report
#                                 LEFT JOIN (
#                                     SELECT
#                                         project_id,
#                                         SUM(work_done) AS work_done_sum
#                                     FROM
#                                         project_each_day_work_done
#                                     GROUP BY
#                                         project_id
#                                 ) wd ON report.project_id = wd.project_id
#                                 LEFT JOIN (
#                                     SELECT
#                                         p_id,
#                                         SUM(work_done) + SUM(total_amt) AS total_sum
#                                     FROM
#                                         (
#                                             SELECT
#                                                 ep.project_id AS p_id,
#                                                 SUM(COALESCE(ep.expense_amt, 0)) AS work_done,
#                                                 0 AS total_amt
#                                             FROM
#                                                 expense_prepaid ep
#                                             WHERE ep.res_company_id = (SELECT business_unit_id FROM analytic_project_code 
#                                                     WHERE id = '{pj_summary_id}')
#                                             GROUP BY
#                                                 ep.project_id, ep.res_company_id
#                                             UNION ALL
#                                             SELECT
#                                                 project_id AS p_id,
#                                                 0 AS work_done,
#                                                 SUM(total_amt) AS total_amt
#                                             FROM
#                                                 duty_odoo_report
#                                             GROUP BY
#                                                 project_id
#                                         ) AS combined_data
#                                     GROUP BY
#                                         p_id
#                                 ) ep ON report.project_id = ep.p_id
#                                 LEFT JOIN (
#                                     SELECT
#                                         pj.id,
#                                         pj.name AS project_name,
#                                         pj.code AS project_code,
#                                         status.name AS project_state
#                                     FROM
#                                         analytic_project_code pj
#                                     INNER JOIN project_status status
#                                     ON status.id = pj.project_status_id 
#                                 ) pj ON pj.id = report.project_id
#                                 WHERE
#                                     report.project_id = '{pj_summary_id}'
#                                 GROUP BY
#                                     report.project_id, work_done_sum, total_sum, project_code, project_name,project_state;
#                 """)
#                 datas = cur.fetchall()
#                 if datas == []:
#                     cur.execute("SELECT name,code FROM analytic_project_code WHERE id = %s;",(pj_summary_id,))
#                     pj_code_name = cur.fetchall()
#                     cur.execute("SELECT pj.id,code,name FROM analytic_project_code pj INNER JOIN project_user_access access ON access.project_id = pj.id WHERE access.user_id = %s;",(int(user_id),))
#                     project_datas = cur.fetchall()
#                     return render_template("summary_form.html",pj_code_name = pj_code_name,project_datas = project_datas)
#                 result_data = [(datas[0][5],datas[0][4],'Unassigned Supervisor',Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),datas[0][1],Decimal('0.0')-datas[0][1],Decimal('0.0'),datas[0][0],Decimal('0.0')-datas[0][0],Decimal('0.0'),Decimal('0.0'),datas[0][3],Decimal('0.0')-datas[0][3],datas[0][6])]
#                 exp = [datas[0][2],Decimal('0.0')-datas[0][2]]
#             else:
#                 cur.execute(f""" SELECT
#                                     SUM(work_done) + SUM(total_amt) AS total_sum
#                                 FROM
#                                 (
#                                     SELECT
#                                         SUM(COALESCE(pe.expense_amt, '0.00')) AS work_done,
#                                         0 AS total_amt  
#                                     FROM
#                                         expense_prepaid pe 
#                                     WHERE
#                                         pe.project_id = '{pj_summary_id}'
#                                         AND pe.res_company_id = (SELECT business_unit_id FROM analytic_project_code WHERE id = '{pj_summary_id}')
#                                 UNION ALL
#                                     SELECT
#                                         0 AS work_done, 
#                                         SUM(total_amt) AS total_amt
#                                     FROM
#                                         duty_odoo_report
#                                     WHERE
#                                         project_id = '{pj_summary_id}'
#                                 ) AS combined_data;""")
#                 exp = cur.fetchall()
#                 if result_data and exp:
#                     exp = [exp[0][0],result_data[0][-5] - exp[0][0]]
#             cur.execute("SELECT pj.id,code,name FROM analytic_project_code pj INNER JOIN project_user_access access ON access.project_id = pj.id WHERE access.user_id = %s;",(int(user_id),))
#             project_datas = cur.fetchall()
#             cur.close()
#             conn.close()
#             return render_template("summary_form.html",result_data = result_data[0] if result_data else result_data,message=mgs,exp=exp,project_datas=project_datas)
#     return render_template("not_found.html")

@reports.route('/summary-duty-report',methods=['GET','POST'])
def summary_duty_report():

    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))

    conn = db_connect()
    cur = conn.cursor()
    user_id = session["cpu_user_id"]
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]
    if not role:
        return redirect(url_for('views.home'))
    else:
        if role not in (1,2,3,4):
            return render_template('access_error.html')

    if request.method == 'POST':
        pj_summary_id = request.form.get('pj_id')
        pj_summary_name = request.form.get('pj_name')
        if pj_summary_id:
            cur.execute("""
            WITH stat_table AS (
                SELECT stat.project_id,status.name AS status,pj.code,pj.name AS pj_name,emp.name AS emp_name,stat.pj_start_date,
                    stat.location,stat.estimate_feet,stat.estimate_sud,stat.will_sud,stat.estimate_duty,stat.estimate_fuel,stat.estimate_expense,
                    stat.estimate_day
                FROM project_statistics AS stat
                LEFT JOIN analytic_project_code AS pj 
                ON stat.project_id = pj.id
                LEFT JOIN employee AS emp
                ON emp.id = stat.supervisor_id
                LEFT JOIN project_status status
                ON status.id = pj.project_status_id
            ),
            form_table AS ( 
                SELECT project_id,sum(complete_feet) AS feet,sum(complete_sud) AS sud
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
                SELECT project_id,count(id) AS working_days FROM daily_activity
                WHERE working_status = 't' GROUP BY project_id 
                        )
            SELECT stat_table.project_id,stat_table.status,stat_table.code,stat_table.pj_name,stat_table.emp_name,
                stat_table.estimate_duty,COALESCE(line_table.hour,0) AS a_duty,
                stat_table.estimate_fuel,COALESCE(line_table.fuel,0) AS a_fuel,
                stat_table.estimate_expense,COALESCE(expense_table.expense,0) AS a_expense,
                stat_table.estimate_feet,COALESCE(form_table.feet,0) AS a_feet,
                stat_table.will_sud,COALESCE(form_table.sud,0) AS a_sud,
                stat_table.estimate_day,CURRENT_DATE - stat_table.pj_start_date AS a_day,
                stat_table.estimate_sud,stat_table.location,COALESCE(working.working_days,0) AS work_days FROM stat_table
            LEFT JOIN form_table
                ON form_table.project_id = stat_table.project_id 
            LEFT JOIN line_table 
                ON form_table.project_id = line_table.project_id
            LEFT JOIN expense_table
                ON stat_table.project_id = expense_table.project_id
            LEFT JOIN working
                ON working.project_id = stat_table.project_id
            WHERE stat_table.project_id = %s;""",(pj_summary_id,))
            result_data = cur.fetchone()
            if role in (3, 4):
                cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
            else:
                cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
            project_datas = cur.fetchall()
            return render_template("summary_form.html",result_data=result_data,project_datas=project_datas,pj_summary_name=pj_summary_name, current_role = role)
    return render_template("not_found.html")

@reports.route('/call-project-statistics/<pjCode>')
def call_project_statistics(pjCode):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""SELECT ps.id,pc.name,pc.code,ps.supervisior,ps.estimate_feet,ps.will_sud,ps.estimate_sud,ps.estimate_duty,ps.estimate_fuel,ps.estimate_expense FROM project_statistics ps
                INNER JOIN analytic_project_code pc
                ON ps.project_id = pc.id WHERE project_id = %s""",(pjCode,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result[0] if result else result)

def get_max_day(monthh,yearr,only_end_day=False,start_end_dates = [(None,None)],in_one_month=False):
    if((monthh==2) and ((yearr%4==0)  or ((yearr%100==0) and (yearr%400==0)))):
        maxx = 29
    elif(monthh==2):
        maxx = 28
    elif(monthh==1 or monthh==3 or monthh==5 or monthh==7 or monthh==8 or monthh==10 or monthh==12) :
        maxx = 31
    else :
        maxx = 30
    lst = []
    mnt = f"0{monthh}" if monthh < 10 else f"{monthh}"
    if only_end_day:
        if start_end_dates[0][0]:
            if in_one_month:
                if start_end_dates[0][0].month != start_end_dates[0][1].month:
                    return f"{yearr}-{mnt}-{start_end_dates[0][0].day}",f"{yearr}-{mnt}-{maxx}"                    
            print(start_end_dates[0][0].month,start_end_dates[0][0].day)
            print(start_end_dates[0][1].month,start_end_dates[0][1].day)
            return f"{yearr}-{mnt}-{start_end_dates[0][0].day}",f"{yearr}-{mnt}-{start_end_dates[0][1].day}"
        return f"{yearr}-{mnt}-01",f"{yearr}-{mnt}-{maxx}"
    start_date = start_end_dates[0][0].day if start_end_dates[0][0] else 1
    end_date = start_end_dates[0][1].day+1 if start_end_dates[0][1] else maxx + 1
    for i in range(start_date,end_date):
        dt = f"{yearr}-{mnt}-0{i}" if i < 10 else f"{yearr}-{mnt}-{i}"
        lst.append(dt)
    if start_end_dates == [(None,None)]:
        return []
    return lst


def get_the_previous_data(temp,fst_temp,optionGroupBy):
    if fst_temp == [(None,None)]:
        fst_temp = [(Decimal('0.0'),Decimal('0.0'))]
    if optionGroupBy == 'qty':
        overall_temps = ['Daily Overall',timedelta(0),Decimal('0.0')]
        for tmp in temp:
            overall_temps[1] += tmp[1]
            overall_temps[2] += tmp[2]
        overall_temps.append(fst_temp[0][1])
        if overall_temps[2] != Decimal('0.0') and fst_temp[0][1] != Decimal('0.00'):
            overall_temps.append(overall_temps[2]/fst_temp[0][1])
        else:
            overall_temps.append(Decimal(0))        
    elif optionGroupBy == 'price':
        overall_temps = ['Daily Overall',Decimal('0.0'),Decimal('0.0')]
        for tmp in temp:
            overall_temps[1] += tmp[1]
            overall_temps[2] += tmp[2]
    else:
        overall_temps = ['Daily Overall',timedelta(0),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),Decimal('0.0'),0,0]
        print(temp)
        for tmp in temp:
            overall_temps[1] += tmp[1]
            overall_temps[2] += tmp[2]
            overall_temps[3] += tmp[4]
            overall_temps[4] += tmp[5]
        overall_temps[5] = fst_temp[0][0]
        print(overall_temps)
        overall_temps[6] = overall_temps[3] + overall_temps[4] + overall_temps[5]
        overall_temps[7] = fst_temp[0][1]
        if overall_temps[7] != Decimal(0):
            overall_temps[8] = overall_temps[2] / overall_temps[7]  
            overall_temps[9] = overall_temps[6] / overall_temps[7]
    temp.append(overall_temps)
    return temp

# @reports.route("/gett-monthly-duty",methods=['GET','POST'])
# def gett_monthly_duty():
#     conn = db_connect()
#     cur = conn.cursor()
#     user_id = request.cookies.get("cpu_user_id")
#     role = request.cookies.get("cpu_role")
#     if not user_id:
#         return redirect(url_for('auth.authenticate',typ='log'))
#     elif role not in ('1','2','3','4'):
#         return render_template("access_error.html")
#     if request.method == 'POST':
#         pj_id = request.form.get("pj_id")
#         date_duty = request.form.get("start")
#         pj_name, pj_code = request.form.get("pj_name").split('_&_')
#         optionGroupBy = request.form.get("radioOPtions")
#         optionGroupByTwo = request.form.get("radioOPtionsTwo")
#         yer,mnt = map(int,date_duty.split("-"))
#         dt_text = datetime(yer,mnt,1).strftime("%Y %B")
#         tableOptionsOne = {"type":["machine_type","machine_type_id"],"class":["machine_class","machine_class_id"],"capacity":["vehicle_machine_config","machine_config_id"]} 
#         table_option_one = tableOptionsOne[optionGroupBy]
#         tableOptionsTwo = {"qty":["SUM(total_hr),","ROUND(SUM(totaluse_fuel)/4.54,2),"],"price":["SUM(duty_amt),","SUM(fuel_amt),"],"consumption":["SUM(total_hr),","ROUND(SUM(totaluse_fuel)/4.54,2),","SUM(duty_amt),","SUM(fuel_amt),",'SUM(way),']}
#         table_fields_one_query = ""
#         flt = 'Qty' if optionGroupByTwo == 'qty' else 'Price'
#         for idx,field in enumerate(tableOptionsTwo[optionGroupByTwo]):
#             if optionGroupByTwo == 'consumption' and idx == 2:
#                 table_fields_one_query += """ CASE
#                                                 WHEN SUM(dty.total_hr) = '0:0:0' THEN 0
#                                                 ELSE ROUND((SUM(dty.totaluse_fuel)/4.54) / EXTRACT(EPOCH FROM SUM(dty.total_hr)) * 3600, 2)
#                                             END,"""
#             table_fields_one_query += field
#         if pj_id == "" or date_duty == "" or pj_name == "":
#             return redirect(url_for('views.home',mgs=f"Incomplete Field For Project Name - Project Code."))
#         query = f""" SELECT MIN(DISTINCT(duty_date)),MAX(DISTINCT(duty_date)) 
#                         FROM duty_odoo_report WHERE project_id = {pj_id}
#                         AND EXTRACT(YEAR FROM duty_date) = {yer} AND EXTRACT(MONTH FROM duty_date) = {mnt}; """
#         cur.execute(query)
#         start_end_dates = cur.fetchall()
#         query = f""" SELECT DISTINCT(mc.name) FROM duty_odoo_report dty
#                     LEFT JOIN fleet_vehicle fv ON fv.id = dty.machine_id
#                     LEFT JOIN {table_option_one[0]} mc ON mc.id = fv.{table_option_one[1]}
#                     WHERE dty.project_id = '{pj_id}' ORDER BY mc.name;"""
#         cur.execute(query)
#         all_classes = cur.fetchall()
#         final_dct = {}
#         counter = 0
#         ## get work done
#         start_wd_date , end_wd_date = get_max_day(mnt,yer,True,start_end_dates)
#         fst_temp = []
#         if optionGroupByTwo != 'price':
#             cur.execute(f"""WITH all_dates AS (
#                             SELECT generate_series('{start_wd_date}'::date, '{end_wd_date}'::date, '1 day'::interval) AS date
#                             )
#                             SELECT
#                             all_dates.date,
#                             COALESCE(pe.work_done, '0.00') AS work_done
#                             FROM
#                             all_dates
#                             LEFT JOIN
#                             project_each_day_work_done pe ON all_dates.date = pe.duty_date AND pe.project_id = '{pj_id}'
#                             ORDER BY
#                             all_dates.date;
#                             """)
#             idx_for_wd = 0
#             all_wd_datas = cur.fetchall()
#             ## get expenses
#             cur.execute(f""" WITH all_dates AS (
#                             SELECT generate_series('{start_wd_date}'::date, '{end_wd_date}'::date, '1 day'::interval) AS date
#                             )
#                             SELECT
#                             all_dates.date,
#                             SUM(COALESCE(pe.expense_amt, '0.00')) AS work_done
#                             FROM
#                             all_dates
#                             LEFT JOIN
#                             expense_prepaid pe 
#                             ON all_dates.date = pe.duty_date AND pe.project_id = '{pj_id}'
#                             AND pe.res_company_id = (SELECT business_unit_id FROM analytic_project_code WHERE id = '{pj_id}')
#                             GROUP BY pe.duty_date,all_dates.date
#                         ORDER BY all_dates.date; """)
#             all_exp_datas = cur.fetchall()
#             ## before queries
#             cur.execute(f""" SELECT
#                                 SUM(expense_amt) AS exp,
#                                 SUM(work_done) AS wd
#                             FROM
#                                 ( SELECT expense_amt,0 AS work_done 
#                                     FROM expense_prepaid
#                                     WHERE duty_date <= '{start_wd_date}' AND project_id = '{pj_id}' 
#                                     AND res_company_id = (SELECT business_unit_id 
#                                                             FROM analytic_project_code
#                                                             WHERE id = '{pj_id}')
#                                 UNION ALL
#                                 SELECT 0 AS expense_amt,work_done
#                                     FROM project_each_day_work_done
#                                     WHERE duty_date <= '{start_wd_date}' AND project_id = '{pj_id}'
#                                 ) AS combined_data; """)
#             fst_temp = cur.fetchall()
#         cur.execute(f"""SELECT mc.name,{table_fields_one_query[:-1]} FROM duty_odoo_report dty
#                     LEFT JOIN fleet_vehicle fv ON fv.id = dty.machine_id
#                     LEFT JOIN {table_option_one[0]} mc ON mc.id = fv.{table_option_one[1]}
#                     WHERE dty.duty_date <= '{start_wd_date}' AND dty.project_id = '{pj_id}'
#                     GROUP BY mc.name
#                     ORDER BY mc.name;""")
#         temp = cur.fetchall()
#         overall_temps = get_the_previous_data(temp,fst_temp,optionGroupByTwo)
#         ##
#         idx_for_wd = 0            
#         show_all = 2
#         for dt in get_max_day(mnt,yer,False,start_end_dates):
#             lst = [i[0] for i in all_classes]
#             query = f"""SELECT mc.name,{table_fields_one_query[:-1]} FROM duty_odoo_report dty
#                     LEFT JOIN fleet_vehicle fv ON fv.id = dty.machine_id
#                     LEFT JOIN {table_option_one[0]} mc ON mc.id = fv.{table_option_one[1]}
#                     WHERE dty.duty_date = '{dt}' AND dty.project_id = '{pj_id}'
#                     GROUP BY mc.name
#                     ORDER BY mc.name;"""
#             cur.execute(query)
#             each_day_data = cur.fetchall()
#             for day_data in each_day_data:
#                 lst[lst.index(day_data[0])] = day_data

#             if optionGroupByTwo != 'price':
#                 work_done = all_wd_datas[idx_for_wd][1]
#                 expense = all_exp_datas[idx_for_wd][1]
#             consump = decimal.Decimal(0.0)
#             cost = Decimal('0.0')
#             if optionGroupByTwo == "qty":
#                 rmv_no = [("",timedelta(seconds=0),decimal.Decimal(0.0)) if isinstance(item,str) else item for item in lst]
#                 total_fuel = sum(item[2] for item in rmv_no)
#                 if work_done != decimal.Decimal(0.0):
#                     consump = total_fuel/work_done
#                 rmv_no.append(("Daily Overall",timedelta(seconds=sum(item[1].total_seconds() for item in rmv_no)),total_fuel,work_done,consump))
#             elif optionGroupByTwo == 'price':
#                 rmv_no = [("",decimal.Decimal(0.0),decimal.Decimal(0.0)) if isinstance(item,str) else item for item in lst]
#                 rmv_no.append(("Daily Overall",sum(item[1] for item in rmv_no),sum(item[2] for item in rmv_no)))
#             else:
#                 rmv_no = [("",timedelta(seconds=0),decimal.Decimal(0.0),decimal.Decimal(0.0),decimal.Decimal(0.0),decimal.Decimal(0.0),0) if isinstance(item,str) else item for item in lst]
#                 total_duty , total_fuel = sum(item[4] for item in rmv_no),sum(item[5] for item in rmv_no)
#                 if work_done != decimal.Decimal(0.0):
#                     consump = sum(item[2] for item in rmv_no)/work_done
#                     cost = (total_duty+total_fuel+expense) / work_done
#                 rmv_no.append(("Daily Overall",timedelta(seconds=sum(item[1].total_seconds() for item in rmv_no)),sum(item[2] for item in rmv_no),total_duty,total_fuel,expense,total_duty+total_fuel+expense,work_done,consump,cost))
#                 show_all = 6
#             if counter == 0:
#                 head_lst = [dt[0] for dt in overall_temps]
#                 print("compare")
#                 print(overall_temps)
#                 print(head_lst)
#                 if len(rmv_no) != len(overall_temps):
#                     for idx,dt_s in enumerate(rmv_no):
#                         if dt_s[0] not in head_lst:
#                             overall_temps.insert(idx,dt_s)
#                 rmv_next = overall_temps
#                 print(rmv_next)
#             else:
#                 result = []
#                 for item_1, item_2 in zip(rmv_no, rmv_next):
#                     result_tuple = []
#                     for i in range(len(item_1)):
#                         if isinstance(item_1[i], str):
#                             result_tuple.append(item_1[i])
#                         else:
#                             result_tuple.append(item_1[i] + item_2[i])
#                     result.append(tuple(result_tuple))
#                 if optionGroupByTwo not in ['price','qty']:
#                     for idx,to_date in enumerate(result):                   
#                         to_date = list(to_date)
#                         if to_date[0] != 'Daily Overall':
#                             if to_date[1] != timedelta(0) and to_date[2] != Decimal('0.00'):
#                                 to_date[3] = ((to_date[2])/Decimal(str(to_date[1].total_seconds()/3600)))
#                             else:
#                                 to_date[3] = Decimal('0.0')
#                         else:
#                             if to_date[7] != Decimal(0.0):
#                                 to_date[8] = to_date[2] / to_date[7]
#                                 to_date[9] = to_date[6] / to_date[7]
#                             else:
#                                 to_date[8] =  to_date[7]
#                                 to_date[9] =  to_date[7]
#                         result[idx] = to_date                     
#                 rmv_next = result
#             counter += 1
#             final_dct[dt] = [rmv_no,rmv_next]
#             idx_for_wd += 1
#     else:
#         return redirect(url_for('views.home'))
#     if role in ('3','4'):
#         cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
#     else:
#         cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
#     project_datas = cur.fetchall()
#     return render_template("monthly_duty.html",all_classes = all_classes,h_datas = [pj_name,dt_text,pj_code],final_dct=final_dct,message=None,flt=flt,show_all = show_all,project_datas = project_datas)

@reports.route("/get-monthly-duty",methods=['GET','POST'])
def get_monthly_duty():

    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))

    conn = db_connect()
    cur = conn.cursor()
    user_id = session["cpu_user_id"]
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]
    if not user_id:
        return redirect(url_for('auth.authenticate',typ='log'))
    elif role not in [1,2,3,4]:
        return render_template("access_error.html")
    if request.method == 'POST':
        pj_id = request.form.get("pj_id")
        date_duty = request.form.get("start")
        pj_name, pj_code = request.form.get("pj_name").split('_&_')
        optionGroupBy = request.form.get("radioOPtions")
        optionGroupByTwo = request.form.get("radioOPtionsTwo")
        yer,mnt = map(int,date_duty.split("-"))
        dt_text = datetime(yer,mnt,1).strftime("%Y %B")
        tableOptionsOne = {
            "type":["machine_type","fv.machine_type_id"],
            "class":["machine_class","fv.machine_class_id"],
            "capacity":["vehicle_machine_config","fv.machine_config_id"],
            "function":["activity_job_function","line.job_function_id"],
            "j_type":["activity_job_type","line.job_type_id"]
        } 
        table_option_one = tableOptionsOne[optionGroupBy]
        tableOptionsTwo = {"qty":["SUM(duty_hour),","ROUND(SUM(used_fuel),2),"],"price":["SUM(duty_amt),","SUM(fuel_amt),"],"consumption":["SUM(duty_hour),","ROUND(SUM(used_fuel),2),","SUM(duty_amt),","SUM(fuel_amt),","COALESCE(SUM(way),'0.0'),"]}
        table_fields_one_query = ""
        flt = 'Qty' if optionGroupByTwo == 'qty' else 'Price'
        for idx,field in enumerate(tableOptionsTwo[optionGroupByTwo]):
            if optionGroupByTwo == 'consumption' and idx == 2:
                table_fields_one_query += """ CASE
                                                WHEN SUM(duty_hour) = '0:0:0' THEN 0
                                                ELSE ROUND(SUM(used_fuel) / EXTRACT(EPOCH FROM SUM(duty_hour)) * 3600, 2)
                                            END,"""
            table_fields_one_query += field
        if pj_id == "" or date_duty == "" or pj_name == "":
            return redirect(url_for('views.home',mgs=f"Incomplete Field For Project Name - Project Code."))
        query = f""" SELECT MIN(DISTINCT(set_date)),MAX(DISTINCT(set_date)) 
                        FROM daily_activity WHERE project_id = {pj_id}
                        AND EXTRACT(YEAR FROM set_date) = {yer} AND EXTRACT(MONTH FROM set_date) = {mnt}; """
        cur.execute(query)
        start_end_dates = cur.fetchall()
        query = f""" SELECT DISTINCT(mc.name) FROM daily_activity_lines AS line
                    LEFT JOIN daily_activity AS form ON line.daily_activity_id = form.id
                    LEFT JOIN fleet_vehicle fv ON fv.id = line.machine_id
                    LEFT JOIN {table_option_one[0]} mc ON mc.id = {table_option_one[1]}
                    WHERE form.project_id = '{pj_id}' ORDER BY mc.name;"""
        cur.execute(query)
        all_classes = cur.fetchall()
        print(all_classes)
        final_dct = {}
        counter = 0
        ## get work done
        start_wd_date , end_wd_date = get_max_day(mnt,yer,True,start_end_dates)
        fst_temp = []
        if optionGroupByTwo != 'price':
            cur.execute(f"""WITH all_dates AS (
                            SELECT generate_series('{start_wd_date}'::date, '{end_wd_date}'::date, '1 day'::interval) AS date
                            )
                            SELECT
                            all_dates.date,
                            COALESCE(SUM(form.complete_sud), '0.00') AS work_done
                            FROM
                            all_dates
                            LEFT JOIN daily_activity AS form
                            ON all_dates.date = form.set_date AND form.project_id = '{pj_id}'
                            GROUP BY all_dates.date
                            ORDER BY all_dates.date;
                            """)
            idx_for_wd = 0
            all_wd_datas = cur.fetchall()
            ## get expenses
            cur.execute(f""" WITH all_dates AS (
                            SELECT generate_series('{start_wd_date}'::date, '{end_wd_date}'::date, '1 day'::interval) AS date
                            )
                            SELECT all_dates.date, COALESCE(budget.total_amt, '0.00') AS expense
                            FROM all_dates
                            LEFT JOIN (
                                SELECT form.set_date,SUM(line.amt) AS total_amt FROM income_expense AS form
                                INNER JOIN income_expense_line AS line
                                ON form.id = line.income_expense_id
                                WHERE form.project_id = '{pj_id}' AND form.income_status = 'f'
                                GROUP BY form.set_date
                            ) AS budget
                            ON all_dates.date = budget.set_date
                            ORDER BY all_dates.date; """)
            all_exp_datas = cur.fetchall()
            ## before queries
            cur.execute(f""" SELECT
                                SUM(expense_amt) AS exp,
                                SUM(work_done) AS wd
                            FROM
                                (
                                    SELECT SUM(line.amt) AS expense_amt,0 AS work_done
                                    FROM income_expense AS form INNER JOIN income_expense_line AS line
                                    ON form.id = line.income_expense_id
                                    WHERE form.set_date <= '{start_wd_date}' AND form.project_id = '{pj_id}' AND form.income_status = 'f'
                                UNION ALL
                                    SELECT 0.0 AS expense_amt,SUM(complete_sud) AS work_done
                                    FROM daily_activity AS form
                                    WHERE set_date <= '{start_wd_date}' AND project_id = '{pj_id}'
                                ) AS combined_data; """)
            fst_temp = cur.fetchall()
        cur.execute(f"""SELECT mc.name,{table_fields_one_query[:-1]} FROM daily_activity AS form
                    INNER JOIN daily_activity_lines AS line ON form.id = line.daily_activity_id
                    LEFT JOIN fleet_vehicle fv ON fv.id = line.machine_id
                    LEFT JOIN {table_option_one[0]} mc ON mc.id = {table_option_one[1]}
                    WHERE form.set_date <= '{start_wd_date}' AND form.project_id = '{pj_id}'
                    GROUP BY mc.name
                    ORDER BY mc.name;""")
        temp = cur.fetchall()
        overall_temps = get_the_previous_data(temp,fst_temp,optionGroupByTwo)
        ##
        idx_for_wd = 0            
        show_all = 2
        for dt in get_max_day(mnt,yer,False,start_end_dates):
            lst = [i[0] for i in all_classes]
            query = f"""SELECT mc.name,{table_fields_one_query[:-1]} FROM daily_activity AS form
                    INNER JOIN daily_activity_lines AS line ON form.id = line.daily_activity_id
                    LEFT JOIN fleet_vehicle fv ON fv.id = line.machine_id
                    LEFT JOIN {table_option_one[0]} mc ON mc.id = {table_option_one[1]}
                    WHERE form.set_date = '{dt}' AND form.project_id = '{pj_id}'
                    GROUP BY mc.name
                    ORDER BY mc.name;"""
            cur.execute(query)
            each_day_data = cur.fetchall()
            for day_data in each_day_data:
                lst[lst.index(day_data[0])] = day_data

            if optionGroupByTwo != 'price':
                work_done = all_wd_datas[idx_for_wd][1]
                expense = all_exp_datas[idx_for_wd][1]
            consump = decimal.Decimal(0.0)
            cost = Decimal('0.0')
            print("what is this",optionGroupByTwo)
            if optionGroupByTwo == "qty":
                for item in lst:
                    print(item)
                    if isinstance(item,str):
                        print(("",timedelta(seconds=0),decimal.Decimal(0.0)))
                rmv_no = [("",timedelta(seconds=0),decimal.Decimal(0.0)) if isinstance(item,str) else item for item in lst]
                total_fuel = sum(item[2] for item in rmv_no)
                if work_done != decimal.Decimal(0.0):
                    consump = total_fuel/work_done
                rmv_no.append(("Daily Overall",timedelta(seconds=sum(item[1].total_seconds() for item in rmv_no)),total_fuel,work_done,consump))
            elif optionGroupByTwo == 'price':
                rmv_no = [("",decimal.Decimal(0.0),decimal.Decimal(0.0)) if isinstance(item,str) else item for item in lst]
                rmv_no.append(("Daily Overall",sum(item[1] for item in rmv_no),sum(item[2] for item in rmv_no)))
            else:
                rmv_no = [("",timedelta(seconds=0),decimal.Decimal(0.0),decimal.Decimal(0.0),decimal.Decimal(0.0),decimal.Decimal(0.0),0) if isinstance(item,str) else item for item in lst]
                total_duty , total_fuel = sum(item[4] for item in rmv_no),sum(item[5] for item in rmv_no)
                if work_done != decimal.Decimal(0.0):
                    consump = sum(item[2] for item in rmv_no)/work_done
                    cost = (total_duty+total_fuel+expense) / work_done
                rmv_no.append(("Daily Overall",timedelta(seconds=sum(item[1].total_seconds() for item in rmv_no)),sum(item[2] for item in rmv_no),total_duty,total_fuel,expense,total_duty+total_fuel+expense,work_done,consump,cost))
                show_all = 6
            if counter == 0:
                head_lst = [dt[0] for dt in overall_temps]
                if len(rmv_no) != len(overall_temps):
                    for idx,dt_s in enumerate(rmv_no):
                        if dt_s[0] not in head_lst:
                            overall_temps.insert(idx,dt_s)
                rmv_next = overall_temps
            else:
                result = []
                print("next and no")
                print(rmv_no)
                print(rmv_next)
                for item_1, item_2 in zip(rmv_no, rmv_next):
                    result_tuple = []
                    for i in range(len(item_1)):
                        if isinstance(item_1[i], str):
                            result_tuple.append(item_1[i])
                        else:
                            result_tuple.append(item_1[i] + item_2[i])
                    result.append(tuple(result_tuple))
                if optionGroupByTwo not in ['price','qty']:
                    for idx,to_date in enumerate(result):                   
                        to_date = list(to_date)
                        if to_date[0] != 'Daily Overall':
                            if to_date[1] != timedelta(0) and to_date[2] != Decimal('0.00'):
                                to_date[3] = ((to_date[2])/Decimal(str(to_date[1].total_seconds()/3600)))
                            else:
                                to_date[3] = Decimal('0.0')
                        else:
                            if to_date[7] != Decimal(0.0):
                                to_date[8] = to_date[2] / to_date[7]
                                to_date[9] = to_date[6] / to_date[7]
                            else:
                                to_date[8] =  to_date[7]
                                to_date[9] =  to_date[7]
                        result[idx] = to_date                     
                rmv_next = result
            counter += 1
            final_dct[dt] = [rmv_no,rmv_next]
            idx_for_wd += 1
    else:
        return redirect(url_for('views.home'))
    if role in (3, 4):
        cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
    else:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
    project_datas = cur.fetchall()
    return render_template("monthly_duty.html",all_classes = all_classes,h_datas = [pj_name,dt_text,pj_code],final_dct=final_dct,flt=flt,show_all = show_all,project_datas = project_datas,current_role = role)

@reports.route("/job-type-function-report",methods=['GET','POST'])
def job_type_function_report():

    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))

    conn = db_connect()
    cur = conn.cursor()

    user_id = session["cpu_user_id"]
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]

    if not user_id:
        return redirect(url_for('auth.authenticate',typ='log'))
    elif role not in [1,2,3,4]:
        return render_template("access_error.html")
    if request.method == 'POST':
        pj_id = request.form.get("pj_id")
        start_date = request.form.get("start_date_for_each")
        end_date = request.form.get("end_date_for_each")
        pj_name, pj_code = request.form.get("pj_name").split('_&_')
        yer,mnt,_ = map(int,start_date.split("-"))
        dt_text = datetime(yer,mnt,1).strftime("%Y %B")
        flt = 'Qty' 
        if pj_id == "" or start_date == "" or end_date == "" or pj_name == "":
            return redirect(url_for('views.home',mgs=f"Incomplete Field For Project Name - Project Code."))
        cur.execute("""SELECT DISTINCT(ajf.name) FROM daily_activity_lines AS line
        LEFT JOIN daily_activity AS form ON line.daily_activity_id = form.id
        LEFT JOIN activity_job_function AS ajf ON line.job_function_id = ajf.id
        WHERE form.project_id = %s ORDER BY ajf.name;""",(pj_id,))
        all_classes = cur.fetchall()
        final_dct = {}           
        show_all = 2
        ##
        cur.execute(""" SELECT DISTINCT(ajt.name) FROM daily_activity AS form
                        INNER JOIN daily_activity_lines AS line ON form.id = line.daily_activity_id
                        LEFT JOIN activity_job_type ajt ON ajt.id = line.job_type_id
                        WHERE form.project_id = %s;""",(pj_id,))
        job_type_ids = cur.fetchall()
        for job_type_id in job_type_ids:
            lst = [i[0] for i in all_classes]
            query = """ SELECT ajf.name,SUM(duty_hour) AS duty_hr,ROUND(SUM(used_fuel),2) AS used_fuel, 
                        CASE
                            WHEN SUM(duty_hour) = '0:0:0' THEN 0
                            ELSE ROUND(SUM(used_fuel) / EXTRACT(EPOCH FROM SUM(duty_hour)) * 3600, 2)       
                        END AS fuel_per_hour,
                        SUM(duty_amt) AS duty_amt,SUM(fuel_amt) AS fuel_amt FROM daily_activity AS form
                    INNER JOIN daily_activity_lines AS line ON form.id = line.daily_activity_id
                    LEFT JOIN fleet_vehicle fv ON fv.id = line.machine_id
                    LEFT JOIN activity_job_function ajf ON ajf.id = line.job_function_id
                    WHERE line.job_type_id = (SELECT id FROM activity_job_type WHERE name = %s) AND form.project_id = %s AND form.set_date  BETWEEN %s AND %s
                    GROUP BY ajf.name ORDER BY ajf.name; """
            cur.execute(query,(job_type_id[0],pj_id,start_date,end_date))
            each_day_data = cur.fetchall()
            for day_data in each_day_data:
                lst[lst.index(day_data[0])] = day_data
            rmv_no = [("",timedelta(seconds=0),decimal.Decimal(0.0),decimal.Decimal(0.0),decimal.Decimal(0.0),decimal.Decimal(0.0)) if isinstance(item,str) else item for item in lst]
            total_duty , total_fuel = sum(item[4] for item in rmv_no),sum(item[5] for item in rmv_no)
            rmv_no.append(("Daily Overall",timedelta(seconds=sum(item[1].total_seconds() for item in rmv_no)),sum(item[2] for item in rmv_no),total_duty,total_fuel,total_duty+total_fuel))
            show_all = 5
            final_dct[job_type_id[0]] = rmv_no
    else:
        return redirect(url_for('views.home'))
    if role in [3,4]:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
    else:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
    project_datas = cur.fetchall()
    return render_template("monthly_duty.html",all_classes = all_classes,h_datas = [pj_name,dt_text,pj_code],final_dct=final_dct,flt=flt,show_all = show_all,project_datas = project_datas,job_type_function = True, current_role = role)

# @reports.route("/report-by-each-machine",methods=['GET','POST'])
# def report_by_each_machine():
#     user_id = request.cookies.get("cpu_user_id")
#     role = request.cookies.get("cpu_role")
#     if not user_id:
#         return redirect(url_for('auth.authenticate',typ='log'))
#     elif role not in ('1','2','3','4') or request.method != 'POST':
#         return render_template("access_error.html")
#     conn = db_connect()
#     cur = conn.cursor()
#     pj_name, pj_code = request.form.get("pj_name").split('_&_')
#     pj_id = request.form.get("pj_id")
#     start_dt = request.form.get('start_date_for_each')
#     end_dt = request.form.get('end_date_for_each')
#     print(start_dt)
#     print(end_dt)
#     print(pj_id)
#     cur.execute("SELECT pj.id,code,name FROM analytic_project_code pj INNER JOIN project_user_access access ON access.project_id = pj.id WHERE access.user_id = %s;",(int(user_id),))
#     project_datas = cur.fetchall()
#     yer , mon , sth = map(int,start_dt.split("-"))
#     if pj_id == "" or start_dt == "" or end_dt == "" or pj_name == "":
#         return redirect(url_for('views.home',mgs=f"Incomplete Field For Project Name - Project Code."))
#     cur.execute("""SELECT MIN(DISTINCT(duty_date)),MAX(DISTINCT(duty_date)) 
#                         FROM duty_odoo_report WHERE project_id = %s
#                         AND duty_date >= %s AND duty_date <= %s;""",(pj_id,start_dt,end_dt))
#     date_datas = cur.fetchall()
#     print(date_datas)
#     if date_datas == [(None,None)]:
#         return render_template('machine_by_each_duty.html',vehicles_dct={},pj_datas=[pj_name,pj_code],project_datas = project_datas)
#     start_dt_contain,end_dt_contain = get_max_day(mon,yer,True,date_datas)
#     query = """ WITH date_range AS (
#                     SELECT
#                         %s::date as start_date,
#                         %s::date as end_date
#                 ),
#                 all_dates AS (
#                     SELECT
#                         start_date + n AS date
#                     FROM
#                         date_range
#                     CROSS JOIN
#                         generate_series(0, end_date - start_date) n
#                 ),
#                 all_machines_and_dates AS (
#                     SELECT
#                         machines.machine_id,
#                         all_dates.date
#                     FROM
#                         (SELECT DISTINCT machine_id FROM duty_odoo_report WHERE project_id = %s) machines
#                     CROSS JOIN
#                         all_dates
#                 )
#                 SELECT
#                     amd.machine_id,
#                     fv.machine_name,
#                     ROUND(COALESCE(SUM(CASE WHEN data.duty_date = amd.date THEN 
# 				     CASE WHEN data.project_id = %s THEN totaluse_fuel ELSE 0.0 END 
# 					END), 0.0)/4.54,2) AS fuel_use,
#                     COALESCE(SUM(CASE WHEN data.duty_date = amd.date THEN 
# 				     CASE WHEN data.project_id = %s THEN total_hr ELSE '0:00:00' END
# 					END), '0:00:00') AS duty_use,
#                     amd.date AS date
#                 FROM
#                     all_machines_and_dates amd
#                 LEFT JOIN
#                     duty_odoo_report AS data ON amd.machine_id = data.machine_id AND data.duty_date = amd.date
#                 LEFT JOIN
#                     fleet_vehicle fv ON amd.machine_id = fv.id
#                 GROUP BY
#                     amd.machine_id, amd.date, fv.machine_name
#                 ORDER BY
#                     amd.machine_id, amd.date, fv.machine_name; """
#     cur.execute(query,(start_dt_contain,end_dt_contain,pj_id,pj_id,pj_id))
#     datas = cur.fetchall()
#     vehicles_dct = {}
#     temp_machine_name = ""
#     for idx,data in enumerate(datas):
#         machine_name = data[1]
#         if machine_name not in vehicles_dct:
#             if idx != 0:
#                 total_seconds = sum(td.total_seconds() for td in vehicles_dct[temp_machine_name][0])
#                 # Convert the total seconds to hours, minutes, and seconds
#                 total_hours, remainder = divmod(total_seconds, 3600)
#                 total_minutes, total_seconds = divmod(remainder, 60)
#                 vehicles_dct[temp_machine_name][0].append(f"{int(total_hours):02d}:{int(total_minutes):02d}:{int(total_seconds):02d}")
#                 vehicles_dct[temp_machine_name][1].append(sum(vehicles_dct[temp_machine_name][1]))
#             vehicles_dct[machine_name] = [[data[3]],[data[2]]]
#             temp_machine_name = machine_name
#         else:
#             vehicles_dct[machine_name][0].append(data[3])
#             vehicles_dct[machine_name][1].append(data[2])
#     total_seconds = sum(td.total_seconds() for td in vehicles_dct[temp_machine_name][0])
#     # Convert the total seconds to hours, minutes, and seconds
#     total_hours, remainder = divmod(total_seconds, 3600)
#     total_minutes, total_seconds = divmod(remainder, 60)
#     vehicles_dct[temp_machine_name][0].append(f"{int(total_hours):02d}:{int(total_minutes):02d}:{int(total_seconds):02d}")
#     vehicles_dct[temp_machine_name][1].append(sum(vehicles_dct[temp_machine_name][1]))
#     return render_template('machine_by_each_duty.html',vehicles_dct=vehicles_dct,date_diff = [int(start_dt_contain.split('-')[2]),int(end_dt_contain.split('-')[2]),(int(end_dt_contain.split('-')[2])-int(start_dt_contain.split('-')[2]))+1,start_dt_contain.split("-")[0] + '/' + start_dt_contain.split("-")[1]],pj_datas=[pj_name,pj_code],project_datas = project_datas)

@reports.route("/report-by-each-machine",methods=['GET','POST'])
def report_by_each_machine():

    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))

    conn = db_connect()
    cur = conn.cursor()
    user_id = session["cpu_user_id"]
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]
    if not user_id:
        return redirect(url_for('auth.authenticate',typ='log'))
    elif role not in [1,2,3,4] or request.method != 'POST':
        return render_template("access_error.html")
    pj_name, pj_code = request.form.get("pj_name").split('_&_')
    pj_id = request.form.get("pj_id")
    start_dt = request.form.get('start_date_for_each')
    end_dt = request.form.get('end_date_for_each')
    print(start_dt)
    print(end_dt)
    print(pj_id)
    if role in [3,4]:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
    else:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
    project_datas = cur.fetchall()
    yer , mon , sth = map(int,start_dt.split("-"))
    if pj_id == "" or start_dt == "" or end_dt == "" or pj_name == "":
        return redirect(url_for('views.home',mgs=f"Incomplete Field For Project Name - Project Code."))
    # cur.execute("""SELECT MIN(DISTINCT(duty_date)),MAX(DISTINCT(duty_date)) 
    #                     FROM duty_odoo_report WHERE project_id = %s
    #                     AND duty_date >= %s AND duty_date <= %s;""",(pj_id,start_dt,end_dt))
    cur.execute("""SELECT MIN(DISTINCT(set_date)),MAX(DISTINCT(set_date)) 
                        FROM daily_activity WHERE project_id = %s
                        AND set_date >= %s AND set_date <= %s;""",(pj_id,start_dt,end_dt))
    date_datas = cur.fetchall()
    print(date_datas)
    if date_datas == [(None,None)]:
        return render_template('machine_by_each_duty.html',vehicles_dct={},pj_datas=[pj_name,pj_code],project_datas = project_datas,current_role = role)
    start_dt_contain,end_dt_contain = get_max_day(mon,yer,True,date_datas,True)
    query = """ WITH date_range AS (
                    SELECT
                        %s::date as start_date,
                        %s::date as end_date
                ),
                all_dates AS (
                    SELECT
                        start_date + n AS date
                    FROM
                        date_range
                    CROSS JOIN
                        generate_series(0, end_date - start_date) n
                ),
                all_machines_and_dates AS (
                    SELECT
                        machines.machine_id,
                        all_dates.date
                    FROM
                        (
                            SELECT DISTINCT machine_id FROM daily_activity_lines AS line
                            INNER JOIN daily_activity AS form ON line.daily_activity_id = form.id
                            WHERE form.project_id = %s
                        ) machines
                    CROSS JOIN
                        all_dates
                )
                SELECT
                    amd.machine_id,
                    fv.machine_name,
                    ROUND(COALESCE(SUM(CASE WHEN data.set_date = amd.date THEN 
				     CASE WHEN data.project_id = %s THEN data.used_fuel ELSE 0.0 END 
					END), 0.0),2) AS fuel_use,
                    COALESCE(SUM(CASE WHEN data.set_date = amd.date THEN 
				     CASE WHEN data.project_id = %s THEN data.duty_hour ELSE '0:00:00' END
					END), '0:00:00') AS duty_use,
                    amd.date AS date
                FROM
                    all_machines_and_dates amd
                LEFT JOIN
                    (
                        SELECT line.machine_id,form.set_date,form.project_id,line.duty_hour,line.used_fuel FROM daily_activity_lines AS line
                        INNER JOIN daily_activity AS form ON line.daily_activity_id = form.id
                    ) AS data 
                    ON amd.machine_id = data.machine_id AND data.set_date = amd.date
                LEFT JOIN
                    fleet_vehicle fv ON amd.machine_id = fv.id
                GROUP BY
                    amd.machine_id, amd.date, fv.machine_name
                ORDER BY
                    amd.machine_id, amd.date, fv.machine_name; """
    cur.execute(query,(start_dt_contain,end_dt_contain,pj_id,pj_id,pj_id))
    datas = cur.fetchall()
    vehicles_dct = {}
    temp_machine_name = ""
    for idx,data in enumerate(datas):
        machine_name = data[1]
        if machine_name not in vehicles_dct:
            if idx != 0:
                total_seconds = sum(td.total_seconds() for td in vehicles_dct[temp_machine_name][0])
                # Convert the total seconds to hours, minutes, and seconds
                total_hours, remainder = divmod(total_seconds, 3600)
                total_minutes, total_seconds = divmod(remainder, 60)
                vehicles_dct[temp_machine_name][0].append(f"{int(total_hours):02d}:{int(total_minutes):02d}:{int(total_seconds):02d}")
                vehicles_dct[temp_machine_name][1].append(sum(vehicles_dct[temp_machine_name][1]))
            vehicles_dct[machine_name] = [[data[3]],[data[2]]]
            temp_machine_name = machine_name
        else:
            vehicles_dct[machine_name][0].append(data[3])
            vehicles_dct[machine_name][1].append(data[2])
    total_seconds = sum(td.total_seconds() for td in vehicles_dct[temp_machine_name][0])
    # Convert the total seconds to hours, minutes, and seconds
    total_hours, remainder = divmod(total_seconds, 3600)
    total_minutes, total_seconds = divmod(remainder, 60)
    vehicles_dct[temp_machine_name][0].append(f"{int(total_hours):02d}:{int(total_minutes):02d}:{int(total_seconds):02d}")
    vehicles_dct[temp_machine_name][1].append(sum(vehicles_dct[temp_machine_name][1]))
    return render_template('machine_by_each_duty.html',vehicles_dct=vehicles_dct,date_diff = [int(start_dt_contain.split('-')[2]),int(end_dt_contain.split('-')[2]),(int(end_dt_contain.split('-')[2])-int(start_dt_contain.split('-')[2]))+1,start_dt_contain.split("-")[0] + '/' + start_dt_contain.split("-")[1]],pj_datas=[pj_name,pj_code],project_datas = project_datas,current_role = role)

@reports.route("/income-expense-report",methods=['GET','POST'])
def income_expense_report_view():

    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))

    conn = db_connect()
    cur = conn.cursor()
    user_id = session["cpu_user_id"]
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]
    if not role:
        return redirect(url_for('views.home'))
    elif role not in [1,2,3,4,5] or request.method != 'POST':
        return render_template('access_error.html')
    pj_name, pj_code = request.form.get("pj_name").split('_&_')
    pj_id = request.form.get("pj_id")
    start_dt = request.form.get('start_date_for_each')
    end_dt = request.form.get('end_date_for_each')
    for_what_type = request.form.get("for_what_type")
    print(pj_name,pj_code,pj_id,start_dt,end_dt,for_what_type)
    if pj_id == "" or start_dt == "" or end_dt == "" or pj_name == "":
        return redirect(url_for('views.home',mgs=f"Incomplete Field For Project Name - Project Code."))
    extra_datas = [pj_name,pj_code,start_dt,end_dt]
    cur.execute(""" 
                    WITH PrevData AS (
                        SELECT
                        SUM(CASE WHEN form.income_status = 't' THEN line.amt ELSE 0.0 END) - SUM(CASE WHEN form.income_status = 'f' THEN line.amt ELSE 0.0 END) AS opening_balance
                        FROM income_expense_line line
                        INNER JOIN income_expense form
                        ON line.income_expense_id = form.id
                        WHERE form.set_date < %s AND form.project_id = %s
                    )
                    SELECT  COALESCE(PrevData.opening_balance,0.0),COALESCE(NowData.income,0.0),COALESCE(NowData.expense,0.0), COALESCE(( COALESCE(PrevData.opening_balance,0.0) + COALESCE(NowData.income,0.0) ) - COALESCE(NowData.expense,0.0),0.0) AS Balance
                        FROM (
                            SELECT
                                SUM(CASE WHEN form.income_status = 't' THEN line.amt ELSE 0.0 END) AS income,
                                SUM(CASE WHEN form.income_status = 'f' THEN line.amt ELSE 0.0 END) AS expense
                            FROM income_expense_line line
                            INNER JOIN income_expense form
                            ON line.income_expense_id = form.id
                            WHERE form.project_id = %s AND form.set_date BETWEEN %s AND %s
                            ) AS NowData
                        CROSS JOIN PrevData;
                    """,(start_dt,pj_id,pj_id,start_dt,end_dt))
    extra_datas.append(cur.fetchone())
    result_datas = []
    if extra_datas[1] != Decimal('0.0') and extra_datas[2] != Decimal('0.0'):
        cur.execute(""" SELECT
                            form.set_date AS date,
                            line.description,
                            line.invoice_no,
                            CASE WHEN form.income_status = 't' THEN line.amt ELSE 0.0 END AS income ,
                            CASE WHEN form.income_status = 'f' THEN line.amt ELSE 0.0 END AS expense,
                            0.0 AS balance,
                            line.remark
                        FROM
                            income_expense_line AS line
                        INNER JOIN 
                            income_expense AS form
                        ON form.id = line.income_expense_id
                        WHERE form.project_id = %s AND form.set_date BETWEEN %s AND %s
                        ORDER BY date;""",(pj_id,start_dt,end_dt))
        result_datas = cur.fetchall()
        opening_balance = extra_datas[4][0]
        for i, datas in enumerate(result_datas):
            datas = list(datas)
            datas[5] = (opening_balance + datas[3]) - datas[4]
            opening_balance = datas[5]
            result_datas[i] = tuple(datas)
        extra_datas.append(pj_id)
    table_header = ['နေ့စွဲ','အကြောင်းအရာ','ဘောင်ချာ','အဝင်','အထွက်','လက်ကျန်','မှတ်ချက်'] 
    if for_what_type == 'excel':
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet("Income Expense")
        merge_format = workbook.add_format({
            "bold": 1,
            "align": "center",
            "valign": "vcenter"
        })
        worksheet.merge_range("A1:G1",data=pj_code,cell_format=merge_format)
        worksheet.merge_range("A2:G2",data=pj_name,cell_format=merge_format) 
        worksheet.merge_range("A3:G3",data="နေ့စဉ်ငွေ အဝင်အထွက်စာရင်း",cell_format=merge_format)
        worksheet.write_row(3,0,table_header,cell_format=merge_format)  
        worksheet.write_row(4,0,[result_datas[0][0],'Opening လက်ကျန်ငွေ','','','',extra_datas[4][0],''],cell_format=merge_format)          
        for idx,lst in enumerate(result_datas,start=4):
            worksheet.write_row(idx,0,lst)
        worksheet.write_row(idx+1,0,['စုစုပေါင်း','','',extra_datas[4][1],extra_datas[4][2],extra_datas[4][3],''])
        workbook.close()
        return send_file(excel_path,as_attachment=True) 
    elif for_what_type == 'pdf':
        tr_rows = ""
        for data in result_datas:
            tr_rows += """             
                <tr>
                    <td >{}</td>
                    <td >{}</td>
                    <td >{}</td>
                    <td align="right">{:,}</td>
                    <td align="right">{:,}</td>
                    <td align="right">{:,}</td>
                    <td >{}</td>
                </tr> """.format(data[0],data[1],data[2],data[3],data[4],data[5],data[6])                   
        html_data = f""" 
                <p align='center' line-height='0.2'>{pj_name}</p>
                <p align='center' line-height='0.2'>{pj_code}</p>
                <p align='center' line-height='0.5'>{start_dt} - {end_dt}</p>
                <p align='center'></p>
                <div>
                    <table border="black">
                        <thead>
                            <tr>
                                <th>နေ့စွဲ</th>
                                <th>အကြောင်းအရာ</th>
                                <th>ဘောင်ချာ အမှတ်</th>
                                <th>အဝင်</th>
                                <th>အထွက်</th>
                                <th>လက်ကျန်ငွေ</th>
                                <th>မှတ်ချက်</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td >{result_datas[0][0]}</td>
                                <td >Opening လက်ကျန်ငွေ</td>
                                <td ></td>
                                <td ></td>
                                <td ></td>
                                <td >{float(extra_datas[4][0]):,.2f}</td>
                                <td ></td>
                            </tr> 
                            {tr_rows}
                            <tr>
                                <td >စုစုပေါင်း</td>
                                <td ></td>
                                <td ></td>
                                <td align="right">{float(extra_datas[4][1]):,.2f}</td>
                                <td align="right">{float(extra_datas[4][2]):,.2f}</td>
                                <td align="right">{float(extra_datas[4][3]):,.2f}</td>
                                <td ></td>
                            </tr>                             
                        </tbody>
                    </table>
                    <p></p><p></p>
                    <div>
                        <div>
                            <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; စာရင်းကိုင် လက်မှတ် / အမည် &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                        </div>
                        <div>
                            <span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ဆိုဒ်တာဝန်ခံ လက်မှတ် / အမည် </span>
                        </div>
                    </div>
                </div>"""
        # Execute the PHP script and pass data to it
        with open(input_path,'w',encoding='utf-8') as file:
            file.write(html_data)
        # Execute the PHP script and capture its output with 'utf-8' encoding
        result = subprocess.run([php_exe, php_script], stdout=subprocess.PIPE, text=True, encoding='utf-8')

        # Extract the captured output (the converted text)
        zawgyiText = result.stdout.strip()
        print(zawgyiText)

        with open(output_path,'r',encoding='utf-8') as file:
            datas = file.readlines()

        pdf = FPDF('P', 'mm', 'A4')

        # Add a page
        pdf.add_page()

        pdf.add_font('pyidaungsu', '', zawgyi_font_path)
        pdf.add_font('pyidaungsu', 'B', zawgyi_font_path)
        pdf.set_font('pyidaungsu', '', 10)

        pdf.write_html("".join(datas),table_line_separators=True)

        # Output the PDF to a file
        pdf.output(pdf_path)
        return send_file(pdf_path,as_attachment=True)
    if role in [3,4]:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
    else:
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
    project_datas = cur.fetchall()       
    return render_template("site-reports.html",result_datas=result_datas,extra_datas=extra_datas,project_datas = project_datas, current_role = role)
