from flask import Flask,render_template
import psycopg2
    
def db_connect():
    # Database connection details
    host = 'localhost'
    port = '9876'  # Default PostgreSQL port
    database = 'postgres'
    user = 'postgres'
    password = 'md-6613'

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            client_encoding = 'UTF8'
        )
        print('Connected to the database successfully!')
        return conn
    except psycopg2.Error as e:
        print('Error connecting to the database:', e)

def catch_db_insert_error(cur,con,queries):
    try:
        for query in queries:
            cur.execute(query)
        con.commit()
    except psycopg2.IntegrityError as e:
        print(e)
        con.rollback()
        return str(e).title()
    else:
        return None

def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = "1j2djeijfksdjfk22r90d9flk2-xspwp2-d90r8*90898(*W)"

    from .views import views
    from .reports import reports
    from .exports import exports
    from .imports import imports
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth,url_prefix='/auth')
    app.register_blueprint(reports,url_prefix='/duty')
    app.register_blueprint(exports,url_prefix='/export')
    app.register_blueprint(imports,url_prefix='/import')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('not_found.html'), 404

    return app
