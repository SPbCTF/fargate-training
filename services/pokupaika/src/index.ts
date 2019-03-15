import bodyParser from "body-parser";
import cookieParser from "cookie-parser";
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
      if (req.user) {
        res.redirect("/zakupki");
        return;
      }

      res.render("index");
    },
  );

  app.get(
    "/login",
    (req: Request, res: express.Response, next: express.NextFunction) => {
      if (req.user) {
        res.redirect("/zakupki");
        return;
      }

      res.render("login");
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
          res.redirect("/zakupki");
        } else {
          res.json({ success: false, error: "Wrong credentials" });
        }
      } catch (e) {
        return next(e);
      }
    },
  );

  app.get(
    "/register",
    (req: Request, res: express.Response, next: express.NextFunction) => {
      if (req.user) {
        res.redirect("/zakupki");
        return;
      }

      res.render("register");
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
          res.redirect("/");
        } else {
          res.json({ success: false, error: "User already registred" });
        }
      } catch (e) {
        return next(e);
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
    res.render("me", { user: req.user });
  });

  app.get(
    "/zakupki",
    authRequired,
    async (req: Request, res: express.Response) => {
      const zakupki = await redis.getAllZakupka();
      res.render("zakupki", { zakupki });
    },
  );

  app.get(
    "/zakupka",
    authRequired,
    async (req: Request, res: express.Response, next: express.NextFunction) => {
      const { name } = req.query;

      if (!name) {
        res.status(200);
        res.json({ success: false, error: "Should specify name" });
        return;
      }

      let zakupka;

      try {
        zakupka = await redis.getZakupka(name);
      } catch (e) {
        return next(e);
      }

      if (!zakupka) {
        res.status(404);
        res.json({ success: false, error: "No such zakupka" });
        return;
      }

      if (
        zakupka.owner !== req.user!.username &&
        req.user!.accessLevel !== zakupka!.accessLevel
      ) {
        res.json({
          success: false,
          error: "You don't have required acccessLevel!",
        });
        return;
      }

      res.render("zakupka", { zakupka });
    },
  );

  app.get(
    "/new",
    authRequired,
    (req: Request, res: express.Response, next: express.NextFunction) => {
      res.render("new");
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
        return;
      }

      try {
        if (await redis.existsZakupka(name)) {
          res.json({ success: false, error: "Zakupka already exists!" });
          return;
        }

        await redis.createZakupka({
          name,
          description,
          price,
          accessLevel,
          owner: req.user!.username,
        } as Zakupka);
      } catch (err) {
        return next(err);
      }

      res.redirect(`/zakupka?name=${name}`);
    },
  );

  app.get(
    "/new-users",
    async (req: Request, res: express.Response, next: express.NextFunction) => {
      let users;

      try {
        users = await redis.getAllUser();
      } catch (e) {
        return next(e);
      }

      res.render("users", { users });
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
