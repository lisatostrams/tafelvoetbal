FROM image-registry.openshift-image-registry.svc:5000/rivm-paskaart-co/pythonbase:3.9-ubi8

USER root
COPY . /opt/app-root/src/
RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:8050 html_pagina:server -k gevent --worker-connections 10 --workers 4 --timeout 900
#CMD /opt/app-root/bin/python3.9 /opt/app-root/src/html_pagina.py
#CMD while true; do sleep 60; done