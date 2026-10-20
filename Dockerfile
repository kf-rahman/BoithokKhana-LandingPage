# The whole site: one static HTML page served by nginx.
#
# This replaced a Next.js server + FastAPI backend + Postgres. The online
# order form is gone — customers order on WhatsApp/Messenger, which is what
# the shop's printed menu already tells them to do — so there is nothing
# dynamic left to run. Static files, one small image, no database.
#
# Deliberately still a Docker web service rather than a Render "static site":
# it keeps the SAME Render service (boithok-web), so the custom domain stays
# attached and no dashboard surgery is needed. If the site ever moves to a
# Render static site it would also stop sleeping, and scripts/keep-warm.sh
# could be deleted.
FROM nginx:alpine

# Render assigns the port at runtime via $PORT. Anything in /etc/nginx/
# templates/*.template is run through envsubst at container start, so the
# listen directive picks it up.
ENV PORT=10000
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template

COPY index.html /usr/share/nginx/html/index.html
COPY favicon.svg /usr/share/nginx/html/favicon.svg

EXPOSE 10000
