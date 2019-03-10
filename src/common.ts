import { Request as ExpressRequest } from "express";

export interface Request extends ExpressRequest {
  user?: User;
}

export interface User {
  username: string;
  secret: string;
  accessLevel?: number;
  password: any;
}

export interface Zakupka {
  name: string;
  description: string;
  price: number;
  accessLevel: number;
}
