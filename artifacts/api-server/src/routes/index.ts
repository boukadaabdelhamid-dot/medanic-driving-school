import { Router, type IRouter } from "express";
import authRouter from "./auth";
import dashboardRouter from "./dashboard";
import documentsRouter from "./documents";
import erpRouter from "./erp";
import reportsRouter from "./reports";
import resourceRouter from "./resources";
import healthRouter from "./health";
import schoolRouter from "./school";

const router: IRouter = Router();

router.use(healthRouter);
router.use(authRouter);
router.use(dashboardRouter);
router.use(documentsRouter);
router.use(erpRouter);
router.use(schoolRouter);
router.use(reportsRouter);
router.use("/resources", resourceRouter);

export default router;
