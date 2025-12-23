# main.py
import json
import uuid
import requests
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# ========================================
#  Configurar CORS (para conectar con tu app web)
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
#  Función para mapear FHIR → Bahmni
# ========================================
def map_fhir_to_bahmni(fhir):

    # -------------------------
    # Datos base
    # -------------------------
    person = fhir.get("name", [{}])[0]
    address = fhir.get("address", [{}])[0]
    telecom = fhir.get("telecom", [])
    extensions = fhir.get("extension", [])
    identifiers = fhir.get("identifier", [])

    # -------------------------
    # Atributos Bahmni
    # -------------------------
    attributes = []

    # =========================
    # Telecom: teléfono y email
    # =========================
    for t in telecom:
        if t.get("system") == "phone":
            attributes.append({
                "attributeType": {"uuid": "a384873b-847a-4a86-b869-28fb601162dd"},
                "value": t.get("value")
            })

        elif t.get("system") == "email":
            attributes.append({
                "attributeType": {"uuid": "e3123cba-5e07-11ef-8f7c-0242ac120002"},
                "value": t.get("value")
            })

    # =========================
    # Identificador: RUT
    # =========================
    for ident in identifiers:
        if ident.get("system") == "https://hl7chile.cl/fhir/ig/clcore/CodeSystem/CSIdentificadoresCL":
            attributes.append({
                "attributeType": {"uuid": "9c50f6db-e624-4aa6-9454-d8b1d49b2bf3"},
                "value": ident.get("value")
            })

    # =========================
    # Segundo Apellido (CL Core)
    # =========================
    for ext in person.get("extension", []):
        if ext.get("url") == "https://hl7chile.cl/fhir/ig/clcore/StructureDefinition/SegundoApellido":
            segundo_apellido = ext.get("valueString")
            if segundo_apellido:
                attributes.append({
                    "attributeType": {"uuid": "e628c57c-8077-422a-a016-2b295998cf36"},  
                    "value": segundo_apellido
                })

    # =========================
    # Extensiones CL Core
    # =========================
    for ext in extensions:

        # -------------------------
        # Sexo Biológico
        # -------------------------
        MAP_SEXO_BIOLOGICO = {
            "Male": "3aa39e38-06e4-4c03-8aad-47007256077f",
            "Female": "61b70ab0-f6fe-4aa8-b36f-67d2f4fd4c92",
            "Other": "0fd08f92-8dda-49b5-9fcb-76d0f21b309b",
            "Unknown": "a6f9792f-7725-448b-9ff3-22945ecbbce8"
        }

        if ext.get("url") == "https://hl7chile.cl/fhir/ig/clcore/StructureDefinition/SexoBiologico":

            sexo_code = (
                ext.get("valueCodeableConcept", {})
                .get("coding", [{}])[0]
                .get("code")
            )

            sexo_uuid = MAP_SEXO_BIOLOGICO.get(sexo_code)

            if sexo_uuid:
                attributes.append({
                    "attributeType": {
                        "uuid": "7c8d50bd-73d0-40ef-8f9a-12057b61286e"
                    },
                    "value": sexo_uuid
                })



        # -------------------------
        # Nacionalidad
        # -------------------------
        elif ext.get("url") == "https://hl7chile.cl/fhir/ig/clcore/StructureDefinition/Nacionalidad":

            nacionalidad = (
                ext.get("valueCodeableConcept", {})
                .get("coding", [{}])[0]
                .get("display")
            )

            if nacionalidad:
                attributes.append({
                    "attributeType": {"uuid": "7bb331e1-968f-4e26-96c5-cc9eb55fba11"},
                    "value": nacionalidad
                })

    # =========================
    # Género administrativo
    # =========================
    gender_map = {
        "male": "M",
        "female": "F",
        "other": "O"
    }

    gender = gender_map.get(
        fhir.get("gender", "other").lower(),
        "O"
    )

    # =========================
    # JSON final Bahmni
    # =========================
    bahmni_patient = {
        "patient": {
            "person": {
                "names": [
                    {
                        "givenName": person.get("given", [""])[0],
                        "middleName": person.get("given", ["", ""])[1]
                        if len(person.get("given", [])) > 1 else "",
                        "familyName": person.get("family", ""),
                        "display": f"{person.get('given', [''])[0]} {person.get('family', '')}",
                        "preferred": True
                    }
                ],
                "gender": gender,
                "birthdate": fhir.get("birthDate", ""),
                "addresses": [
                    {
                        "address1": address.get("line", [""])[0],
                        "address2": address.get("line", ["", ""])[1]
                        if len(address.get("line", [])) > 1 else "",
                        "cityVillage": address.get("city", ""),
                        "countyDistrict": address.get("county", ""),
                        "stateProvince": address.get("state", ""),
                        "country": address.get("country", ""),
                        "postalCode": address.get("postalCode", "")
                    }
                ],
                "attributes": attributes
            },
            "identifiers": [
                {
                    "identifierSourceUuid": "c5cf4b68-6529-43fc-a644-c775ae73745e",
                    "identifierPrefix": "ABC",
                    "identifierType": "d3153eb0-5e07-11ef-8f7c-0242ac120002",
                    "preferred": True,
                    "voided": False
                }
            ]
        },
        "relationships": []
    }

    return bahmni_patient





# ========================================
#  GET: obtener infor de una URL
# ========================================
@app.get("/review_url")
async def review_url(url: str):
    auth = ("superman", "Admin123")
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, auth=auth, verify=False)
        if response.status_code in [200, 201]:
            return {"status": "OK", "message": "Link OK", "data": response.json()}
        else:
            return {"status": "ERROR", "message": f"{response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"status": "ERROR", "message": f"No se pudo conectar a Bahmni: {e}"} 

# ========================================
#  POST: Recibir FHIR y crear paciente en Bahmni
# ========================================
@app.post("/map")
async def map_fhir(request: Request):
    fhir_patient = await request.json()
    print("FHIR recibido:", fhir_patient)

    bahmni_patient = map_fhir_to_bahmni(fhir_patient)

    url = "https://localhost/openmrs/ws/rest/v1/bahmnicore/patientprofile"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    auth = ("superman", "Admin123")  # Cambiar por tus credenciales

    try:
        response = requests.post(url, json=bahmni_patient, headers=headers, auth=auth, verify=False)
        if response.status_code in [200, 201]:
            return {"status": "OK", "message": "Paciente creado en Bahmni!", "data": response.json()}
        else:
            return {"status": "ERROR", "message": f"{response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"status": "ERROR", "message": f"No se pudo conectar a Bahmni: {e}"}

# ========================================
#  Función para mapear Bahmni → FHIR
# ========================================
def map_bahmni_to_fhir(bahmni):
    person = bahmni.get("person", {})
    preferred_name = person.get("preferredName", {})
    preferred_address = person.get("preferredAddress", {})

    # Identificador principal
    fhir_identifiers = []
    ids = bahmni.get("identifiers", [])
    if ids:
        raw = ids[0].get("display", "")
        print("RESPUESTA raw:", raw)
        value = raw.split("=")[-1].strip()
        print("RESPUESTA value:", value)
        fhir_identifiers.append({
            "system": "http://bahmni.org/main-identifier",
            "value": value
        })

    print("RESPUESTA fhir_identifiers:", fhir_identifiers)

    # Nombre → último es apellido
    name_parts = preferred_name.get("display", "").split()
    family = name_parts[-1] if name_parts else ""
    given = name_parts[:-1] if len(name_parts) > 1 else []

    fhir_name = [{
        "family": family,
        "given": given
    }]

    # Dirección (simple)
    fhir_address = []
    if preferred_address:
        fhir_address.append({
            "line": [preferred_address.get("display", "")],
            "url": [preferred_address.get("links", [{}])[0].get("uri", "")],
            #"city": preferred_address.get("cityVillage", ""),
            #"district": preferred_address.get("countyDistrict", ""),
            #"state": preferred_address.get("stateProvince", ""),
            #"country": preferred_address.get("country", ""),
            #"postalCode": preferred_address.get("postalCode", "")
        })

    # Género estándar FHIR
    gender = {
        "m": "male",
        "f": "female",
        "o": "other"
    }.get(person.get("gender", "").lower(), "unknown")

    # Paciente FHIR final
    fhir_patient = {
        "resourceType": "Patient",
        "id": bahmni.get("uuid"),
        "name": fhir_name,
        "gender": gender,
        "birthDate": person.get("birthdate", "").split("T")[0] if person.get("birthdate") else None,
        #"identifier": fhir_identifiers,
        #"telecom": fhir_telecom,
        "address": fhir_address,
        "extension": person.get("attributes", []),
    }

    return fhir_patient




# ========================================
# GET: Buscar pacientes en Bahmni por nombre
# ========================================
@app.get("/search")
def search_patients(name: str = Query(..., description="Nombre o parte del nombre del paciente")):
    url = f"https://localhost/openmrs/ws/rest/v1/patient?q={name}"
    auth = ("superman", "Admin123")
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, auth=auth, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"{response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
# ========================================
# GET: Buscar pacientes en Bahmni por id
# ========================================
@app.get("/search_by_id")
def search_patients_by_id(id: str = Query(..., description="ID del paciente")):
    url = f"http://localhost/openmrs/ws/rest/v1/patient/{id}"
    auth = ("superman", "Admin123")
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, auth=auth, verify=False)
        print("RESPUESTA BRUTA DE BAHMNI:")
        print(json.dumps(response.json(), indent=4))

        if response.status_code == 200:
            bahmni_data = response.json()
            fhir_data = map_bahmni_to_fhir(bahmni_data) #← Usar la función de mapeo

            print("RESULTADO MAPEADO A FHIR (enviado al frontend):")
            print(json.dumps(fhir_data, indent=4))
            print("==============================\n")

            return {"fhir": fhir_data}
        else:
            return {"error": f"{response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}




# ========================================
# POST: Enviar paciente FHIR a HAPI FHIR
# ========================================
@app.post("/send_to_hapi")
async def send_to_hapi(request: Request):
    data = await request.json()

  
    #  Normalizar gender antes de enviar a HAPI  
    gender = data.get("gender", "").lower()

    gender_map = {
        "m": "male",
        "male": "male",
        "f": "female",
        "female": "female",
        "o": "other",
        "other": "other"
    }

    data["gender"] = gender_map.get(gender, "unknown")

    #HAPI NO acepta "id" en POST → eliminarlo
    data.pop("id", None)


    if "extension" in data and not data["extension"]:
        data.pop("extension")

    if "address" in data and isinstance(data["address"], list):
        if len(data["address"]) == 0:
            data.pop("address")
        else:
            # limpiar line vacía (HAPI lo odia)
            if "line" in data["address"][0] and data["address"][0]["line"] == [""]:
                data["address"][0].pop("line")

   # Mostrar JSON FINAL (este es EL que va a HAPI)
    print("\n==============================")
    print("JSON FINAL enviado a HAPI:")
    print(json.dumps(data, indent=4))
    print("==============================\n")

    # Enviar a HAPI
    try:
        response = requests.post(
            "http://localhost:8081/fhir/Patient",
            json=data,
            headers={"Content-Type": "application/json"},
            verify=False
        )

        print("===== RESPUESTA DE HAPI =====")
        print("Status:", response.status_code)
        try:
            print("Body:", response.json())
        except:
            print("Body (RAW):", response.text)
        print("==============================")

        # Respuesta de error
        if response.status_code not in [200, 201]:
            return {
                "status": "ERROR",
                "message": f"HAPI devolvió {response.status_code}",
                "details": response.text
            }

        return {
            "status": "OK",
            "message": "Paciente enviado a HAPI FHIR",
            "hapi_response": response.json()
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": "No se pudo conectar a HAPI FHIR",
            "details": str(e)
        }
