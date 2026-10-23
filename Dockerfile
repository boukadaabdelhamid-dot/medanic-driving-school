FROM node:22-bookworm-slim AS build

WORKDIR /app
RUN corepack enable && corepack prepare pnpm@10.26.1 --activate
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm run typecheck:libs
ENV BASE_PATH=/
ENV PORT=3000
RUN pnpm --filter @workspace/medanic-erp run build
RUN pnpm --filter @workspace/api-server run build

FROM node:22-bookworm-slim

WORKDIR /app
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-tk \
    fonts-dejavu-core \
  && python3 -m pip install --break-system-packages --no-cache-dir \
    "arabic-reshaper>=3.0.1" \
    "pillow>=13.0.0" \
    "python-bidi>=0.6.12" \
    "reportlab>=5.1.0" \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY --from=build /app /app

ENV NODE_ENV=production
ENV TZ=Africa/Algiers
ENV PYTHONDONTWRITEBYTECODE=1

USER node
EXPOSE 3000
CMD ["node", "--enable-source-maps", "artifacts/api-server/dist/index.mjs"]
