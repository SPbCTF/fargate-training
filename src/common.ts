import { Request as ExpressRequest } from "express";

export interface User {
  username: string;
}

export interface Request extends ExpressRequest {
  user?: User;
}
