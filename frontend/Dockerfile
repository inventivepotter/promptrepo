# Use Node.js 22 LTS image
FROM node:22-alpine

WORKDIR /app

# Set Node environment to production
ENV NODE_ENV=production

COPY package*.json ./

RUN npm ci --only=production

COPY . .

RUN npm run build

EXPOSE 7376

CMD ["npm", "start"]