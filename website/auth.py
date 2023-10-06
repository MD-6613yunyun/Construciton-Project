from flask import Blueprint,render_template,request,redirect,url_for,after_this_request
from website import db_connect
from psycopg2 import IntegrityError
from datetime import datetime,timedelta


auth = Blueprint('auth',__name__)


@auth.route("/")
@auth.route("/<typ>",methods = ['GET','POST'])
def authenticate(typ='log'):
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()
        if typ == 'log':
            mail = request.form.get("email")
            pwd = request.form.get("password")
            print(mail,pwd)
            cur.execute("SELECT pwd,name,user_access_id,id FROM user_auth WHERE mail = %s",(mail,))
            db_data = cur.fetchall()
            db_pwd = db_data[0][0] if db_data != [] else None
            print(pwd,db_pwd)
            if db_pwd == pwd:
                @after_this_request
                def after_index(response):
                    response.set_cookie("cpu_username",db_data[0][1],expires=datetime.now() + timedelta(seconds=10))
                    response.set_cookie("cpu_role",str(db_data[0][2]),expires=datetime.now() + timedelta(seconds=10))
                    response.set_cookie("cpu_user_id",str(db_data[0][3]),expires=datetime.now() + timedelta(seconds=10))
                    return response
                return redirect(url_for('views.home'))
            else:
                return render_template('auth.html',mgs='Wrong Credentials',typ='log')
        else:
            name = request.form.get("username")
            mail = request.form.get("email")
            pwd = request.form.get("password")
            confirmPwd = request.form.get("confirmPassword")
            print(name,mail,pwd,confirmPwd)
            if typ == 'reg':
                if pwd == confirmPwd:
                    try:
                        cur.execute("INSERT INTO user_auth (name,mail,pwd,user_access_id) VALUES (%s,%s,%s,5)",(name,mail,pwd))
                        conn.commit()
                        return redirect(url_for('auth.authenticate',typ='log'))
                    except IntegrityError as err:
                        print(err)
                        return render_template('auth.html',mgs='Already Registered',typ='reg')
                else:
                    return render_template('auth.html',mgs='Unmatched Password',typ='reg')
            elif typ == 'forgot':
                cur.execute("SELECT name FROM user_auth WHERE mail = %s",(mail,))
                data = cur.fetchall()
                db_name = data[0][0] if data != [] else None
                if db_name == name:
                    if pwd == confirmPwd:
                        cur.execute("UPDATE user_auth SET pwd = %s WHERE mail = %s;",(pwd,mail))
                        conn.commit()
                        return redirect(url_for('auth.authenticate',typ='log'))
                    else:
                        return render_template('auth.html',mgs='Unmatched Password',typ='forgot')
                else:
                    return render_template('auth.html',mgs='Invalid Credentials',typ='forgot')
    else:
        print("nani")
        return render_template('auth.html',typ=typ,mgs=None)

@auth.route("logout")
def logout():
    return redirect(url_for('auth.authenticate'))

@auth.route("checkforget/<email>/<name>")
def checkforget(name,email):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_auth WHERE mail = %s;",(email,))
    db_data = cur.fetchall()
    db_name = db_data[0][0] if db_data != [] else None
    if db_name == name:
        return [1]
    else:
        return [0]
   
@auth.route("/admin",methods=['GET','POST'])
def admin_panel():
    conn = db_connect()
    cur = conn.cursor()
    role = request.cookies.get('cpu_role')
    user_id = request.cookies.get("cpu_user_id")
    if not role:
        return redirect(url_for('views.home'))
    else:
        if role != '4':
            return render_template('access_error.html')
    if request.method == 'POST':
        user_id = request.form.get("income_expense_id")
        cur.execute("SELECT users.id,users.name,users.mail,access.name FROM user_auth AS users LEFT JOIN user_access access ON users.user_access_id = access.id WHERE users.id = %s;",(user_id,))
        user_data = cur.fetchone()
        cur.execute("SELECT id,code,name FROM analytic_project_code")
        pj_datas = cur.fetchall()
        cur.execute("SELECT id,name FROM user_access;")
        access_datas = cur.fetchall()
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
        project_datas = cur.fetchall()
        return render_template('admin_panel.html',not_tree=True,user_data=user_data,pj_datas=pj_datas,access_datas=access_datas,project_datas=project_datas)
    else:
        cur.execute("SELECT id,name,mail FROM user_auth ORDER BY name LIMIT 81;")
        all_users = cur.fetchall()
        cur.execute("SELECT count(*) FROM user_auth;")
        all_users_count = cur.fetchone()[0]
        cur.execute("SELECT pj.id,code,name FROM analytic_project_code pj INNER JOIN project_user_access access ON access.project_id = pj.id WHERE access.user_id = %s;",(int(user_id),))
        project_datas = cur.fetchall()
    
    return render_template("admin_panel.html",all_users=all_users,total=all_users_count,project_datas=project_datas)

@auth.route("/add-remove-projects/<typ>",methods=['POST'])
def add_remove_pj(typ):
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()
        project_ids = request.form.get("project_ids")
        user_id = request.form.get("user_id")
        current_role = request.cookies.get("cpu_role")
        if current_role != '4':
            return render_template('access_error.html')
        if typ == 'add':
            for data in project_ids.split(","):
                cur.execute("SELECT id FROM project_user_access WHERE user_id = %s AND project_id = %s;",(user_id,data))
                if not cur.fetchone():
                    cur.execute("INSERT INTO project_user_access(user_id,project_id) VALUES(%s,%s);",(user_id,data))
        elif typ == 'remove':
            cur.execute("DELETE FROM project_user_access WHERE user_id = %s AND project_id IN %s;",(user_id,tuple(project_ids.split(","))))
        cur.execute("SELECT users.id,users.name,users.mail,access.name FROM user_auth AS users LEFT JOIN user_access access ON users.user_access_id = access.id WHERE users.id = %s;",(user_id,))
        user_data = cur.fetchone()
        cur.execute("SELECT id,code,name FROM analytic_project_code")
        pj_datas = cur.fetchall()
        cur.execute("SELECT id,name FROM user_access;")
        access_datas = cur.fetchall()
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
        project_datas = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return render_template('admin_panel.html',not_tree=True,user_data=user_data,pj_datas=pj_datas,access_datas=access_datas,project_datas=project_datas)

@auth.route("/change-user-access",methods=['POST'])
def change_user_access():
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()
        current_user_id = request.cookies.get("cpu_user_id")
        user_id = request.form.get("user_id")
        current_role = request.cookies.get("cpu_role")
        if current_role != '4':
            return render_template('access_error.html')
        access_id = request.form.get("access_id")
        cur.execute("UPDATE user_auth SET user_access_id = %s WHERE id = %s;",(access_id,user_id))
        conn.commit()
        cur.close()
        conn.close()
        @after_this_request
        def after_index(response):
            if user_id == current_user_id:
                response.set_cookie("cpu_role",str(access_id),expires=datetime.now() + timedelta(seconds=10))
            return response
        return redirect(url_for('auth.admin_panel'))