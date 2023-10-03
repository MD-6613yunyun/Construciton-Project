from flask import Blueprint,render_template,redirect,request,send_file
from website import db_connect
from psycopg2 import IntegrityError
import xlsxwriter
import os


# Get the base directory of your project
base_directory = os.path.dirname(os.path.abspath(__file__))

exports = Blueprint('exports',__name__)

@exports.route('/',methods=['GET','POST'])
def export():
    if request.method == 'POST':
        excel_file_type = request.form.get('selectedOption')
        excel_path = os.path.join(base_directory, f"static\downloadable_files\{excel_file_type.replace(' ','')}.xlsx")
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet(excel_file_type)
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter"
            }
        )
        result_data = get_data(excel_file_type)
        worksheet.write_row(0,0,result_data[0],cell_format=merge_format)
        for idx,lst in enumerate(result_data[1:],start=1):
            worksheet.write_row(idx,0,lst)
        workbook.close()
    return send_file(excel_path,as_attachment=True,download_name=f'{excel_file_type}.xlsx')

def get_data(file_type):
    conn = db_connect()
    cur = conn.cursor()
    if file_type == 'Machine List':
        query = """ SELECT rc.name,mt.name,mcf.name,vb.name,vo.name,mc.name,fv.machine_name
                        FROM fleet_vehicle fv
                        LEFT JOIN machine_type mt ON mt.id = fv.machine_type_id 
                        LEFT JOIN machine_class mc ON mc.id = fv.machine_class_id
                        LEFT JOIN res_company rc ON rc.id = fv.business_unit_id
                        LEFT JOIN fleet_vehicle_model_brand vb ON vb.id = fv.brand_id
                        LEFT JOIN vehicle_owner vo ON vo.id = fv.owner_name_id
                        LEFT JOIN vehicle_machine_config mcf ON mcf.id = fv.machine_config_id"""
        header = [('Unit','Type','Capacity','Brand','Owner','Class','Machine Name')]
    elif file_type == 'Project Code':
        query = """SELECT code,pj.name,pj_group,type, 
                    CASE WHEN com.name IS NOT NULL THEN com.name ELSE 'NULL' END,
                    finished_state
                    FROM analytic_project_code pj
                    LEFT JOIN res_company com
                    ON com.id = pj.business_unit_id"""
        header = [('Project Code','Project Name','Project Group','Project Type','Business Unit','Finished State')]
    cur.execute(query)
    data = cur.fetchall()
    return header + data

@exports.route("/download",methods=['GET','POST'])
def download_data():
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()
        pj_id = request.form.get("pj_id")
        start_dt = request.form.get("start_date_for_each")
        end_dt = request.form.get("end_date_for_each")
        db_model = request.form.get("db_model")
        if db_model == 'Income Expense Query':
            cur.execute(""" SELECT form.set_date,form.income_expense_no,pj.code,pj.name,
                CASE WHEN form.income_status = 't' THEN 'Income' ELSE 'Expense' END,
                line.description,car.machine_name,line.invoice_no,line.qty,line.price,line.amt,line.remark 
                FROM income_expense_line line 
                LEFT JOIN income_expense form 
                ON line.income_expense_id  = form.id
                LEFT JOIN analytic_project_code pj
                ON pj.id = form.project_id
                LEFT JOIN fleet_vehicle car
                ON car.id = line.machine_id
                WHERE pj.id = %s AND form.set_date BETWEEN %s AND %s
                ORDER BY form.project_id,form.set_date DESC;""",(pj_id,start_dt,end_dt))
            table_header = ['Date','No','Project Code','Project Name','Cash Type','Description','Machine Name','Invoice No','Qty','Price','Amount','Remark']
        elif db_model == 'Duty Query':
            cur.execute(""" SELECT 
                            dty.duty_date,pj.code,pj.name,fv.machine_name,dty.operator_name,dty.morg_start,dty.morg_end,
                            dty.aftn_start,dty.aftn_end,dty.evn_start,dty.evn_end,dty.total_hr,dty.hrper_rate,
                            dty.totaluse_fuel,dty.fuel_price,dty.duty_amt,dty.fuel_amt,dty.total_amt,dty.way,
                            dty.complete_feet, dty.complete_sud 
                        FROM duty_odoo_report dty
                            LEFT JOIN fleet_vehicle fv ON fv.id = dty.machine_id
                            LEFT JOIN analytic_project_code pj ON pj.id = dty.project_id 
                        WHERE pj.id = %s AND dty.duty_date BETWEEN %s AND %s
                        ORDER BY dty.duty_date ASC;""",(pj_id,start_dt,end_dt))
            table_header = ['Date','Project Code','Project Name','Machine Name','Operator','Morg. Start','Morg. End','Noon Start','Noon End','Even. Start','Even. End','Total Hour','Pay per Hour','Total Fuel','Pay per Litre','Duty Amt.','Fuel Amt.','Total Amt.','Way','Complete Feet','Complete Suds']
        elif db_model == 'Expenses Query':
            cur.execute(""" 
                        SELECT
                            exp.duty_date,pj.code,pj.name,bi.name,exp.expense_amt
                        FROM expense_prepaid AS exp
                        INNER JOIN analytic_project_code AS pj
                        ON pj.id = exp.project_id
                        INNER JOIN res_company bi
                        ON bi.id = exp.res_company_id
                        WHERE pj.id = %s AND exp.duty_date BETWEEN %s AND %s;""",(pj_id,start_dt,end_dt))
            table_header = ['Date','Project Code','Project Name','Business Unit','Expense Amount']
        elif db_model == 'Machine Activities Query':
            cur.execute(""" 
                SELECT form.set_date,pj.code,pj.name,form.daily_activity_no,car.machine_name,ajt.name,ajf.name,line.duty_hour,line.used_fuel,line.description FROM daily_activity_lines AS line 
                    LEFT JOIN daily_activity AS form ON line.daily_activity_id = form.id 
                    LEFT JOIN analytic_project_code AS pj ON pj.id = form.project_id 
                    LEFT JOIN fleet_vehicle AS car ON car.id = line.machine_id 
                    LEFT JOIN activity_job_type AS ajt ON ajt.id = line.job_type_id 
                    LEFT JOIN activity_job_function AS ajf ON ajf.id = line.job_function_id 
                WHERE pj.id = %s AND form.set_date BETWEEN %s AND %s
                ORDER BY pj.id,form.set_date;""",(pj_id,start_dt,end_dt))
            table_header = ['Date','Project Code','Project Name','Report No.','Machine Name','Job Type','Job Function','Duty Hour','Used Fuel','Description']
        elif db_model == 'Repair Activities Query':
            cur.execute(""" 
                        SELECT form.set_date,pj.code,pj.name,form.daily_activity_no,car.machine_name,line.description,line.accident_status 
                            FROM daily_activity_accident_lines AS line 
                        LEFT JOIN daily_activity AS form ON line.daily_activity_id = form.id 
                        LEFT JOIN analytic_project_code AS pj ON pj.id = form.project_id 
                        LEFT JOIN fleet_vehicle AS car ON car.id = line.machine_id
                        WHERE pj.id = %s AND form.set_date BETWEEN %s AND %s
                        ORDER BY pj.id,form.set_date;""",(pj_id,start_dt,end_dt))
            table_header = ['Date','Project Code','Project Name','Report No.','Machine Name','Description','Accident Status']
        datas = cur.fetchall()
        excel_path = os.path.join(base_directory, f"static\downloadable_files\{db_model}.xlsx")
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet(db_model)
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "valign": "vcenter"
            }
        )
        worksheet.write_row(0,0,table_header,cell_format=merge_format)
        for idx,lst in enumerate(datas,start=1):
            worksheet.write_row(idx,0,lst)
        workbook.close()
        return send_file(excel_path,as_attachment=True,download_name=f'{db_model}.xlsx')