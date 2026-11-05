# Build a partir da raiz do repositório: docker build -f apps/web/consumer/Dockerfile .
FROM node:20-slim AS build
WORKDIR /repo
RUN corepack enable
COPY . .
RUN pnpm install --frozen-lockfile
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SUPPORT_EMAIL
ENV NEXT_STANDALONE=1 NEXT_TELEMETRY_DISABLED=1
RUN pnpm --filter @kubo/consumer build

FROM node:20-slim
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0
COPY --from=build /repo/apps/web/consumer/.next/standalone ./
COPY --from=build /repo/apps/web/consumer/.next/static ./apps/web/consumer/.next/static
COPY --from=build /repo/apps/web/consumer/public ./apps/web/consumer/public
USER node
EXPOSE 3000
CMD ["node", "apps/web/consumer/server.js"]
