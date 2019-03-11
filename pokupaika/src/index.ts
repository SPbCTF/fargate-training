import bodyParser from "body-parser";
import cookieParser from "cookie-parser";
import cors from "cors";
import express from "express";
import morgan from "morgan";
import { resolve } from "path";
import { jwtSecretVerify } from "../secrets";
import { authRequired, jwtMiddleware, login, register } from "./auth";
import { Request, User, Zakupka } from "./common";
import { redis } from "./redis";

export const startServer = (port: number) => {
  const app = express();

  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(cookieParser());
  // app.use(cors());
  app.use(morgan("dev"));

  app.all(
    "*",
    (req: Request, res: express.Response, next: express.NextFunction) => {
      res.header("Access-Control-Allow-Origin", "*");
      res.header("Access-Control-Allow-Methods", "DELETE, PUT, GET, POST");
      res.header(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept",
      );
      next();
    },
  );

  app.set("view engine", "pug");
  app.set("views", resolve(__dirname, "./views"));

  app.use(jwtMiddleware);

  app.get(
    "/",
    (req: Request, res: express.Response, next: express.NextFunction) => {
      res.render("index");
    },
  );

  app.post(
    "/login",
    async (req: Request, res: express.Response, next: express.NextFunction) => {
      const { username, password } = req.body;

      if (!username || !password) {
        res.status(200);
        res.json({ success: false, error: "Not all fields provided!" });
      }

      let token;

      try {
        if ((token = await login(username, password))) {
          res.cookie("token", token as string);
          res.json({ success: true, token });
        } else {
          res.json({ success: false, error: "Wrong credentials" });
        }
      } catch (e) {
        next(e);
      }
    },
  );

  app.post(
    "/register",
    async (req: Request, res: express.Response, next: express.NextFunction) => {
      const { username, password, secret } = req.body;

      let token;

      try {
        if (!username || !password || !secret) {
          res.status(200);
          res.json({ success: false, error: "Not all fields provided!" });
        }

        if ((token = await register(username, secret, password))) {
          res.cookie("token", token as string);
          res.json({ success: true, token });
        } else {
          res.json({ success: false, error: "User already registred" });
        }
      } catch (e) {
        next(e);
      }
    },
  );

  app.get(
    "/pubkey",
    async (req: Request, res: express.Response, next: express.NextFunction) => {
      res.status(200);
      res.send(jwtSecretVerify);
    },
  );

  app.get("/me", authRequired, async (req: Request, res: express.Response) => {
    res.json(req.user!);
  });

  app.get(
    "/zakupki",
    authRequired,
    async (req: Request, res: express.Response) => {
      const zakupki = await redis.getAllZakupka();
      res.json(zakupki);
    },
  );

  app.get(
    "/zakupka",
    authRequired,
    async (req: Request, res: express.Response) => {
      const { name } = req.query;

      if (!name) {
        res.status(200);
        res.json({ success: false, error: "Should specify name" });
        return;
      }

      const zakupka = await redis.getZakupka(name);

      if (!zakupka) {
        res.status(404);
        res.json({ success: false, error: "No such zakupka" });
        return;
      }

      if (zakupka!.accessLevel === 0) {
        res.json(zakupka);
        return;
      }

      if (!req.user || req.user!.accessLevel !== zakupka!.accessLevel) {
        res.json({
          success: false,
          error: "You don't have required acccessLevel!",
        });
        return;
      }

      res.json(zakupka);
    },
  );

  app.post(
    "/zakupka",
    authRequired,
    async (req: Request, res: express.Response, next: express.NextFunction) => {
      const { name, description, price, accessLevel } = req.body;

      if (!name || !description || !price || !accessLevel) {
        res.status(200);
        res.json({ success: false, error: "Not all fields provided!" });
      }

      try {
        await redis.createZakupka({
          name,
          description,
          price,
          accessLevel,
        } as Zakupka);
      } catch (err) {
        next(err);
      }

      res.status(200);
      res.json({ success: true });
    },
  );

  app.use(
    (
      err: Error,
      req: Request,
      res: express.Response,
      next: express.NextFunction,
    ) => {
      console.error(err);
      res.status(500);
      res.send(":(");
    },
  );

  app.listen(port, () => {
    console.log(`Server started at :${port}`);
  });
};
