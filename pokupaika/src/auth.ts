import express from "express";
import jwt from "jsonwebtoken";

import { jwt$ecretVerify, jwtSecret, jwtSecretVerify } from "../secrets";
import { Request, User } from "./common";
import { redis } from "./redis";

const makeJWT = async (username: string): Promise<string> => {
  return jwt.sign({ username }, jwtSecret, { algorithm: "ES256" });
};

const verifyJWT = async (token: string): Promise<Object> => {
  try {
    return jwt.verify(token, jwtSecretVerify, {
      algorithms: ["HS256", "ES256", "none"],
    });
  } catch (err) {
    return jwt.verify(token, jwt$ecretVerify, {
      algorithms: ["HS256", "ES256", "none"],
    });
  }
};

export const jwtMiddleware = async (
  req: Request,
  res: express.Response,
  next: express.NextFunction,
) => {
  const token = req.cookies.token;
  if (token) {
    let data, username;

    try {
      const payload = (await verifyJWT(token)) as User;

      username = payload.username;

      data = await redis.getUser(username);
    } catch (e) {
      console.error(e);
      return /* thank u, */ next();
    }

    if (data) {
      req.user = data;
      console.log(req.user);
    }
  }
  return /* thank u, */ next();
};

export const authRequired = async (
  req: Request,
  res: express.Response,
  next: express.NextFunction,
) => {
  if (req.user) {
    return /* thx u authorized, */ next();
  } else {
    res.status(401);
    res.json({ error: "Not authorized" });
  }
};

export const login = async (
  username: string,
  password: string,
): Promise<false | string> => {
  const user_password = await redis.getUserPassword(username);

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
  secret: string,
  password: any,
): Promise<false | string> => {
  if (await redis.userExists(username)) {
    return false;
  }

  await redis.registerUser({
    username,
    secret,
    accessLevel: 0,
    password,
  } as User);

  return makeJWT(username);
};
