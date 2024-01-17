from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, BLOB, ForeignKey, Date
from sqlalchemy.orm import relationship
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    idUsuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, unique=True)
    correo = db.Column(db.String, unique=True)
    contrasena = db.Column(db.String)
    foto = db.Column(db.BLOB)
    # Relación de seguidores
    seguidores = db.relationship(
        'Usuario',
        secondary='seguidores',
        primaryjoin=('seguidores.c.usuarioSeguidoId == Usuario.idUsuario'),
        secondaryjoin=('seguidores.c.usuarioSeguidorId == Usuario.idUsuario'),
        backref=db.backref('usuarios_seguidos', lazy='dynamic'),
        lazy='dynamic'
    )

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.idUsuario

    def consultaGeneral(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def consultaIndividual(self, id):
        return Usuario.query.get(id)
    
    def validar(self, correo):
        user = Usuario.query.filter(Usuario.correo == correo).first()
        return user

class Publicacion(db.Model):
    __tablename__ = 'publicaciones'
    idPublicacion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)
    descripcion = db.Column(db.String)
    foto = db.Column(db.BLOB)
    usuarioId = Column(Integer, ForeignKey("usuarios.idUsuario"))
    categoriaId = Column(Integer, ForeignKey("categorias.categoriaId"))
    comentarios = relationship('Comentario', backref='publicacion', lazy='select')
    categoria = relationship('Categoria')
    usuario = relationship('Usuario')

    def consultarImagen(self, id):
        return Publicacion().query.get(id).foto

    def consultaGeneral(self):
        return Publicacion().query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def consultaIndividual(id):
        return Publicacion().query.get(id)


class Categoria(db.Model):
    __tablename__ = 'categorias'
    categoriaId = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)
    
    def consultaGeneral(self):
        return Categoria().query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def consultaIndividual(id):
        return Categoria().query.get(id)
    


class Comentario(db.Model):
    __tablename__='comentarios' 
    comentarioId = Column(Integer, primary_key=True)
    publicacionId = Column(Integer, ForeignKey('publicaciones.idPublicacion'))
    usuarioId = Column(Integer, ForeignKey("usuarios.idUsuario"))
    contenido = Column(String)
    fecha = Column(Date)
    usuario = relationship("Usuario")
    
    def consultaGeneral(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()
    
    def editar(self):
        db.session.merge(self)
        db.session.commit()
    
    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def consultaIndividual(self, id):
        return Comentario().query.get(id)
    

class Seguidor(db.Model):
    __tablename__='seguidores' 
    relacionId = Column(Integer, primary_key=True)
    usuarioSeguidorId = Column(Integer, ForeignKey('usuarios.idUsuario'))
    usuarioSeguidoId = Column(Integer, ForeignKey("usuarios.idUsuario"))
    
    def consultaGeneral(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()
    
    def editar(self):
        db.session.merge(self)
        db.session.commit()
    
    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def consultaIndividual(self, id):
        return Seguidor().query.get(id)
    

class Interaccion(db.Model):
    __tablename__='interacciones' 
    interaccionId = Column(Integer, primary_key=True)
    publicacionId = Column(Integer, ForeignKey('publicaciones.idPublicacion'))
    usuarioId = Column(Integer, ForeignKey("usuarios.idUsuario"))
    tipoInteraccion = Column(Integer)

    def consultaGeneral(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()
    
    def editar(self):
        db.session.merge(self)
        db.session.commit()
    
    def eliminar(self):
        db.session.delete(self)
        db.session.commit()

    def consultaIndividual(self, id):
        return Interaccion().query.get(id)
    


