import glob
import os
import datetime

import boxsdk
import flask


# Setup Flask application web server
app = flask.Flask(__name__)


# Web server route to handle requests from Box hosted CDS
@app.route('/cds', methods=['GET'])
def cds():

    # Authenticate with Box web services and get web service client
    box_auth = boxsdk.JWTAuth.from_settings_file(os.path.join('box_auth', 'kaiser_permanente_california.json'))
    box_client = boxsdk.Client(box_auth)




    # ------------------------------------------------------------------------------------------------------------------
    # This implementation for retrieving files from Box is not suitable for production.
    # In the production application, services sending CDS to Box will write Redis record with newly created Box file id
    #
    # Key = [patient id]-latest-cds-box-file-id
    # Value = [newly created box file id]
    #
    # Example in Redis
    # 443340029-latest-cds-box-file-id:1233321
    #
    # This request handler's route will change to /cds/[patient_id]
    # Patient id will be used to retrieve Box file id from Redis, then the Box Download File API will be called with the
    # associated Box file id.
    # ------------------------------------------------------------------------------------------------------------------




    # Demoware solution to get a file from Box
    # Get Box folder
    box_folder = box_client.folder(folder_id='0').get()

    # Determine last CDS uploaded to Box folder
    latest_entry = None
    latest_entry_created_at = None
    for entry in box_folder.item_collection['entries']:
        current_created_at = datetime.datetime.strptime(entry.get().created_at, '%Y-%m-%dT%H:%M:%S%z')
        if not latest_entry_created_at or current_created_at > latest_entry_created_at:
            latest_entry = entry
            latest_entry_created_at = current_created_at

    # Write CDS to file system
    with open(os.path.join(os.getcwd(), 'tmp', latest_entry.name), 'wb') as fh:
        latest_entry.download_to(fh)

    # Build response with CDS included
    response = flask.send_from_directory('tmp', filename=latest_entry.name)

    # Disable browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # Respond to client request
    return response


# Remove CDS from file system after client response sent
@app.teardown_request
def clear_tmp(request):
    for tmp_cds_file in glob.glob('tmp/*'):
        os.remove(tmp_cds_file)


# Run web server if module run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
