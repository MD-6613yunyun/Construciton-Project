from flask import Blueprint,render_template,request,redirect,url_for,after_this_request,session
from website import db_connect
from psycopg2 import IntegrityError
from datetime import datetime,timedelta


auth = Blueprint('auth',__name__)


@auth.route("/")
@auth.route("/<typ>",methods = ['GET','POST'])
def authenticate(typ='log'):
    session.pop("cpu_username",default=None)
    session.pop("cpu_user_id",default=None)
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
                session["cpu_username"] = db_data[0][1]
                session["cpu_user_id"] = str(db_data[0][3])
                return redirect(url_for('views.home'))
            else:
                return render_template('auth.html',mgs='အီးမေးလ် (သို့) စကားဝှက် မှားယွင်းနေပါသည်။ ',typ='log')
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
                        return render_template('auth.html',mgs='ဤအီးမေလ် ဖြင့် အကောင့် ပြုလုပ်ထားခြင်း ရှိပါသည်',typ='reg')
                else:
                    return render_template('auth.html',mgs='စကားဝှက် နှင့် အတည်ပြု စကားဝှက်သည် ကိုက်ညီမှု မရှိပါ။',typ='reg')
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
                        return render_template('auth.html',mgs='စကားဝှက် နှင့် အတည်ပြု စကားဝှက်သည် ကိုက်ညီမှု မရှိပါ။',typ='forgot')
                else:
                    return render_template('auth.html',mgs='အီးမေးလ် (သို့) စကားဝှက် မှားယွင်းနေပါသည်။',typ='forgot')
    else:
        return render_template('auth.html',typ=typ,mgs=None)

@auth.route("logout")
def logout():
    session.pop('cpu_username', default=None)
    session.pop('cpu_user_id', default=None)
    return redirect(url_for('auth.authenticate'))

@auth.route("checkforget/<email>/<name>")
def checkforget(name,email):
    session.pop('cpu_username', default=None)
    session.pop('cpu_user_id', default=None)
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_auth WHERE mail = %s;",(email,))
    db_data = cur.fetchall()
    db_name = db_data[0][0] if db_data != [] else None
    if db_name == name:
        return [1]
    else:
        return [0]

@auth.route("/admin/<mgs>",methods=['GET','POST']) 
@auth.route("/admin",methods=['GET','POST'])
def admin_panel(mgs=None):
    conn = db_connect()
    cur = conn.cursor()
    print(session)
    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))
    user_id = session["cpu_user_id"]
    print(user_id)
    cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(user_id,))
    role = cur.fetchone()[0]
    if not role:
        return redirect(url_for('views.home'))
    else:
        if role != 4:
            return render_template('access_error.html')
    if request.method == 'POST':
        user_id = request.form.get("income_expense_id")
        cur.execute("SELECT users.id,users.name,users.mail,access.name,access.id FROM user_auth AS users LEFT JOIN user_access access ON users.user_access_id = access.id WHERE users.id = %s;",(user_id,))
        user_data = cur.fetchone()
        cur.execute("SELECT id,code,name FROM analytic_project_code")
        pj_datas = cur.fetchall()
        cur.execute("SELECT id,name FROM user_access;")
        access_datas = cur.fetchall()
        cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
        project_datas = cur.fetchall()
        if user_data[4] == 4:
            user_projects = project_datas
        else:
            cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
            user_projects = cur.fetchall()
        return render_template('admin_panel.html',not_tree=True,user_data=user_data,pj_datas=pj_datas,access_datas=access_datas,project_datas=project_datas,user_projects=user_projects, current_role = role)
    else:
        cur.execute("SELECT id,name,mail FROM user_auth ORDER BY name LIMIT 81;")
        all_users = cur.fetchall()
        cur.execute("SELECT count(*) FROM user_auth;")
        all_users_count = cur.fetchone()[0]
        cur.execute("SELECT pj.id,code,name FROM analytic_project_code AS pj;")
        project_datas = cur.fetchall()
    
    return render_template("admin_panel.html",all_users=all_users,total=all_users_count,project_datas=project_datas,mgs=mgs, current_role = role)

@auth.route("/add-remove-projects/<typ>",methods=['POST'])
def add_remove_pj(typ):
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()
        project_ids = request.form.get("project_ids")
        user_id = request.form.get("user_id")

        if "cpu_user_id" not in session:
            return redirect(url_for("auth.authenticate"))        

        cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(session["cpu_user_id"],))
        current_role = cur.fetchone()[0]
        if current_role != 4:
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
        if current_role != 4:
            return render_template("access_error.html")
        cur.execute("SELECT pj.id,pj.code,pj.name FROM analytic_project_code AS pj;")
        project_datas = cur.fetchall()
        cur.execute("SELECT pj.id,pj.code,pj.name FROM project_user_access access LEFT JOIN  analytic_project_code pj ON access.project_id = pj.id WHERE access.user_id = %s;",(user_id,))
        user_projects = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return render_template('admin_panel.html',not_tree=True,user_data=user_data,pj_datas=pj_datas,access_datas=access_datas,project_datas=project_datas,user_projects = user_projects, current_role = current_role)

@auth.route("/change-user-access",methods=['POST'])
def change_user_access():
    if "cpu_user_id" not in session:
        return redirect(url_for("auth.authenticate"))
    if request.method == 'POST':
        conn = db_connect()
        cur = conn.cursor()

        current_user_id = session["cpu_user_id"]
        cur.execute("SELECT user_access_id FROM user_auth WHERE id = %s;",(current_user_id,))
        current_role = cur.fetchone()[0]

        if current_role != 4:
            return render_template('access_error.html')
        
        access_id = request.form.get("access_id")
        user_id = request.form.get("user_id")

        cur.execute("UPDATE user_auth SET user_access_id = %s WHERE id = %s;",(access_id,user_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('auth.admin_panel'))
