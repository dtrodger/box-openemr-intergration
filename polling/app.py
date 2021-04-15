import datetime
import os
import time

import boxsdk
import jinja2
import pdfkit
import pymysql
import celery
import redis


# Setup Celery application with Redis message broker
app = celery.Celery('tasks',
                    broker='redis://localhost:6379/0')

# Define OpenEMR database polling task
@app.task
def poll_cds():

    # Create database connection to OpenEMR MySQL backend
    db_connection = pymysql.connect(host='localhost',
                                    user='openemr',
                                    password='openemr',
                                    db='openemr',
                                    cursorclass=pymysql.cursors.DictCursor)

    # Create Redis connection for cache
    cache_connection = redis.Redis(host='localhost',
                                   port=6379,
                                   db=0)

    # Get database cursor
    with db_connection.cursor() as cursor:
        try:

            # Query OpenEMR for one patient record
            cursor.execute("SELECT * FROM openemr.patient_data;")
            db_record = cursor.fetchone()

            if db_record:




                # ------------------------------------------------------------------------------------------------------
                # This is where the clinical subject matter experts logic to determine care recommendations is
                # implemented. For the demo, the CDS logic is simply
                #
                # Create CDS if never done before or patient age changes
                # If we create CDS
                #     Make no recommendations if the patient is under or 26 years old
                #     Make one set of recommendations if the patient is over 26 years old
                #
                # ------------------------------------------------------------------------------------------------------

                # Get patient age
                db_patient_dob = db_record['DOB']
                today = datetime.date.today()
                db_patient_age = today.year - db_patient_dob.year - ((today.month, today.day) < (db_patient_dob.month, db_patient_dob.day))

                # Get patient age
                patient_id = db_record['id']

                # Retrieve patient age from cache - cache records represented as {patient id: patient age}
                cached_patient_age = cache_connection.get(patient_id)

                # Generate CDS if first encounter of patient of patient age changed since last poll
                if not cached_patient_age or int(cached_patient_age) != db_patient_age:
                    # Update cache with new patient id age mapping
                    cache_connection.set(patient_id, db_patient_age)

                    # Render CDS recommendations as HTML
                    provide_recommendation = True if db_patient_age > 26 else False
                # ------------------------------------------------------------------------------------------------------




                    template_env_loader = jinja2.FileSystemLoader(os.path.join(os.getcwd(), 'static'))
                    template_env = jinja2.Environment(loader=template_env_loader)
                    cds_template = template_env.get_template('cds_template.html')
                    rendered_cds = cds_template.render(provide_recommendation=provide_recommendation,
                                                       age=db_patient_age,
                                                       fname=db_record['fname'],
                                                       lname=db_record['lname'],
                                                       sex=db_record['sex'],
                                                       patient_id=patient_id)
                    tmp_cds_path = os.path.join(os.getcwd(), f'tmp/cds_{patient_id}_{db_patient_age}_{int(time.time())}.pdf')

                    # Convert rendered HTML to PDF
                    pdfkit.from_string(rendered_cds,
                                       tmp_cds_path)

                    # Authenticate with Box web services and get web service client
                    box_auth = boxsdk.JWTAuth.from_settings_file(os.path.join('box_auth', 'kaiser_permanente_california.json'))
                    box_client = boxsdk.Client(box_auth)

                    # Upload CDS to Box
                    box_client.folder('0').upload(tmp_cds_path)

                    # Remove CDS from file system
                    os.remove(tmp_cds_path)
        finally:

            # Close database cursor
            cursor.close()

# Configure periodic execution of OpenEMR polling task
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1,
                             poll_cds.s(),
                             name='Poll CDS')
