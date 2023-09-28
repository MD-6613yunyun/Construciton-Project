from flask import Blueprint,render_template, request, redirect , url_for , jsonify
from website import db_connect,catch_db_insert_error
from openpyxl import load_workbook
from psycopg2 import IntegrityError
import calendar

views = Blueprint('views',__name__)

machine_type_mapping = {}
machine_class_mapping = {}
machine_owner_mapping = {}
business_unit_mapping = {}
machine_brand_mapping = {}
machine_capacity_mapping = {}
mappings = []
day_max = {'1':31,'2':31,'3':31,'4':30,'5':31,'6':30,'7':31,'8':31,'9':30,'10':31,'11':30,'12':31}


def get_first_and_last_day(month, year):
    _, last_day = calendar.monthrange(year, month)
    first_day = f"{year}-{month:02d}-01"
    last_day = f"{year}-{month:02d}-{last_day}"
    return first_day, last_day


@views.route('/')
def home():
    if request.cookies.get('username'):
        return render_template('home.html')
    return render_template('auth.html',typ='log')

@views.route("/transactions/<what>/<mgs>",methods =['GET','POST'])
@views.route("/transactions/<what>",methods =['GET','POST'])
def show_transactions(what,mgs=None):
    role = request.cookies.get('role')
    if not role:
        return redirect(url_for('views.home'))
    else:
        if int(role) not in (1,3,4):
            return render_template('access_error.html')
    conn = db_connect()
    cur = conn.cursor()
    if request.method == 'POST':
        pass
    else:
        if what == 'duty':
            query = """ SELECT 
                            dty.duty_date,pj.code,pj.name,fv.machine_name,dty.operator_name,dty.morg_start,dty.morg_end,
                            dty.aftn_start,dty.aftn_end,dty.evn_start,dty.evn_end,dty.total_hr,dty.hrper_rate,
                            dty.totaluse_fuel,dty.fuel_price,dty.duty_amt,dty.fuel_amt,dty.total_amt,dty.way,
                            dty.complete_feet, dty.complete_sud 
                        FROM duty_odoo_report dty
                            LEFT JOIN fleet_vehicle fv ON fv.id = dty.machine_id
                            LEFT JOIN analytic_project_code pj ON pj.id = dty.project_id ORDER BY dty.duty_date ASC LIMIT 81"""
            cur.execute(query)
            datas = cur.fetchall()
            cur.execute("SELECT count(*) FROM duty_odoo_report;")
            total = cur.fetchall()[0][0]
            name = "Duty Query"
        elif what == 'expense':
            query = """ SELECT
                            exp.duty_date,pj.code,pj.name,bi.name,exp.expense_amt
                        FROM expense_prepaid AS exp
                        INNER JOIN analytic_project_code AS pj
                        ON pj.id = exp.project_id
                        INNER JOIN res_company bi
                        ON bi.id = exp.res_company_id
                        LIMIT 81; """
            cur.execute(query)
            datas = cur.fetchall()
            cur.execute("SELECT count(*) FROM expense_prepaid;")
            total = cur.fetchall()[0][0]
            name = "Expenses Query"
        elif what == 'income-expense':
            cur.execute(""" 
                SELECT form.set_date,form.income_expense_no,pj.code,pj.name,
                CASE WHEN form.income_status = 't' THEN 'Income' ELSE 'Expense' END,
                line.description,line.invoice_no,line.qty,line.price,line.amt,line.remark 
                FROM income_expense_line line 
                LEFT JOIN income_expense form 
                ON line.income_expense_id  = form.id
                LEFT JOIN analytic_project_code pj
                ON pj.id = form.project_id
                ORDER BY form.project_id,form.set_date DESC;""")
            datas = cur.fetchall()
            cur.execute("SELECT count(id) FROM income_expense_line;")
            total = cur.fetchall()[0][0]
            name = "Income Expense Query"
        elif what == 'service':
            datas = []
            name = "Service Query"
            total = 70
        return render_template("transactions.html",datas=datas,total=total,name=name,message=mgs)

@views.route("/configurations/<what>/<mgs>",methods=['GET','POST'])
@views.route("/configurations/<what>",methods=['GET','POST'])
def configurations(what,mgs=None):

    conn = db_connect()
    cur = conn.cursor()

    machine_name_wildcard = pj_name_wildcard = sup_name_wildcard = "" 
    extra_datas = ["",False,0]

    if request.method == 'POST':
        machine_name = request.form.get('name-search')
        pj_name = request.form.get('project-search')
        sup_name = request.form.get('supervisor-search')

        machine_name_wildcard = machine_name.strip() if machine_name else ""
        pj_name_wildcard = pj_name.strip() if pj_name else ""
        sup_name_wildcard = sup_name.strip() if sup_name else ""

        if machine_name_wildcard != "" or pj_name_wildcard != "" or sup_name_wildcard != "":
            extra_datas[1] = True

    if what == 'machine':
        cur.execute("""SELECT fv.machine_name,mt.name,mc.name,rc.name,mcf.name,vb.name,vo.name,fv.id
                    FROM fleet_vehicle fv
                    LEFT JOIN machine_type mt ON mt.id = fv.machine_type_id 
                    LEFT JOIN machine_class mc ON mc.id = fv.machine_class_id
                    LEFT JOIN res_company rc ON rc.id = fv.business_unit_id
                    LEFT JOIN fleet_vehicle_model_brand vb ON vb.id = fv.brand_id
                    LEFT JOIN vehicle_owner vo ON vo.id = fv.owner_name_id
                    LEFT JOIN vehicle_machine_config mcf ON mcf.id = fv.machine_config_id 
                    WHERE fv.machine_name ILIKE %s
                    ORDER BY CASE WHEN fv.machine_name = %s THEN 0 ELSE 1 END
                    LIMIT 81;""",('%'+machine_name_wildcard+'%',machine_name_wildcard))
        data = cur.fetchall()
        cur.execute("SELECT count(id) FROM fleet_vehicle;")
        extra_datas[2] = cur.fetchall()[0][0]
        extra_datas[0] = "Machine List"
    elif what == 'project':
        cur.execute("""SELECT 
                    code,pj.name,pj_group,type,bi.name,finished_state,pj.id
                    FROM analytic_project_code pj 
                    LEFT JOIN res_company bi
                    ON pj.business_unit_id = bi.id
                    WHERE code ILIKE %s OR pj.name ILIKE %s
                    ORDER BY CASE WHEN pj.name = %s THEN 0 WHEN pj.code = %s THEN 0 ELSE 1 END
                    LIMIT 81;""",('%'+pj_name_wildcard+'%','%'+pj_name_wildcard+'%',pj_name_wildcard,pj_name_wildcard))
        data = cur.fetchall()
        cur.execute("""SELECT count(id) FROM analytic_project_code;""")
        extra_datas[2] = cur.fetchall()[0][0]
        extra_datas[0] = "Project List"
    elif what == 'details':
        data = {}
        extra_datas[0] = "Machine Details"
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

    elif what == 'project-stat':
        cur.execute(""" SELECT pj.id , pj.name , pj.code , emp.name FROM project_statistics stat 
                    INNER JOIN analytic_project_code pj ON stat.project_id = pj.id 
                    INNER JOIN employee emp ON emp.id = stat.supervisor_id
                    WHERE pj.code ILIKE %s OR pj.name ILIKE %s OR emp.name ILIKE %s
                    ORDER BY CASE WHEN pj.name = %s THEN 0 WHEN pj.code = %s THEN 0 WHEN emp.name = %s  THEN 0 ELSE 1 END
                    LIMIT 81;""",('%'+pj_name_wildcard+'%','%'+pj_name_wildcard+'%','%'+sup_name_wildcard+'%',pj_name_wildcard,pj_name_wildcard,sup_name_wildcard))
        
        data = cur.fetchall()
        cur.execute("""SELECT count(id) FROM project_statistics;""")
        extra_datas[2] = cur.fetchall()[0][0]
        extra_datas[0] = "Project Statistics"

    cur.close()
    conn.close()

    return render_template('configurations.html',message=mgs,datas=data,extra_datas = extra_datas)
        
def get_necessary_data_for_imports():
    global mappings,machine_brand_mapping,machine_capacity_mapping,machine_class_mapping,machine_owner_mapping,machine_type_mapping,business_unit_mapping
    
    conn = db_connect()
    cur = conn.cursor()
    
    cur.execute("SELECT id,name FROM machine_type")
    datas = cur.fetchall()
    machine_type_mapping = {item[1]: item[0] for item in datas}

    cur.execute("SELECT id,name FROM machine_class")
    datas = cur.fetchall()
    machine_class_mapping = {item[1]: item[0] for item in datas}

    cur.execute("SELECT id,name FROM res_company")
    datas = cur.fetchall()
    business_unit_mapping = {item[1]: item[0] for item in datas}

    cur.execute("SELECT id,name FROM vehicle_machine_config")
    datas = cur.fetchall()
    machine_capacity_mapping = {item[1]: item[0] for item in datas}

    cur.execute("SELECT id,name FROM fleet_vehicle_model_brand")
    datas = cur.fetchall()
    machine_brand_mapping = {item[1]: item[0] for item in datas}

    cur.execute("SELECT id,name FROM vehicle_owner")
    datas = cur.fetchall()
    machine_owner_mapping = {item[1]: item[0] for item in datas}

    mappings = [business_unit_mapping,machine_type_mapping,machine_capacity_mapping,machine_brand_mapping,machine_owner_mapping,machine_class_mapping]


@views.route("/upload-machine-details",methods=['GET','POST'])
def upload_machine_details():
    mgs = None
    if request.method == 'POST':
        upload_file = request.files["upload_excel_machine_details"]
        excel_file_type = request.form.get('selectedOption')
        what_dct = {"Machine List":"machine","Project Code":"project"}
        if upload_file.filename != '' and upload_file.filename.endswith(".xlsx"):
            workbook = load_workbook(filename=upload_file,data_only=True,read_only=True)
            # Select the worksheet to read from
            try:
                worksheet = workbook[excel_file_type]  # Replace 'Sheet1' with the actual sheet name
            except:
                mgs = f"The sheet name of your Imported Excel file doesn't match with <strong>{excel_file_type}<&#47;strong>"
                return redirect(url_for('views.configurations',what=what_dct.get(excel_file_type),mgs=mgs))
            # GET
            get_necessary_data_for_imports()
            # Iterate over rows in the worksheet
            conn = db_connect()
            cur = conn.cursor()

            if excel_file_type == "Machine Details":
                machine_type_query = """INSERT INTO machine_type (name) VALUES """
                machine_class_query = """INSERT INTO machine_class (name) VALUES """
                unit_query = """INSERT INTO res_company (name) VALUES """
                capacity_query = """INSERT INTO vehicle_machine_config (name) VALUES """
                brand_query = """INSERT INTO fleet_vehicle_model_brand (name) VALUES """
                owner_query = """INSERT INTO vehicle_owner (name) VALUES """

                for row in worksheet.iter_rows(min_row=2):  # Start from the second row (adjust as needed)
                    # Access data for each cell in the row
                    machine_type_query += f"""('{row[1].value}'),""" if row[1].value else ""
                    machine_class_query += f"""('{row[5].value}'),""" if row[5].value else ""
                    unit_query += f"""('{row[0].value}'),""" if row[0].value else ""
                    capacity_query += f"""('{row[2].value}' ),""" if row[2].value else ""
                    brand_query += f"""('{row[3].value}'),""" if row[3].value else ""
                    owner_query += f"""('{row[4].value}'),""" if row[4].value else ""

                queries = [machine_type_query[:-1],machine_class_query[:-1],unit_query[:-1],capacity_query[:-1],brand_query[:-1],owner_query[:-1]]
                mgs = catch_db_insert_error(cur,conn,queries)
            elif excel_file_type == "Machine List":
                machine_list_insert_query = """INSERT INTO fleet_vehicle 
                (business_unit_id,machine_type_id,machine_config_id,brand_id,owner_name_id,machine_class_id,machine_name) VALUES """
                for row_counter , row in enumerate(worksheet.iter_rows(min_row=2),start=1):  # Start from the second row (adjust as needed)        
                    stng = "("
                    for idx,mapping in enumerate(mappings):
                        idd = mapping.get(row[idx].value)
                        if idd is None:
                            mgs = f"Unknown Field or Unknow Value at <strong class='text-danger'>  Row : ({row_counter}) {row[idx].value} <&#47;strong> "
                            return redirect(url_for('views.machine_details',mgs=mgs))
                        else:
                            stng += f"{idd},"
                    machine_list_insert_query += stng + f"'{row[6].value.strip()}'),"
                print(machine_list_insert_query)
                mgs = catch_db_insert_error(cur,conn,[machine_list_insert_query[:-1]+ 'ON CONFLICT (machine_name) DO NOTHING;']) 
            elif excel_file_type == 'Work Done':
                machine_list_insert_query = """ INSERT INTO  project_each_day_work_done 
                (project_id,duty_date,work_done,constraint_unique_text) VALUES """
                for row_counter, row in enumerate(worksheet.iter_rows(min_row=2),start=1):
                    if not row[0].value or not row[1].value or row[2].value is None:
                        return redirect(url_for('views.machine_details',mgs=f"<strong>Blank Field at ROW No. {row_counter}<&#47;strong>"))
                    else:
                        cur.execute("SELECT id FROM analytic_project_code WHERE code = %s",(row[1].value,))
                        id = cur.fetchall()
                        if not id:
                            return redirect(url_for('views.machine_details',mgs=f"<strong>Project Code {row[1].value} doesn't exit!!<&#47;strong>"))   
                        unique_constraint_for_work_done = row[0].value.strftime('%Y-%m-%d') + "|" + str(id[0][0])
                        machine_list_insert_query += f"('{id[0][0]}','{row[0].value}','{row[2].value}','{unique_constraint_for_work_done}'),"
                mgs = catch_db_insert_error(cur,conn,[machine_list_insert_query[:-1] + 'ON CONFLICT (constraint_unique_text) DO NOTHING;'])                
            elif excel_file_type == "Project Code":
                machine_list_insert_query = """INSERT INTO analytic_project_code
                (code,pj_group,name,type,business_unit_id) VALUES """
                for row_counter , row in enumerate(worksheet.iter_rows(min_row=2),start=1):
                    if not row[0].value  or not row[1].value  or  not row[2].value or not row[3].value or not row[4].value:
                        mgs = f"<strong>Blank Field at ROW No. {row_counter}<&#47;strong>"
                        return redirect(url_for('views.machine_details',mgs=mgs))
                    else:
                        unit = mappings[0].get(row[4].value)
                        if not unit:
                            return redirect(url_for('views.machine_details',mgs=f"<strong>Invalid Buinsess Unit <{row[4].value}> at ROW No. {row_counter}<&#47;strong>"))
                        machine_list_insert_query += f"('{row[0].value}','{row[1].value}','{row[2].value}','{row[3].value}','{unit}'),"
                machine_list_insert_query = machine_list_insert_query[:-1] + 'ON CONFLICT (code) DO NOTHING;'
                mgs = catch_db_insert_error(cur,conn,[machine_list_insert_query]) 

            workbook.close()
            cur.close()
            conn.close()

            return redirect(url_for('views.configurations',what=what_dct.get(excel_file_type),mgs=mgs))
        else:    
            return redirect(url_for('views.configurations',what=what_dct.get(excel_file_type,"project"),mgs="Invalid File Type"))
    else:
        return render_template("home.html")

@views.route("/get-pj-datas")
def get_pj_datas():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("SELECT id ,name , code FROM analytic_project_code")
    pj_datas = cur.fetchall()
    
    return jsonify(pj_datas)


@views.route("upload-duty",methods=['GET','POST'])
def upload_duty():
    mgs = None
    if request.method == 'POST':
        upload_file = request.files['upload_duty_data']
        month = request.form.get("selectedMonth")
        year = request.form.get("selectedYear")
        query = request.form.get('selectedQuery')
        what_dct = {"Duty Query":'duty',"Expenses Query":'expense','Services Query':"service"}
        if upload_file.filename != '' and upload_file.filename.endswith(".xlsx"):
            workbook = load_workbook(filename=upload_file,read_only=True,data_only=True)
            # Select the worksheet to read from
            try:
                worksheet = workbook[query]  # Replace 'Sheet1' with the actual sheet name
            except:
                return redirect(url_for('views.show_transactions',what=what_dct.get(query,'duty'),mgs=f"Sheet Name must be  {query}"))     
            # Iterate over rows in the worksheet
            conn = db_connect()
            cur = conn.cursor()

            if query == 'Duty Query':
                insert_statement_query = """ INSERT INTO duty_odoo_report 
                (project_id,duty_date,machine_id,operator_name,morg_start,morg_end,aftn_start,aftn_end,evn_start,evn_end,total_hr,totaluse_fuel,hrper_rate,fuel_price,duty_amt,fuel_amt,way,complete_feet,complete_sud)  VALUES """
                for row_counter , row in enumerate(worksheet.iter_rows(min_row=2),start=2):
                    # 3,4,10,11,14,15,16,17,18,19,20,30,33,37,38,43,46
                    # 3,4,10,11,27,28,29,39,31,32,33,43,46,52,53,56,59
                    if row[3].value is None or row[4].value is None or row[10].value is None or row[11].value is None or row[27].value is None or row[28].value is None or row[29].value is None or row[30].value is None or row[31].value is None or row[32].value is None or row[33].value is None or row[46].value is None or row[50].value is None or row[51].value is None:
                        return redirect(url_for('views.show_transactions',what=what_dct.get(query,'duty'),mgs=f"Invalid Field or Blank Field at Row - {row_counter}"))     
                    else:
                        if year != 'all':
                            if row[4].value.month != int(month) and row[4].value.year != int(year):
                                return redirect(url_for('views.duty_query',mgs=f"Selected date doen't match with Imported date at Row - {row_counter}"))
                        com_feet = row[43].value if row[43].value else 0.00
                        way = row[56].value if row[56].value else 0
                        com_sud = row[59].value if row[59].value else 0.00
                        cur.execute("SELECT id FROM analytic_project_code WHERE code = %s",(row[3].value,))
                        pj_id = cur.fetchone()
                        pj_id = pj_id[0] if pj_id else pj_id
                        cur.execute("SELECT id FROM fleet_vehicle WHERE machine_name = %s",(row[10].value,))
                        machine_id = cur.fetchone()
                        machine_id = machine_id[0] if machine_id else machine_id
                        if not machine_id or not pj_id:
                            mgs = f"Invalid field or Unknown Field at Row - {row_counter} <br>"
                            mgs = mgs + f"Project Code - {row[3].value.replace('/','&#47;')} doesnt't match with system <br>" if not pj_id else mgs
                            mgs = mgs + f"Machine Name - {row[10].value.replace('/','&#47;')} doesnt't match with system <br>" if not machine_id else mgs
                            return redirect(url_for('views.show_transactions',what=what_dct.get(query,'duty'),mgs=mgs))
                        insert_statement_query += f""" ({pj_id},'{row[4].value.strftime("%Y-%m-%d")}',{machine_id},'{row[11].value}','{row[27].value}','{row[28].value}','{row[29].value}','{row[30].value}','{row[31].value}','{row[32].value}','{row[33].value}','{row[46].value}','{row[50].value}','{row[51].value}',{row[52].value},{row[53].value},'{way}','{com_feet}','{com_sud}'),"""
                table = 'duty_odoo_report'
            elif query == 'Expenses Query':
                insert_statement_query = """ INSERT INTO expense_prepaid 
                (res_company_id,project_id,duty_date,expense_amt) VALUES """
                cur.execute("SELECT name,id from res_company;")
                unit_ids = cur.fetchall()
                unit_ids_dct = {data[0]:data[1] for data in unit_ids}
                for row_counter , row in enumerate(worksheet.iter_rows(min_row=2),start=2):
                    if row[5].value is None or row[8].value is None or row[10].value is None:
                        return redirect(url_for('views.duty_query',mgs=f"Invalid field or Blank field at Row - {row_counter}"))
                    if year != 'all':
                        if row[10].value.month != int(month) and row[10].value.year != int(year):
                            return redirect(url_for('views.duty_query',mgs=f"Selected date doen't match with Imported date at Row - {row_counter}"))
                    unit_id = unit_ids_dct.get(row[5].value.strip())
                    cur.execute("SELECT id FROM analytic_project_code WHERE code = %s",(row[8].value.strip(),))
                    id = cur.fetchall()
                    if unit_id and id != []:
                        if row[38].value.strip() == 'P&L':
                            expenses = row[22].value if row[22].value else 0
                            insert_statement_query += f""" ('{unit_id}','{id[0][0]}','{row[10].value}',{expenses}),"""
                    else:
                        return redirect(url_for('views.show_transactions',what=what_dct.get(query,'duty'),mgs=f"Unknown Project Code or Unknown Unit at Row - {row_counter}"))                        
                table = "expense_prepaid"
            elif query == "Services Query":
                insert_statement_query = """ INSERT INTO service_datas (service_date,business_unit_id,machine_id,
                category_id,parts_price,parts_qty) VALUES """
                cur.execute("SELECT machine_name,id FROM fleet_vehicle;")
                vehicle_datas = {data[0]:data[1] for data in cur.fetchall()}
                cur.execute("SELECT name,id FROM res_company;")
                bi_datas = {data[0]:data[1] for data in cur.fetchall()}
                cur.execute("SELECT name,id FROM service_category;")
                category_datas = {data[0]:data[1] for data in cur.fetchall()}
                for row_counter , row in enumerate(worksheet.iter_rows(min_row=2),start=2):
                    print(row[0].value,row[2].value,row[3].value,row[4].value,row[5].value,row[6].value)
                    if None in (row[0].value,row[2].value,row[3].value,row[4].value,row[5].value,row[6].value) or row[2].value not in bi_datas or row[3].value not in vehicle_datas:
                        print("Blank Field")
                    category_id = row[4].value.strip()
                    if not category_datas.get(category_id):
                        cur.execute("INSERT INTO service_category(name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;",(category_id,))
                        category_id = cur.fetchall()[0][0]
                    insert_statement_query += f""" ('{row[0].value}','{bi_datas.get(row[2].value.strip())}','{vehicle_datas.get(row[3].value.strip())}','{category_id}','{row[5].value.strip()}','{row[6].value.strip()}') """
            print(insert_statement_query)
            if year != 'all':
                s_date , e_date = get_first_and_last_day(int(month),int(year))
                cur.execute("""DELETE FROM {} WHERE duty_date BETWEEN '{}' AND '{}' """.format(table,s_date,e_date))
                conn.commit()
            mgs = catch_db_insert_error(cur,conn,[insert_statement_query[:-1]])
            cur.close()
            conn.close()
        else:
            mgs = "Invalid File Type.."
    return redirect(url_for('views.show_transactions',what=what_dct.get(query,'duty'),mgs=mgs))

@views.route("/delete-data/<db>/<id>")
def delete_data(db,id):
    conn = db_connect()
    cur = conn.cursor()
    mgs = 'Success'
    try:
        cur.execute(f'DELETE FROM {db} WHERE id = {id}')
        conn.commit()
    except IntegrityError as err:
        print(err)
        mgs = err
        conn.rollback()
    return mgs    


@views.route("/edit-data/<db>/<id>/<stng>")
def edit_data_in_db(db,id,stng):
    queries_values = { 'project_statistics' : """ UPDATE project_statistics SET supervisior = %s,estimate_feet = %s,
                                                    will_sud = %s,estimate_sud = %s,estimate_duty = %s,estimate_fuel = %s,
                                                    estimate_expense = %s WHERE id = %s;""",
                        'fleet_vehicle' : """ UPDATE fleet_vehicle SET business_unit_id = %s,machine_type_id = %s,
                                                machine_config_id = %s,brand_id = %s,owner_name_id = %s,
                                                machine_class_id = %s,machine_name = %s WHERE id = %s;""",
                        'analytic_project_code' : """ UPDATE analytic_project_code SET code = %s,name = %s,pj_group = %s,
                                                type = %s,business_unit_id = %s , finished_state = %s WHERE id = %s"""
    }
    datas = stng.split(",")
    lst = []
    if db == 'fleet_vehicle':
        "business_unit_id,machine_type_id,machine_config_id,brand_id,owner_name_id,machine_class_id,machine_name"
        lst = [datas[3],datas[1],datas[4],datas[5],datas[6],datas[2]]
        for idx,mapping in enumerate(mappings):
            dt = mapping.get(lst[idx].replace('thisIsSlash','/'))
            if dt is None:
                return f"""["Error","{lst[idx]}"]"""
            lst[idx] = dt
        lst.append(datas[0].replace('thisIsSlash','/'))
        lst.append(int(id))
    elif db == 'analytic_project_code':
        lst = list(datas)
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM res_company WHERE name = '{lst[4].replace('thisIsSlash','/')}';")
        unit = cur.fetchall()
        if lst[5] not in ['True','False'] or unit == []:
            return f"""["Error","{lst[5]} | {lst[4]}"]"""
        lst[4] = str(unit[0][0]) 
        print(lst)
        lst = [dt.replace('thisIsSlash','/') for dt in lst]

    inserted_values_query = {'project_statistics':tuple(datas)+(id,),
                            'fleet_vehicle':tuple(lst),
                            'analytic_project_code':tuple(lst)+(id,)}
    conn = db_connect()
    cur = conn.cursor()
    print(queries_values[db],inserted_values_query[db])
    try:
        cur.execute(queries_values[db],inserted_values_query[db])
        conn.commit()
    except IntegrityError as err:
        print(err)
        conn.rollback()
    cur.close()
    conn.close()
    return """["Success"]"""

@views.route("/offset-display/<for_what>/<ofset>")
def offset_display(for_what,ofset):
    queries_dct = {
        "pj" : f""" SELECT pj.code,pj.name,pj.pj_group,pj.type,
                    com.name,pj.finished_state
                    FROM analytic_project_code pj
                    INNER JOIN res_company com
                    ON com.id = pj.business_unit_id
                    LIMIT 81 OFFSET {ofset};""",
        "dty": f""" SELECT 
                    dty.duty_date,pj.code,pj.name,fv.machine_name,dty.operator_name,dty.morg_start,dty.morg_end,
                    dty.aftn_start,dty.aftn_end,dty.evn_start,dty.evn_end,dty.total_hr,dty.hrper_rate,
                    dty.totaluse_fuel,dty.fuel_price,dty.duty_amt,dty.fuel_amt,dty.total_amt,dty.way,
                    dty.complete_feet, dty.complete_sud 
                    FROM duty_odoo_report dty
                    LEFT JOIN fleet_vehicle fv ON fv.id = dty.machine_id
                    LEFT JOIN analytic_project_code pj ON pj.id = dty.project_id ORDER BY dty.duty_date ASC 
                    LIMIT 81 OFFSET {ofset}""",
        "machine" : f"""SELECT fv.machine_name,mt.name,mc.name,rc.name,mcf.name,vb.name,vo.name 
                        FROM fleet_vehicle fv
                        LEFT JOIN machine_type mt ON mt.id = fv.machine_type_id 
                        LEFT JOIN machine_class mc ON mc.id = fv.machine_class_id
                        LEFT JOIN res_company rc ON rc.id = fv.business_unit_id
                        LEFT JOIN fleet_vehicle_model_brand vb ON vb.id = fv.brand_id
                        LEFT JOIN vehicle_owner vo ON vo.id = fv.owner_name_id
                        LEFT JOIN vehicle_machine_config mcf ON mcf.id = fv.machine_config_id 
                        LIMIT 81 OFFSET {ofset}""",
        "expense" : f"""  SELECT
                            exp.duty_date,pj.code,pj.name,bi.name,exp.expense_amt
                            FROM expense_prepaid AS exp
                            INNER JOIN analytic_project_code AS pj
                            ON pj.id = exp.project_id
                            INNER JOIN res_company bi
                            ON bi.id = exp.res_company_id
                            LIMIT 81 OFFSET {ofset};"""
    }
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(queries_dct[for_what])
    result_datas = cur.fetchall()
    if for_what == 'dty':
        result_datas = [
            (str(d[0]), d[1], d[2], d[3], d[4], str(d[5]), str(d[6]), str(d[7]), str(d[8]), str(d[9]), str(d[10]),
            str(d[11]), str(d[12]), str(d[13]), str(d[14]), str(d[15]), str(d[16]), str(d[17]), d[18], str(d[19]), 
            str(d[20])) for d in result_datas
            ]
    return jsonify(result_datas)


@views.route("/get-api/<for_what>/<data>")
def call_api(for_what,data:str):
    conn = db_connect()
    cur = conn.cursor()
    data = data.replace("thisIsSlash","/")
    if for_what == 'project-stat':
        cur.execute("""  
        SELECT
            pj.id,emp.name,pj.name,stat.location,stat.pj_start_date,sup.name
        FROM project_statistics AS stat
            INNER JOIN analytic_project_code AS pj
            ON stat.project_id = pj.id
            INNER JOIN employee AS emp
            ON stat.ho_acc_id = emp.id
            INNER JOIN employee AS sup
            ON stat.supervisor_id = sup.id 
        WHERE pj.code = %s or pj.name = %s;""",(data,data))
    elif for_what == 'project-check-for-stats':
        cur.execute("SELECT pj.id FROM analytic_project_code AS pj LEFT JOIN project_statistics AS stat ON pj.id = stat.project_id WHERE stat.project_id is NULL AND (name = %s or code = %s) LIMIT 1;",(data,data))
    elif for_what == 'machine-check':
        cur.execute(""" WITH LatestStartTime AS (
                            SELECT
                                machine_id,
                                MAX(start_time) AS latest_start_time
                            FROM
                                machines_history
                            WHERE
                                start_time IS NOT NULL
                            GROUP BY
                                machine_id
                            )
                        SELECT
                            car.id AS machine_id,
                            car.machine_name,
                            tp.name AS machine_type
                        FROM
                            fleet_vehicle AS car
                        LEFT JOIN
                            LatestStartTime AS latest_start
                        ON car.id = latest_start.machine_id
                        LEFT JOIN
                            machines_history AS history
                        ON car.id = history.machine_id
                        LEFT JOIN
                            machine_type AS tp
                            ON car.machine_type_id = tp.id
                        WHERE (
                            (history.start_time IS NULL AND history.end_time IS NULL)
                        OR
                            (history.start_time = latest_start.latest_start_time AND history.end_time IS NOT NULL) )
                        AND car.machine_name = %s LIMIT 1;""",(data,))
    elif for_what == 'employee-group-check':
        cur.execute("SELECT id,name FROM employee_group WHERE name = %s;",(data,))
    elif for_what == 'accountant-supervisor-check':
        sup , acc = data.split("~|~")
        result = []
        cur.execute("SELECT emp.id FROM employee emp INNER JOIN employee_group emp_gp ON emp.employee_group_id = emp_gp.id WHERE emp_gp.name = 'SUPERVISOR' AND LOWER(emp.name) = %s LIMIT 1;",(sup.lower(),))
        result.append(cur.fetchone())
        cur.execute("SELECT emp.id FROM employee emp INNER JOIN employee_group emp_gp ON emp.employee_group_id = emp_gp.id WHERE emp_gp.name = 'ACCOUNTANT' AND LOWER(emp.name) = %s LIMIT 1;",(acc.lower(),))
        result.append(cur.fetchone())
        return jsonify(result)
    elif for_what == 'delete-machines-histrory':
        cur.execute("DELETE FROM machines_history WHERE id = %s RETURNING id;",(data,))
        conn.commit()
    elif for_what == 'delete-employee-group-history':
        cur.execute("DELETE FROM employee_group_project WHERE id = %s RETURNING id;",(data,))
        conn.commit()
    elif for_what == 'transfer-machine-to-another-project':
        cur.execute("UPDATE machines_history SET end_time = now() WHERE id = %s;")
        cur.execute("INSERT INTO machines_history (project_id,machine_id,start_time) VALUES (%s,%s,%s);",())
    elif for_what == 'transfer_machine_project':
        his_id , project_id , start_time , machine_id = data.split("~~")
        try:
            cur.execute("UPDATE machines_history SET end_time = %s WHERE id = %s;",(start_time,his_id))
            cur.execute("INSERT INTO machines_history (project_id,start_time,machine_id) VALUES (%s,%s,%s);",(project_id,start_time,machine_id))
            conn.commit()
        except IntegrityError as err:
            print(err)
        return ""
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result)