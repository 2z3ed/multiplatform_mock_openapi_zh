FROM node:20-alpine

RUN npm install -g pnpm

WORKDIR /workspace

COPY pnpm-workspace.yaml ./
COPY apps/agent-console/package.json ./apps/agent-console/
COPY apps/admin-console/package.json ./apps/admin-console/

RUN pnpm install

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=development
