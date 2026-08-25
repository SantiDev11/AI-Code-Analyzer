# ---------------------------------------------------------------------------
# AI-Code-Analyzer — Frontend (React + TypeScript + Vite)
#
# Multi-stage: Node compila el bundle y una imagen nginx sin privilegios lo
# sirve como estatico. El servidor de desarrollo de Vite NO se usa en runtime.
#
# IMPORTANTE: las variables VITE_* se incrustan en el bundle durante el build
# y son publicas para cualquiera que abra la aplicacion. Nunca pongas secretos
# en VITE_API_BASE_URL ni en ninguna otra VITE_*.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS build

WORKDIR /app

# Instalacion reproducible a partir del lockfile.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vacio por defecto: el bundle hace peticiones relativas al mismo origen y
# nginx las redirige al backend. Asi el navegador nunca necesita resolver el
# hostname interno de Docker.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# `npm run build` ejecuta tsc (comprobacion estricta de tipos) y vite build.
RUN npm run build

# ---------------------------------------------------------------------------
# Runtime: nginx sin privilegios (uid 101, escucha en 8080).
# ---------------------------------------------------------------------------
FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --spider http://127.0.0.1:8080/ || exit 1
