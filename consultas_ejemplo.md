# 1. Consulta: 
`Estudiantes mayores de 17 años` 
## SQL:
  SELECT nombre, apellido, edad
  FROM estudiantes
  WHERE edad > 17

# 2. Consulta: `Estudiantes con sus calificaciones`
## SQL:
  SELECT estudiantes.nombre, estudiantes.apellido, matriculas.calificacion, materias.nombre as materia
  FROM estudiantes
  JOIN matriculas ON estudiantes.id = matriculas.estudiante_id
  JOIN materias ON matriculas.materia_id = materias.id

# 3. Consulta: 
`Promedio de calificaciones por materia`
## SQL:
  SELECT materias.nombre, AVG(matriculas.calificacion) as promedio
  FROM materias
  JOIN matriculas ON materias.id = matriculas.materia_id
  GROUP BY materias.id, materias.nombre

# 4. Consulta:
`Estudiantes con calificación mayor a 8 en Matemáticas I`
## SQL:
  SELECT estudiantes.nombre, estudiantes.apellido, matriculas.calificacion, materias.nombre as materia
  FROM estudiantes
  JOIN matriculas ON estudiantes.id = matriculas.estudiante_id
  JOIN materias ON matriculas.materia_id = materias.id
  WHERE matriculas.calificacion > 8 AND materias.nombre = 'Matemáticas I'

# 5. Consulta: 
`Top 3 estudiantes con mejor promedio`
## SQL:
  SELECT estudiantes.nombre, estudiantes.apellido, AVG(matriculas.calificacion) as promedio
  FROM estudiantes
  JOIN matriculas ON estudiantes.id = matriculas.estudiante_id
  WHERE matriculas.calificacion IS NOT NULL
  GROUP BY estudiantes.id, estudiantes.nombre, estudiantes.apellido
  ORDER BY promedio DESC
  LIMIT 3

# 6. Consulta: 
`Cantidad de estudiantes por materia`
## SQL:
  SELECT COUNT(estudiantes.id) as cantidad, materias.nombre
  FROM estudiantes
  JOIN matriculas ON estudiantes.id = matriculas.estudiante_id
  JOIN materias ON matriculas.materia_id = materias.id
  GROUP BY materias.nombre

# 7. Consulta: 
`Estudiantes que tienen calificación menor a 7 en alguna materia`
## SQL:
  SELECT estudiantes.nombre, estudiantes.apellido
  FROM estudiantes
  JOIN matriculas ON estudiantes.id = matriculas.estudiante_id
  JOIN materias ON matriculas.materia_id = materias.id
  WHERE matriculas.calificacion < 7

# 8. Consulta: 
`Estudiantes inscritos este mes`
## SQL:
  SELECT nombre, apellido, fecha_inscripcion
  FROM estudiantes
  WHERE EXTRACT(MONTH
  FROM fecha_inscripcion) = EXTRACT(MONTH
  FROM CURRENT_DATE)

# 9. Consulta: 
`Asistencias de estudiantes con nombres de materias`
## SQL:
  SELECT materias.nombre, asistencias.fecha, asistencias.presente
  FROM asistencias
  JOIN matriculas ON asistencias.matricula_id = matriculas.id
  JOIN estudiantes ON matriculas.estudiante_id = estudiantes.id
  JOIN materias ON matriculas.materia_id = materias.id

# 10. Consulta: 
`Añadir nuevo estudiante Laura Torres de 17 años`
## SQL:
  INSERT INTO estudiantes (nombre, apellido, edad, email, telefono, direccion, fecha_inscripcion)
  VALUES ('Laura', 'Torres', 17, 'laura.torres@example.com', '123456789', 'Calle 123', CURRENT_DATE)

