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
    