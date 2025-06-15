from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import text

Base = declarative_base()

# Clases para las tablas de la base de datos
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
    nombres = Column(Date)
    direccion = Column(String(255))
    direccion = Column(String)
    carrera = Column(String(100))
    inscripciones = relationship("Inscripcion", back_populates="estudiante")

class Curso(Base):  # Modelo para la tabla 'curso'
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

# Conectar a la base de datos
engine = create_engine("postgresql+psycopg2://postgres:123456@localhost:5432/Exame_final")
Session = sessionmaker(bind=engine)
session = Session()

# Funciones CRUD para Profesor
def crear_profesor(nombre, departamento, salario):
    try:
        nuevo_profesor = Profesor(
            nombre=nombre,
            departamento=departamento,
            salario=salario
        )
        session.add(nuevo_profesor)
        session.commit()
        print(f"¡Profesor {nombre} creado con éxito!")
        return nuevo_profesor.id_profesor
    except Exception as e:
        session.rollback()
        print(f"¡Oops! Algo salió mal al crear el profesor: {e}")
        return None

def leer_profesor(id_profesor):
    try:
        profesor = session.query(Profesor).filter_by(id_profesor=id_profesor).first()
        if profesor:
            print(f"Profesor encontrado: {profesor.nombre}, {profesor.departamento}, Salario: {profesor.salario}")
            return profesor
        else:
            print(f"No se encontró un profesor con ID {id_profesor}")
            return None
    except Exception as e:
        print(f"¡Oops! Algo salió mal al leer el profesor: {e}")
        return None

def actualizar_profesor(id_profesor, nombre=None, departamento=None, salario=None):
    try:
        profesor = session.query(Profesor).filter_by(id_profesor=id_profesor).first()
        if profesor:
            if nombre:
                profesor.nombre = nombre
            if departamento:
                profesor.departamento = departamento
            if salario:
                profesor.salario = salario
            session.commit()
            print(f"¡Profesor con ID {id_profesor} actualizado!")
            return profesor
        else:
            print(f"No se encontró un profesor con ID {id_profesor}")
            return None
    except Exception as e:
        session.rollback()
        print(f"¡Oops! Algo salió mal al actualizar el profesor: {e}")
        return None

def eliminar_profesor(id_profesor):
    try:
        # Eliminar registros relacionados en auditoriasalarios
        session.execute(
            text("DELETE FROM auditoriasalarios WHERE id_profesor = :id_profesor"),
            {"id_profesor": id_profesor}
        )
        profesor = session.query(Profesor).filter_by(id_profesor=id_profesor).first()
        if profesor:
            session.delete(profesor)
            session.commit()
            print(f"¡Profesor con ID {id_profesor} eliminado!")
            return True
        else:
            print(f"No se encontró un profesor con ID {id_profesor}")
            return False
    except Exception as e:
        session.rollback()
        print(f"¡Oops! Algo salió mal al eliminar el profesor: {e}")
        return False
    
# Función para listar estudiantes por curso
def estudiantes_por_curso(id_curso):
    try:
        curso = session.query(Curso).filter_by(id_curso=id_curso).first()
        if not curso:
            print(f"No se encontró un curso con ID {id_curso}")
            return None
        
        estudiantes = (
            session.query(Estudiante.nombre, Inscripcion.nota)
            .join(Inscripcion, Estudiante.id_estudiante == Inscripcion.id_estudiante)
            .filter(Inscripcion.id_curso == id_curso)
            .all()
        )
        
        if estudiantes:
            print(f"Estudiantes en el curso '{curso.nombre}' (ID {id_curso}):")
            result = [{"nombre": nombre, "nota": nota} for nombre, nota in estudiantes]
            for est in result:
                print(f"- {est['nombre']} (nota: {est['nota']})")
            return result
        else:
            print(f"No hay estudiantes inscritos en el curso con ID {id_curso}")
            return []
    except Exception as e:
        print(f"¡Oops! Algo salió mal al buscar estudiantes: {e}")
        return None

if __name__ == "__main__":
    while True:
        print("\nOpciones:")
        print("1. Añadir profesor")
        print("2. Leer profesor")
        print("3. Actualizar profesor")
        print("4. Eliminar profesor")
        print("5. Listar estudiantes por curso")
        print("6. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            nombre = input("Nombre: ")
            departamento = input("Departamento: ")
            salario = float(input("Salario: "))
            crear_profesor(nombre, departamento, salario)
        elif opcion == "2":
            id_profesor = int(input("ID del profesor: "))
            leer_profesor(id_profesor)
        elif opcion == "3":
            id_profesor = int(input("ID del profesor: "))
            nombre = input("Nuevo nombre (deja vacío para no cambiar): ")
            departamento = input("Nuevo departamento (deja vacío para no cambiar): ")
            salario = input("Nuevo salario (deja vacío para no cambiar): ")
            salario = float(salario) if salario else None
            actualizar_profesor(
                id_profesor,
                nombre=nombre if nombre else None,
                departamento=departamento if departamento else None,
                salario=salario
            )
        elif opcion == "4":
            id_profesor = int(input("ID del profesor: "))
            eliminar_profesor(id_profesor)
        elif opcion == "5":
            id_curso = int(input("ID del curso: "))
            estudiantes_por_curso(id_curso)
        elif opcion == "6":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")
