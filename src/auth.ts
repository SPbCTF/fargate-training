import express from "express";
import jwt from "jsonwebtoken";

import { redis } from "./redis";
import { User, Request } from "./common";

export const jwtMiddleware = async (
  req: Request,
  res: express.Response,
  next: express.NextFunction
) => {
  console.log("JWT Middleware");
  const token = req.cookies["token"];
  if (token) {
    console.log(`Token: ${token}`);

    let data, username;

    try {
      const payload = (await jwt.verify(token, process.env.JWT_SECRET!, {
        algorithms: ["HS256", "ES256"]
      })) as User;

      username = payload.username;

      data = await redis.hgetall(`users:${username}`);
    } catch (e) {
      console.error(e);
      return /* thank u, */ next();
    }

    if (data) {
      req.user = { username } as User;
    }
  }
  return /* thank u, */ next();
};

const makeJWT = async (username: string): Promise<string> => {
  return jwt.sign({ username }, process.env.JWT_SECRET!);
};

export const authRequired = async (
  req: Request,
  res: express.Response,
  next: express.NextFunction
) => {
  console.log("Auth checking");
  console.log(req.user);
  if (req.user) {
    next();
  } else {
    res.status(401);
    res.json({ error: "Not authorized" });
  }
};

export const authenticate = async (
  username: string,
  password: string
): Promise<false | string> => {
  const user_password = await redis.hget(`users:${username}`, "password");

  if (!user_password) {
    return false;
  }

  if (user_password === password) {
    return makeJWT(username);
  } else {
    return false;
  }
};

export const register = async (
  username: string,
  password: any
): Promise<false | string> => {
  if (await redis.exists(`users:${username}`)) {
    return false;
  }

  await redis.hmset(`users:${username}`, password);

  return makeJWT(username);
};
