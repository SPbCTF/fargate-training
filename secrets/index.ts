import fs from "fs";
import path from "path";

export const jwtSecret = fs
  .readFileSync(path.resolve(__dirname, "./private.pem"))
  .toString();
export const jwtSecretVerify = fs
  .readFileSync(path.resolve(__dirname, "./public.pem"))
  .toString();
