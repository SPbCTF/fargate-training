import Redis from "ioredis";

import { User, Zakupka } from "./common";

class Database {
  private _redis: Redis.Redis;

  constructor() {
    this._redis = new Redis(
      process.env.NODE_ENV === "development"
        ? "redis://localhost"
        : process.env.REDIS_URL,
    );
  }

  public async getUser(name: string): Promise<User | undefined> {
    return this._redis.hgetall(`user:${name}`);
  }

  public async userExists(name: string): Promise<number | boolean> {
    return this._redis.exists(`user:${name}`);
  }

  public async getUserPassword(name: string): Promise<string | null> {
    return this._redis.hget(`user:${name}`, "password");
  }

  public async setUserFields(name: string, fields: any): Promise<void> {
    await this._redis.hmset(`user:${name}`, ...fields);
  }

  public async registerUser(user: User): Promise<void> {
    const { username, secret, accessLevel, password } = user;
    console.log(`Password: ${password}`);
    await this.setUserFields(username, [
      "username",
      username,
      "secret",
      secret,
      "accessLevel",
      accessLevel,
      "password",
      password,
    ]);
  }

  public async getZakupka(name: string): Promise<Zakupka | undefined> {
    return this._redis.hgetall(`zakupka:${name}`);
  }

  public async getAllZakupka(): Promise<Zakupka[] | undefined> {
    const names = await this._redis.keys("zakupka:*");

    console.log("names ", names);

    const pipeline = await this._redis.pipeline();
    names.forEach((name) => pipeline.hmget(name, "name", "money", "accessLevel"));

    const zakupki = (await pipeline.exec()).map((el: any) => ({
      name: el[1][0],
      money: +el[1][1],
      accessLevel: +el[1][2],
    }));

    console.log("zakupki", zakupki);
    return zakupki;
  }

  public async setZakupkaFields(name: string, fields: any): Promise<void> {
    await this._redis.hmset(`zakupka:${name}`, ...fields);
  }

  public async createZakupka(zakupka: Zakupka): Promise<void> {
    const { name, description, price, accessLevel } = zakupka;
    await this.setZakupkaFields(name, [
      "description",
      description,
      "price",
      price,
      "accessLevel",
      accessLevel,
    ]);
  }
}

export const redis = new Database();
