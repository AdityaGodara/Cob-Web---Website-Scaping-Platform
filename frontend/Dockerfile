# ----- BUILD STAGE -----

FROM node:22-alpine as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm install 

COPY . .

RUN npm run build

# -------- NGINX STAGE -----

FROM nginx:alpine

COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80