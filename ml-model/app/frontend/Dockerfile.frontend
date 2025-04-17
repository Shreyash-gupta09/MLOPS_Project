# ———————— BUILD STAGE ————————
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install             # clean install

# Copy source & build
COPY . .
RUN npm run build      # outputs to /app/build

# ———————— RUN STAGE ————————
FROM nginx:stable-alpine

# Copy the static build over to nginx’s html folder
COPY --from=build /app/build /usr/share/nginx/html

# Optional: customize nginx routing (for client‑side routing)
# If you need that, drop an nginx.conf next to this Dockerfile and uncomment:
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE  80

CMD ["nginx", "-g", "daemon off;"]
