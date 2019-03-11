import bodyParser from "body-parser";
import cookieParser from "cookie-parser";
import express from "express";
import morgan from "morgan";
import { authRequired, jwtMiddleware, login, register } from "./auth";
import { Request, User } from "./common";
import { redis } from "./redis";

export const startServer = (port: number) => {
  const app = express();

  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(cookieParser());
  app.use(morgan("dev"));

  app.use(jwtMiddleware);

  app.use(
    async (
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
    "/secret",
    authRequired,
    async (req: Request, res: express.Response) => {
      res.json("secret");
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
        res.json({ success: false, error: "You don't have acccess!" });
        return;
      }

      res.json(zakupka);
    },
  );

  app.post(
    "/zakupka",
    authRequired,
    async (req: Request, res: express.Response) => {
      const { name, description, price, accessLevel } = req.body;

      if (!name || !description || !price || !accessLevel) {
        res.status(200);
        res.json({ success: false, error: "Not all fields provided!" });
      }
    },
  );

  app.listen(port, () => {
    console.log(`Server started at :${port}`);
  });
};
