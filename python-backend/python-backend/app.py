from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
from flask_cors import CORS

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'hospital-app',
    'host': 'localhost',
    'port': 27017
}

CORS(app)
db = MongoEngine(app)

class Appointment(db.EmbeddedDocument):
    name = db.StringField(required=True)
    condition = db.StringField(required=True)
    appointmentDate = db.StringField(required=True)
    appointmentTime = db.StringField(required=True)



class MedicalRecord(db.EmbeddedDocument):
    record_id = db.StringField(required=True)
    diagnosis = db.StringField(required=True)
    treatment = db.StringField(required=True)
    date_of_visit = db.StringField(required=True)
    notes = db.StringField()

class User(db.Document):
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    name = db.StringField(required=True)
    surname = db.StringField(required=True)
    role = db.StringField(required=True)
    appointments = db.ListField(db.EmbeddedDocumentField(Appointment))
    medical_history = db.ListField(db.StringField())
    work_description = db.StringField()
    retete_medicale = db.ListField(db.StringField())
    phone = db.StringField()
    medical_records = db.ListField(db.EmbeddedDocumentField(MedicalRecord))

@app.route('/api/users/<email>/medicalRecords', methods=['POST'])
def add_medical_record(email):
    data = request.get_json()

    # Fetch the user with the provided email
    user = User.objects(email=email).first()

    if user:
        # Create a new medical record
        new_record = MedicalRecord(
            record_id=data.get('record_id'),
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            date_of_visit=data.get('date_of_visit'),
            notes=data.get('notes')
        )

        # Add the medical record to the user's medical records list
        user.medical_records.append(new_record)
        user.save()

        return jsonify({"success": True, "message": "Medical record added successfully"})
    else:
        return jsonify({"success": False, "message": "User not found"})


@app.route('/api/users/update', methods=['PUT'])
def update_user():
    data = request.get_json()

    email = data['email']
    user = User.objects(email=email).first()

    if user:
        user.name = data.get('name', user.name)
        user.surname = data.get('surname', user.surname)
        user.work_description = data.get('work_description', user.work_description)
        user.phone = data.get('phone', user.phone)
        user.save()
        return jsonify({"success": True, "message": "User information updated successfully"})
    else:
        return jsonify({"success": False, "message": "User not found"})
    

@app.route('/api/users/<email>/appointments', methods=['POST'])
def add_appointment(email):
    data = request.get_json()

    # Fetch the user with the provided email
    user = User.objects(email=email).first()

    if user:
        # Create a new appointment
        new_appointment = Appointment(
            name=data.get('name'),
            condition=data.get('condition'),
            appointmentDate=data.get('appointmentDate'),
            appointmentTime=data.get('appointmentTime')
        )

        # Add the appointment to the user's appointments list
        user.appointments.append(new_appointment)
        user.save()

        return jsonify({"success": True, "message": "Appointment added successfully"})
    else:
        return jsonify({"success": False, "message": "User not found"})



@app.route('/patients', methods=['GET'])
def get_patients():
    patients = User.objects(role='patient')
    patients_list = []
    for patient in patients:
        patient_data = {
            "name": patient.name,
            "email": patient.email,
            "surname": patient.surname,
            "role": patient.role,
            "description": patient.work_description,
            "phone": patient.phone  # Add this line
        }
        patients_list.append(patient_data)
    return jsonify(patients_list), 200



@app.route('/medics', methods=['GET'])
def get_medics():
    medics = User.objects(role='doctor')
    medics_list = []
    for medic in medics:
        medic_data = {
            "name": medic.name,
            "email": medic.email,
            "surname": medic.surname,
            "role": medic.role,
            "description": medic.work_description,
            "phone": medic.phone  # Add this line
        }
        medics_list.append(medic_data)
    return jsonify(medics_list), 200



@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()

    new_user = User(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        surname=data['surname'],
        role=data['role'],
        appointments=[],
        medical_history=[],
        work_description=None,
        retete_medicale=[]
    )

    try:
        new_user.save()
        return jsonify({"success": True, "message": "User registered successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json()

    email = data['email']
    password = data['password']

    # Find the user by email
    user = User.objects(email=email).first()

    if user:
        if user.password == password:
            # Successful login
            user_data = {
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'appointments': [
                    {
                        'name': appointment.name,
                        'condition': appointment.condition,
                        'appointmentDate': appointment.appointmentDate,
                        'appointmentTime': appointment.appointmentTime
                    }
                    for appointment in user.appointments
                ],
                'medical_history': user.medical_history,
                'description': user.work_description,
                'retete_medicale': user.retete_medicale
            }
            return jsonify({"success": True, "message": "Login successful", "user": user_data})
        else:
            # Incorrect password
            return jsonify({"success": False, "message": "Incorrect password"})
    else:
        # User not found
        return jsonify({"success": False, "message": "User not found"})


if __name__ == "__main__":
    app.run(debug=True)