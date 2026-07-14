# Frontend image — Next.js built, then served with `next start`.
# NEXT_PUBLIC_API_URL is inlined into the client bundle at build time (it's a
# NEXT_PUBLIC_* var), so it's supplied as a build ARG rather than runtime env.
FROM node:20-slim

WORKDIR /app

# Install deps first for better layer caching.
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

ENV NODE_ENV=production
EXPOSE 3000
CMD ["npm", "start"]
