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
- docker Desktop

Tambien nececita acceso a:

- Servidor HAPI FHIR en ejecución

- Servidor Bahmni/OpenMRS operativo

**Para decargar el proyecto:**  
https://github.com/eduardoooooo6/mapeo-fhir-bahmniOpenMRS-API

## Instalación

## Instalación de Docker Desktop

Docker Desktop permite ejecutar contenedores Docker de manera sencilla en sistemas Windows, macOS y Linux, y es requerido para levantar Bahmni mediante contenedores.

### Pasos de instalación

**Docker Desktop**

1. Descargar Docker Desktop desde el sitio oficial:
   https://www.docker.com/products/docker-desktop/

2. Ejecutar el instalador y seguir las instrucciones del asistente

3. Reiniciar el sistema si el instalador lo solicita

4. Verificar que Docker esté correctamente instalado ejecutando en una terminal:


docker --version
docker compose version

---
**Entorno virtual VENV**

1. Crear entorno virtual
En la terminal de VScode entrar a la carpeta del proyecto donde se desea tener la api de mapeo, luego ejecutar el comando:

python -m venv venv

2. Activar entorno virtual
Para activar el entorno virtual ejecutar:

venv\Scripts\activate


3. Instalar dependencias

pip install -r requirements.txt

---
**Bahmni/OpenMRS**

Instalación de Bahmni/OpenMRS mediante Docker

Para levantar Bahmni/OpenMRS de forma local se utiliza el repositorio oficial basado en Docker.

Repositorio oficial de Bahmni Docker:
https://github.com/Bahmni/bahmni-docker

1. Clonar el repositorio de Bahmni
git clone https://github.com/Bahmni/bahmni-docker.git
cd bahmni-docker

2. Levantar los servicios de Bahmni

Desde el directorio del repositorio clonado, ejecutar:

docker compose up -d


Este comando descargará las imágenes necesarias y levantará automáticamente los servicios de Bahmni y OpenMRS.

3. Acceso a Bahmni

Una vez finalizado el proceso, Bahmni estará disponible normalmente en:

http://localhost


El sistema quedará listo para ser utilizado por la API de interoperabilidad FHIR–Bahmni.

---

**Descargar la imagen oficial de HAPI FHIR**

HAPI FHIR proporciona una imagen oficial lista para usar.
1. Para descargarla, ejecutar:

docker pull hapiproject/hapi:latest

2. Ejecutar el servidor HAPI FHIR

Para levantar el servidor HAPI FHIR en modo R4, ejecutar:

docker run -d \
  -p 8080:8080 \
  --name hapi-fhir \
  hapiproject/hapi:latest


Este comando ejecuta HAPI FHIR y expone el servicio en el puerto 8080.

3. Acceso a HAPI FHIR

Una vez iniciado el contenedor, el servidor HAPI FHIR estará disponible en:

http://localhost:8080/fhir


La interfaz web de prueba (si está habilitada) se puede acceder desde:

http://localhost:8080

4. Verificación del servidor

Para comprobar que el servidor está funcionando correctamente, se puede acceder desde el navegador a:

http://localhost:8080/fhir/Patient


Si el servidor responde, HAPI FHIR está correctamente instalado y listo para integrarse con la API de interoperabilidad.

## Ejecución de la API

Primero se debe Activar el entorno virtual como ya se mostro anteriormente.

Luego la a API se ejecuta en el puerto 5000 dentro de un entorno virtual ejecutando el sigueinte comando en la consola:

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