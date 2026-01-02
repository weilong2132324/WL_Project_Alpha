FROM node:18-alpine AS frontend
WORKDIR /src

RUN apk add --no-cache python3 make g++

COPY package*.json ./
RUN npm ci --prefer-offline

COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=frontend /dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]