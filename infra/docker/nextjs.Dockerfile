FROM node:20-alpine

RUN npm install -g pnpm

WORKDIR /workspace

COPY apps/*/package.json ./
COPY pnpm-workspace.yaml ./

RUN pnpm install

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=development