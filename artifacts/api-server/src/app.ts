import express, { type Express } from "express";
import cookieParser from "cookie-parser";
import pinoHttp from "pino-http";
import { existsSync } from "node:fs";
import path from "node:path";
import router from "./routes";
import { logger } from "./lib/logger";
import { loadOptionalUser } from "./lib/auth";

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(loadOptionalUser);

app.use("/api", router);

const workspaceRoot = existsSync(path.join(process.cwd(), "artifacts/medanic-erp"))
  ? process.cwd()
  : path.resolve(process.cwd(), "../..");
const webDist = process.env.WEB_DIST_DIR
  ? path.resolve(process.env.WEB_DIST_DIR)
  : path.join(workspaceRoot, "artifacts/medanic-erp/dist/public");

if (process.env.NODE_ENV === "production" && existsSync(path.join(webDist, "index.html"))) {
  app.use(express.static(webDist, { index: false, fallthrough: true }));
  app.use((req, res, next) => {
    if (
      (req.method !== "GET" && req.method !== "HEAD") ||
      req.path === "/api" ||
      req.path.startsWith("/api/")
    ) {
      next();
      return;
    }
    res.sendFile(path.join(webDist, "index.html"), (error) => {
      if (error) next(error);
    });
  });
}

app.use(
  (
    error: unknown,
    req: express.Request,
    res: express.Response,
    _next: express.NextFunction,
  ) => {
    req.log.error({ err: error }, "Unhandled API error");
    res.status(500).json({ error: "An unexpected server error occurred." });
  },
);

export default app;
