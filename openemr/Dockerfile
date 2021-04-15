FROM openemr/openemr:5.0.1

RUN rm -rf /var/www/localhost/htdocs/openemr/interface/main/tabs/templates/patient_data_template.php
COPY --chown=apache:root uhg_src /var/www/localhost/htdocs/openemr/interface/main/tabs/templates
