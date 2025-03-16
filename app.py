import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask,redirect,url_for,render_template,request

HOSTNAME='localhost'
DATABASE='empleados'
USERNAME='jairo'
PWD='1234'
PORT=5432

load_dotenv()


app=Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(host = HOSTNAME,
                              dbname= DATABASE,
                              user = USERNAME,
                              password = PWD,
                              port = PORT)

@app.route('/empleados')
def empleado():
    cur = connection.cursor()
    sql ="SELECT e.id_empleado, e.nombre, e.calificacion, COALESCE((SELECT STRING_AGG(DISTINCT s.nombre, ', ') FROM sucursal_empleado se JOIN sucursal s ON s.id_sucursal = se.id_sucursal WHERE se.id_empleado = e.id_empleado), 'Ninguno') AS sucursales, COALESCE((SELECT STRING_AGG(DISTINCT c.nombre, ', ') FROM curso_empleado ce JOIN curso c ON c.id_curso = ce.id_curso WHERE ce.id_empleado = e.id_empleado), 'Ninguno') AS cursos FROM empleado e;"
    cur.execute(sql)
    empleados = cur.fetchall()
    connection.commit()
    return render_template('empleados/index.html',empleados = empleados)
    
@app.route('/empleados/create', methods=['GET', 'POST'])
def empleado_crear():
 if request.method == 'POST':
    _name = request.form['TxtNombre']
    _cali = request.form['Range_1']
    #print(_cali)
    sucursal = request.form.getlist('sucursal[]')
    curso = request.form.getlist('curso[]')
    sql= "insert into empleado(nombre,calificacion) values (%s,%s);"
    datos = (_name,_cali)
    cur = connection.cursor()
    cur.execute(sql,datos)
    connection.commit()
    id = get_id()
    #print(id)
    for cu in curso:
        #print(str(id) +" " + str(cu) + " " + "curso_empleado" )
        insert_in(id,cu,"curso_empleado","id_curso")
    for su in sucursal:
        #print(str(id) +" " + str(su) + " " + "sucursal_empleado" )
        insert_in(id,su,"sucursal_empleado","id_sucursal")
    return redirect('/empleados')
 else: 
    cur2 = connection.cursor()
    sql2 ="select * from sucursal;"
    cur2.execute(sql2)
    sucursales = cur2.fetchall()
    cur = connection.cursor()
    sql ="select * from curso;"
    cur.execute(sql)
    cursos = cur.fetchall()
    connection.commit()
    return render_template('empleados/create.html',sucursales=sucursales,cursos=cursos)

def insert_in(id_empleado,id,table,colu):
    curf = connection.cursor()
    sqlf= "insert into "+ table +"(id_empleado,"+colu+") values (%s,%s);"
    datosf = (id_empleado,id)
    curf.execute(sqlf,datosf)
    connection.commit()

def get_id():
    curd = connection.cursor()
    sqld= "select id_empleado from empleado order by id_empleado desc limit 1;"
    curd = connection.cursor()
    curd.execute(sqld)
    ids = curd.fetchall()
    #print(ids)
    #print(ids[0][0])
    connection.commit()
    #print("ids "+str(ids))
    return ids[0][0]

@app.route('/empleados/edit/<int:id>',methods=['GET', 'POST'])
def empleado_editar(id):   
    cur2 = connection.cursor()
    sql2 ="SELECT su.id_sucursal,su.nombre, CASE WHEN exists(select 1 from sucursal_empleado se where su.id_sucursal = se.id_sucursal and se.id_empleado = %s) THEN 'selected' ELSE '' END AS es FROM sucursal su;"
    cur2.execute(sql2,[id])
    sucursales = cur2.fetchall()
    cur3 = connection.cursor()
    sql3 ="SELECT cu.id_curso,cu.nombre, CASE WHEN exists(select 1 from curso_empleado ce where cu.id_curso = ce.id_curso and ce.id_empleado = %s) THEN 'selected' ELSE '' END AS es FROM curso cu;"
    cur3.execute(sql3,[id])
    cursos = cur3.fetchall()
    #print(cursos)
    #print(cursos[0])
    #print(cursos[0][0])
    cur = connection.cursor()
    sql= "select * from empleado where id_empleado=%s;"
    datos=(id)
    cur.execute(sql,[datos])
    empleados = cur.fetchall()
    connection.commit()
    return render_template('/empleados/edit.html',empleados = empleados,sucursales=sucursales,cursos=cursos)
    #return redirect('/empleados')


@app.route('/empleados/update',methods=['GET', 'POST'])
def empleado_update():   
    _name = request.form['TxtNombre']
    _id = request.form['id']
    _cali = request.form['Range_1']
        
    sql1= "delete from sucursal_empleado where id_empleado = %s;"
    datos1 = (_id)
    cur1 = connection.cursor()
    cur1.execute(sql1,datos1)
    connection.commit()
    
    sql2= "delete from curso_empleado where id_empleado = %s;"
    datos2 = (_id)
    cur2 = connection.cursor()
    cur2.execute(sql2,datos2)
    connection.commit()
    
    sucursal = request.form.getlist('sucursal[]')
    curso = request.form.getlist('curso[]')
    for cu in curso:
        #print(str(id) +" " + str(cu) + " " + "curso_empleado" )
        insert_in(_id,cu,"curso_empleado","id_curso")
    for su in sucursal:
        #print(str(id) +" " + str(su) + " " + "sucursal_empleado" )
        insert_in(_id,su,"sucursal_empleado","id_sucursal")
    
    sql= "update empleado set nombre = %s, calificacion =%s where id_empleado = %s;"
    datos = (_name,_cali,_id)
    cur = connection.cursor()
    cur.execute(sql,datos)
    connection.commit()
    return redirect('/empleados')

@app.route('/empleados/delete/<int:id>')
def empleado_eliminar(id):
    
    sql1= "delete from sucursal_empleado where id_empleado = %s;"
    datos1 = (id)
    cur1 = connection.cursor()
    cur1.execute(sql1,[datos1])
    connection.commit()
    
    sql2= "delete from curso_empleado where id_empleado = %s;"
    datos2 = (id)
    cur2 = connection.cursor()
    cur2.execute(sql2,[datos2])
    connection.commit()
    
    sql= "delete from empleado where id_empleado=%s;"
    datos = (id)
    cur = connection.cursor()
    cur.execute(sql,[datos])
    connection.commit()
    return redirect('/empleados')


#--------------------------------------------------------------------------

@app.route('/cursos')
def curso():
    cur = connection.cursor()
    sql ="select cu.id_curso,cu.nombre, CASE WHEN exists(select 1 from curso_empleado ce where cu.id_curso= ce.id_curso) THEN 'disabled' ELSE '' END AS ex from curso cu order by cu.id_curso;"
    cur.execute(sql)
    cursos = cur.fetchall()
    connection.commit()
    #print(empleados) 
    return render_template('cursos/index.html',cursos = cursos)

@app.route('/cursos/create', methods=['GET', 'POST'])
def curso_crear():
 if request.method == 'POST':
    _name = request.form['TxtNombre']
    sql= "insert into curso(nombre) values (%s);"
    datos = (_name)
    cur = connection.cursor()
    cur.execute(sql,[datos])
    connection.commit()
    return redirect('/cursos')

 else: 
    return render_template('cursos/create.html')

@app.route('/cursos/edit/<int:id>',methods=['GET', 'POST'])
def curso_editar(id):   
    cur = connection.cursor()
    sql= "select * from curso where id_curso=%s;"
    datos=(id)
    cur.execute(sql,[datos])
    cursos = cur.fetchall()
    connection.commit()
    return render_template('/cursos/edit.html',cursos = cursos)


@app.route('/cursos/update',methods=['GET', 'POST'])
def curso_update():   
    _name = request.form['TxtNombre']
    _id = request.form['id']
    sql= "update curso set nombre = %s where id_curso = %s;"
    datos = (_name,_id)
    cur = connection.cursor()
    cur.execute(sql,datos)
    connection.commit()
    return redirect('/cursos')

@app.route('/cursos/delete/<int:id>')
def curso_eliminar(id):
    sql= "delete from curso where id_curso=%s;"
    datos = (id)
    cur = connection.cursor()
    cur.execute(sql,[datos])
    connection.commit()
    return redirect('/cursos')

#--------------------------------------------------------------------------

@app.route('/sucursal')
def sucursal():
    cur = connection.cursor()
    sql ="select su.id_sucursal,su.nombre, CASE WHEN exists(select 1 from sucursal_empleado se where su.id_sucursal = se.id_sucursal) THEN 'disabled' ELSE '' END AS ex from sucursal su order by su.id_sucursal;"
    cur.execute(sql)
    sucursales = cur.fetchall()
    connection.commit()
    #print(empleados) 
    return render_template('sucursal/index.html',sucursales = sucursales)

@app.route('/sucursal/create', methods=['GET', 'POST'])
def sucursal_crear():
 if request.method == 'POST':
    _name = request.form['TxtNombre']
    sql= "insert into sucursal(nombre) values (%s);"
    datos = (_name)
    cur = connection.cursor()
    cur.execute(sql,[datos])
    connection.commit()
    return redirect('/sucursal')

 else: 
    return render_template('sucursal/create.html')

@app.route('/sucursal/edit/<int:id>',methods=['GET', 'POST'])
def sucursal_editar(id):   
    cur = connection.cursor()
    sql= "select * from sucursal where id_sucursal=%s;"
    datos=(id)
    cur.execute(sql,[datos])
    sucursales = cur.fetchall()
    connection.commit()
    return render_template('/sucursal/edit.html',sucursales = sucursales)


@app.route('/sucursal/update',methods=['GET', 'POST'])
def sucursal_update():   
    _name = request.form['TxtNombre']
    _id = request.form['id']
    sql= "update sucursal set nombre = %s where id_sucursal = %s;"
    datos = (_name,_id)
    cur = connection.cursor()
    cur.execute(sql,datos)
    connection.commit()
    return redirect('/sucursal')

@app.route('/sucursal/delete/<int:id>')
def sucursal_eliminar(id):
    sql= "delete from sucursal where id_sucursal=%s;"
    datos = (id)
    cur = connection.cursor()
    cur.execute(sql,[datos])
    connection.commit()
    return redirect('/sucursal')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)
