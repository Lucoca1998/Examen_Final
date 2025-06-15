from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from collections import defaultdict

app = Flask(__name__)

# Conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://lu_styles:lucianacoca_88@cluster0.pv1rpkp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Exame_final"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/dashboard")
def dashboard_data():
    # 1. Estudiantes por carrera
    pipeline1 = [
        {"$group": {"_id": "$carrera", "count": {"$sum": 1}}}
    ]
    carreras = list(db.estudiantes.aggregate(pipeline1))
    carreras_labels = [c["_id"] for c in carreras]
    carreras_counts = [c["count"] for c in carreras]

    # 2. Promedio de notas por curso
    pipeline2 = [
        {"$group": {"_id": "$id_curso", "prom": {"$avg": "$nota"}}}
    ]
    notas = list(db.inscripciones.aggregate(pipeline2))
    curso_ids = [n["_id"] for n in notas]
    cursos = {c["_id"]: c["nombre"] for c in db.cursos.find({"_id": {"$in": curso_ids}})}
    notas_labels = [cursos.get(i, f"Curso {i}") for i in curso_ids]
    notas_values = [n["prom"] for n in notas]

    # 3. Distribución por semestre (desde cursos inscritos)
    cursos_data = db.cursos.find()
    semestre_counter = defaultdict(int)
    for curso in cursos_data:
        semestre = curso.get("semestre", "Otro")
        insc_count = db.inscripciones.count_documents({"id_curso": curso["_id"]})
        semestre_counter[semestre] += insc_count

    semestre_labels = list(semestre_counter.keys())
    semestre_counts = list(semestre_counter.values())

    # 4. Comparación curso vs rendimiento
    rendimiento_labels = notas_labels
    rendimiento_values = notas_values

    return jsonify({
        "carreras": {"labels": carreras_labels, "counts": carreras_counts},
        "notas": {"labels": notas_labels, "values": notas_values},
        "semestres": {"labels": semestre_labels, "counts": semestre_counts},
        "rendimiento": {"labels": rendimiento_labels, "values": rendimiento_values}
    })

if __name__ == "__main__":
    app.run(debug=True)
