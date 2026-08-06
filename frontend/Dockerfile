# Frontend image — Next.js built, then served with `next start`.
#
# IMPORTANT: this image builds from the REPOSITORY ROOT as its context, not
# from frontend/. The build needs the root `index.html` (the marketing site
# served at "/", copied into public/ by scripts/sync-marketing.mjs), which sits
# outside frontend/. Build it with:
#     docker build -f frontend/Dockerfile .
#
# NEXT_PUBLIC_API_URL is inlined into the client bundle at build time (it's a
# NEXT_PUBLIC_* var), so it's supplied as a build ARG rather than runtime env.
FROM node:20-slim

WORKDIR /app/frontend

# Install deps first for better layer caching.
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./

# The marketing page, one level up — where sync-marketing.mjs expects it.
COPY index.html /app/index.html

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

ENV NODE_ENV=production
EXPOSE 3000
CMD ["npm", "start"]
