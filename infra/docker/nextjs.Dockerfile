FROM node:20-alpine

RUN npm install -g pnpm@8

WORKDIR /workspace

COPY package.json pnpm-workspace.yaml ./
COPY apps/agent-console/package.json ./apps/agent-console/
COPY apps/admin-console/package.json ./apps/admin-console/
COPY apps/agent-console/tsconfig.json ./apps/agent-console/
COPY apps/admin-console/tsconfig.json ./apps/admin-console/

RUN pnpm install

COPY apps/agent-console ./apps/agent-console
COPY apps/admin-console ./apps/admin-console

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=development
