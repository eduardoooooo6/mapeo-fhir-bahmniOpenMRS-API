# API de Interoperabilidad FHIR – Bahmni  
**SIMSADI-UV**

## Descripción
Esta API implementa una **capa de interoperabilidad** entre un servidor **HAPI FHIR** y **Bahmni/OpenMRS**, permitiendo la transferencia **bidireccional** de información de pacientes mediante el estándar **FHIR (HL7)**.

La API:

- Recibe recursos **Patient** en formato FHIR  
- Realiza mapeo estructural y semántico hacia el modelo de datos de **Bahmni**  
- Envía pacientes desde **Bahmni/OpenMRS** hacia **HAPI FHIR**  
- Implementa extensiones del **FHIR Core Chile (CL Core)**  

Este desarrollo forma parte del **proyecto de título de Ingeniería Civil Biomédica**.


La API actúa como intermediario, encargándose del mapeo estructural y semántico entre ambos sistemas.

---

Tecnologías Utilizadas:

- Python 3.9+
- FastAPI
- Requests / HTTPX
- Uvicorn
- HAPI FHIR
- Bahmni / OpenMRS
- FHIR R4
- CL Core Chile
- Python 3.9 o superior
- Git
- VS code

Tambien nececita acceso a:

- Servidor HAPI FHIR en ejecución

- Servidor Bahmni/OpenMRS operativo

**Para decargar el proyecto:**  
https://github.com/eduardoooooo6/mapeo-fhir-bahmniOpenMRS-API

## Instalación

**1️) Crear entorno virtual**
En la terminal de VScode entrar a la carpeta del proyecto donde se desea tener la api de mapeo, luego ejecutar el comando:

python -m venv venv

**2️) Activar entorno virtual**
Para activar el entorno virtual ejecutar:

venv\Scripts\activate


**3️) Instalar dependencias**

pip install -r requirements.txt

## Ejecución de la API

La API se ejecuta en el puerto 5000 dentro de un entorno virtual ejecutando el sigueinte comando en la consola:

uvicorn main:app --host 0.0.0.0 --port 5000 --reload


Una vez iniciada, la documentación automática generada por FastAPI estará disponible en:

Swagger UI

http://localhost:5000/docs



## Endpoints Disponibles

🔹 GET /review_url

Verifica la conectividad con una URL externa (Bahmni/OpenMRS).

Parámetros:

- url: URL a revisar

🔹 POST /map

Recibe un recurso FHIR Patient y crea el paciente en Bahmni/OpenMRS.

**Funcionalidades principales**

Mapeo de:

- Nombre
- Dirección
- Telecom (teléfono y correo electrónico)
- Identificador nacional (RUT – CL Core)
- Segundo apellido (CL Core)
- Sexo biológico (CL Core)
- Nacionalidad (CL Core)

Conversión de género administrativo

Creación del paciente en Bahmni

🔹 GET /search

Busca pacientes en Bahmni/OpenMRS por nombre.

Parámetros:

- name: Nombre o parte del nombre del paciente

🔹 GET /search_by_id

Busca un paciente en Bahmni/OpenMRS por ID y realiza el mapeo a FHIR.

Respuesta

Recurso Patient en formato FHIR

🔹 POST /send_to_hapi

Envía un paciente en formato FHIR hacia un servidor HAPI FHIR.

Validaciones realizadas

Normalización del campo gender

Eliminación de campos no aceptados por HAPI FHIR

Limpieza de estructuras vacías (direcciones, extensiones)

## Mapeos Implementados:

**FHIR → Bahmni**

Patient.name

Patient.gender

Patient.birthDate

Patient.address

Patient.telecom

Identificador RUT (CL Core)

Extensiones CL Core:

Sexo Biológico

Nacionalidad

Segundo Apellido

**Bahmni → FHIR**

Nombre preferido

Dirección preferida

Género administrativo

Fecha de nacimiento

Atributos como extensiones FHIR

**Autor**
Eduardo Allende
Ingeniería Civil Biomédica
Proyecto de Título – 2025