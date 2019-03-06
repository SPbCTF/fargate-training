import { resolve } from "path";
// tslint:disable-next-line:no-var-requires
require("dotenv").config({ path: resolve(__dirname, "..", ".env") });

import express from "express";
import bodyParser from "body-parser";
import jwt from "jsonwebtoken";

import { Request, User } from "./common";
import { redis } from "./redis";
import { jwtMiddleware, authenticate, authRequired, register } from "./auth";

const app = express();

app.use(bodyParser.urlencoded({ extended: true }));
app.use(jwtMiddleware);

app.get("/test", async (req: Request, res: express.Response) => {
  res.json(req.query);
});

app.post("/test", async (req: Request, res: express.Response) => {
  res.json(req.body);
});

app.get("/env", async (req: Request, res: express.Response) => {
  res.json(process.env);
});

app.post("/login", async (req: Request, res: express.Response) => {
  const { username, password } = req.body;

  let token;

  if ((token = await authenticate(username, password))) {
    res.cookie("token", token as string);
    res.json({ success: true, token });
  } else {
    res.json({ success: false, error: "Wrong credentials" });
  }
});

app.post("/register", async (req: Request, res: express.Response) => {
  const { username, password } = req.body;

  let token;

  if ((token = await register(username, password))) {
    res.cookie("token", token as string);
    res.json({ success: true, token });
  }
});

app.get("/verify", async (req: Request, res: express.Response) => {
  if (req.user) {
    res.json({ success: true, user: req.user });
  } else {
    res.status(401);
    res.json({ success: false, error: "Not authorized" });
  }
});

app.get(
  "/secret",
  authRequired,
  async (req: Request, res: express.Response) => {
    res.json("secret");
  }
);

app.listen(3000, () => {
  console.log(`Server started at :3000`);
});
