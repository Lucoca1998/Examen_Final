from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pymongo import MongoClient
import json

# Crear la base para los modelos de SQLAlchemy
Base = declarative_base()

# Modelos para PostgreSQL (para leer los datos)
class Profesor(Base):
    __tablename__ = 'profesor'
    id_profesor = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    departamento = Column(String(100))
    salario = Column(Float)
    cursos = relationship("Curso", back_populates="profesor")

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    id_estudiante = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    fecha_nacimiento = Column(Date)
    direccion = Column(String(255))
    carrera = Column(String(100))
    inscripciones = relationship("Inscripcion", back_populates="estudiante")

class Curso(Base):
    __tablename__ = 'curso'
    id_curso = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    id_profesor = Column(Integer, ForeignKey('profesor.id_profesor'))
    semestre = Column(String(10))
    profesor = relationship("Profesor", back_populates="cursos")
    inscripciones = relationship("Inscripcion", back_populates="curso")

class Inscripcion(Base):
    __tablename__ = 'inscripcion'
    id_inscripcion = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id_estudiante'))
    id_curso = Column(Integer, ForeignKey('curso.id_curso'))
    nota = Column(Float)
    estudiante = relationship("Estudiante", back_populates="inscripciones")
    curso = relationship("Curso", back_populates="inscripciones")

# Conectar a PostgreSQL
engine = create_engine('postgresql+psycopg2://postgres:123456@localhost:5432/Exame_final')
Session = sessionmaker(bind=engine)
session = Session()

# Conectar a MongoDB Atlas
client = MongoClient('mongodb+srv://lu_styles:lucianacoca_88@cluster0.pv1rpkp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['Exame_final']

# Función para migrar datos a MongoDB
def migrar_datos():
    try:
        # Limpiar colecciones existentes en MongoDB
        db.estudiantes.drop()
        db.profesores.drop()
        db.cursos.drop()
        db.inscripciones.drop()

        estudiantes = session.query(Estudiante).all()
        for est in estudiantes:
            inscripciones = [
                {"id_curso": i.id_curso, "nota": i.nota}
                for i in session.query(Inscripcion).filter_by(id_estudiante=est.id_estudiante).all()
            ]
            db.estudiantes.insert_one({
                "_id": est.id_estudiante,
                "nombre": est.nombre,
                "fecha_nacimiento": est.fecha_nacimiento.isoformat() if est.fecha_nacimiento else None,
                "direccion": est.direccion,
                "carrera": est.carrera,
                "inscripciones": inscripciones
            })

        profesores = session.query(Profesor).all()
        for prof in profesores:
            cursos = [c.id_curso for c in session.query(Curso).filter_by(id_profesor=prof.id_profesor).all()]
            db.profesores.insert_one({
                "_id": prof.id_profesor,
                "nombre": prof.nombre,
                "departamento": prof.departamento,
                "salario": prof.salario,
                "cursos": cursos
            })

        cursos = session.query(Curso).all()
        for curso in cursos:
            db.cursos.insert_one({
                "_id": curso.id_curso,
                "nombre": curso.nombre,
                "id_profesor": curso.id_profesor,
                "semestre": curso.semestre
            })

        inscripciones = session.query(Inscripcion).all()
        for ins in inscripciones:
            db.inscripciones.insert_one({
                "_id": ins.id_inscripcion,
                "id_estudiante": ins.id_estudiante,
                "id_curso": ins.id_curso,
                "nota": ins.nota
            })

        print("¡Datos migrados a MongoDB con éxito!")
    except Exception as e:
        print(f"¡Oops! Algo salió mal al migrar los datos: {e}")

# Función para consultar estudiantes por carrera
def estudiantes_por_carrera(carrera):
    try:
        estudiantes = db.estudiantes.find({"carrera": carrera}, {"nombre": 1, "_id": 0})
        result = [est for est in estudiantes]
        if result:
            print(f"Estudiantes en la carrera '{carrera}':")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"No se encontraron estudiantes en la carrera '{carrera}'")
            return []
    except Exception as e:
        print(f"¡Oops! Algo salió mal al consultar estudiantes: {e}")
        return None

if __name__ == "__main__":
    migrar_datos()