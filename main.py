from flask import Flask, redirect, render_template, session, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from modelo.dao import Publicacion, Usuario, db, Categoria, Comentario, Interaccion
from flask_bootstrap import Bootstrap
from datetime import date, time, datetime, timedelta

app = Flask(__name__)
Bootstrap(app)

app.secret_key = 'Laschiquis'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/Blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
login_manager.login_message='Tu sesión expiró'
login_manager.login_message_category='info'


@login_manager.user_loader
def cargar_usuario(userId):
    return Usuario.query.get(int(userId))

@app.before_request
def before_request():
    session.permanent=True
    app.permanent_session_lifetime=timedelta(minutes=10)

@app.route('/cerrarSesion')
@login_required
def cerrarSesion():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if(request.method == 'POST'):   
        correo=request.form['correo']
        contrasena=request.form['contrasena']
        usuario = Usuario()
        usuario = usuario.validar(correo)
        if(usuario != None and usuario.contrasena == contrasena):
            login_user(usuario)
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', msg = "Datos incorrectos")
    else:
        return render_template('login.html')

@app.route('/publicaciones')
@login_required
def mostrarPublicacion():
    publi = Publicacion().consultaGeneral()
    return render_template('publicacion.html', publi=publi)

@app.route('/publicacionesCategoria/<int:idCategoria>')
@login_required
def publicacionesPorCategoria(idCategoria):
    publi = Publicacion.query.filter_by(categoriaId=idCategoria).all()
    categorias = Categoria().consultaGeneral()
    return render_template('publicacionesCategoria.html', publi=publi, categorias=categorias)

@app.route('/publicacionesUsuario/<int:idUsuario>')
@login_required
def publicacionesPorUsuario(idUsuario):
    publi = Publicacion.query.filter_by(usuarioId=idUsuario).all()
    usuarios = Usuario().consultaGeneral()
    return render_template('publicacionesUsuario.html', publi=publi, usuarios=usuarios)


@app.route('/consultarImgPublicacion/<int:idPublicacion>')
@login_required
def imgPublicacion(idPublicacion):
    publi = Publicacion()
    return publi.consultarImagen(idPublicacion)

@app.route('/publicacion/<int:idPublicacion>')
@login_required
def detallePublicacion(idPublicacion):
    publi = Publicacion.consultaIndividual(idPublicacion)
    likes = Interaccion.query.filter_by(publicacionId=idPublicacion, tipoInteraccion=1).count()
    dislikes = Interaccion.query.filter_by(publicacionId=idPublicacion, tipoInteraccion=0).count()
    comentarios = Comentario.query.filter_by(publicacionId=idPublicacion).all()
    return render_template('detallePublicacion.html', likes = likes, dislikes = dislikes, publi=publi, comentarios = comentarios)

@app.route('/guardarPublicacion', methods=['POST', 'GET'])
@login_required
def guardarPublicacion():
    categorias = Categoria().consultaGeneral()
    if request.method == 'POST':
        nom = request.form['nombre']
        desc = request.form['descripcion']
        foto = request.files['foto'].read()
        categoria = request.form['categoria']
        publiN = Publicacion()
        publiN.nombre = nom
        publiN.descripcion = desc
        publiN.foto = foto
        publiN.categoriaId = categoria
        publiN.usuarioId = current_user.idUsuario
        publiN.agregar()
        return redirect(url_for('mostrarPublicacion'))
    else:
        return render_template('registrarPublicacion.html', categorias = categorias)

@app.route('/editarPublicacion/<int:idPublicacion>', methods=['POST', 'GET'])
@login_required
def editarPublicacion(idPublicacion):
    publiM = Publicacion.consultaIndividual(idPublicacion)
    if request.method == 'POST':
        nom = request.form['txtNomPubli']
        desc = request.form['txtDescPubli']
        foto = request.files['fotoP'].read()
        publiM.nombre = nom
        publiM.descripcion = desc
        publiM.foto = foto
        # Agregar código para actualizar la imagen si es necesario
        publiM.editar()
        return redirect(url_for('mostrarPublicacion'))
    
    if publiM.usuarioId != current_user.idUsuario:
        flash("No tienes permiso para editar esta publicación.", "error")
        return redirect(url_for('mostrarPublicacion'))
    else:
        return render_template('editarPublicacion.html', publi=publiM)

@app.route('/eliminarPublicacion/<int:idPublicacion>', methods=['POST', 'GET'])
@login_required
def eliminarPublicacion(idPublicacion):
    publiE = Publicacion.consultaIndividual(idPublicacion)
    if request.method == 'POST':
        publiE.eliminar()
        return redirect(url_for('mostrarPublicacion'))
    
    if publiE.usuarioId != current_user.idUsuario:
        flash("No tienes permiso para eliminar esta publicación.", "error")
        return redirect(url_for('mostrarPublicacion'))
    else:
        return render_template('eliminarPublicacion.html', publi=publiE)

@app.route('/crearComentario/<int:idPub>', methods=['POST'])
@login_required
def crearComentario(idPub):
    publi = Publicacion.consultaIndividual(idPub)
    if request.method == 'POST':
        comentario = Comentario()
        comentario.publicacionId = idPub
        comentario.usuarioId = current_user.idUsuario
        comentario.contenido = request.form['comentario']
        comentario.fecha = date.today()
        comentario.agregar()
        return redirect(url_for('detallePublicacion', idPublicacion=idPub))
    return render_template('detallePublicacion.html', publi=publi)


@app.route('/registrarUsuario', methods=['POST', 'GET'])
def registrarUsuario():
    if request.method == 'POST':
        userN = Usuario()
        userN.nombre = request.form['nombre']
        userN.correo = request.form['correo']
        userN.contrasena = request.form['contrasena']
        userN.foto = request.files['foto'].read()
        userN.agregar()
        return redirect(url_for('login'))
    else:
        return render_template('registrarUsuario.html')

@app.route('/registrarCategoria', methods=['POST', 'GET'])
@login_required
def registrarCategoria():
    if request.method == 'POST':
        categoria = Categoria()
        categoria.nombre = request.form['nombre']
        categoria.agregar()
        return redirect(url_for('guardarPublicacion'))
    else:
        return render_template('registrarCategoria.html')

@app.route('/usuarios')
@login_required
def mostrarUsuarios():
    users = Usuario().consultaGeneral()
    return render_template('usuarios.html', users = users)


@app.route('/seguir_usuario/<int:idUsuario>', methods=['GET'])
@login_required
def seguirUsuario(idUsuario):
    usuario_a_seguir = Usuario.query.get(idUsuario)

    if usuario_a_seguir is not None and usuario_a_seguir != current_user:
        if not current_user.seguidores.filter_by(idUsuario=idUsuario).first():
            current_user.seguidores.append(usuario_a_seguir)
            db.session.commit()
        else:
            flash("Ya sigues a este usuario.", "info")

    return redirect(url_for('mostrarUsuarios'))

@app.route('/seguidores')
@login_required
def mostrarSeguidores():
    user = current_user  # Obtén el usuario actualmente logueado
    seguidores = user.seguidores.all()  # Obtiene todos los seguidores del usuario
    return render_template('seguidores.html', seguidores=seguidores)


@app.route('/eliminar_seguidor/<int:idUsuario>', methods=['GET'])
@login_required
def eliminarSeguidor(idUsuario):
    usuario_a_eliminar = Usuario.query.get(idUsuario)

    if usuario_a_eliminar is not None:
        current_user.seguidores.remove(usuario_a_eliminar)
        db.session.commit()
        flash("Seguidor eliminado con éxito.", "success")

    return redirect(url_for('mostrarSeguidores'))



@app.route('/interaccion/<int:idPublicacion>/<accion>', methods=['GET'])
@login_required
def interaccionPublicacion(idPublicacion, accion):
    tipo_interaccion = 0  # 0 para dislike, 1 para like

    if accion == 'like':
        tipo_interaccion = 1
    
    # Verificar si el usuario ya interactuó con esta publicación
    interaccion_previa = Interaccion.query.filter_by(publicacionId=idPublicacion, usuarioId=current_user.idUsuario).first()

    if interaccion_previa is not None:
        # Si ya existe una interacción, actualizar el tipo de interacción
        interaccion_previa.tipoInteraccion = tipo_interaccion
        db.session.commit()
    else:
        # Si no existe, crear una nueva interacción
        nueva_interaccion = Interaccion(publicacionId=idPublicacion, usuarioId=current_user.idUsuario, tipoInteraccion=tipo_interaccion)
        db.session.add(nueva_interaccion)
        db.session.commit()

    return redirect(url_for('detallePublicacion', idPublicacion = idPublicacion))

if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)
