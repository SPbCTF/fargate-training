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
    await this._redis.zadd("users", Date.now().toString(), username);
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

  public async getAllUser(): Promise<string[] | undefined> {
    const names = await this._redis.zrange("users", -30, -1);

    return names;
  }

  public async getZakupka(name: string): Promise<Zakupka | undefined> {
    return this._redis.hgetall(`zakupka:${name}`);
  }

  public async getAllZakupka(): Promise<Zakupka[] | undefined> {
    const names = await this._redis.zrange("zakupki", -30, -1);

    const pipeline = await this._redis.pipeline();
    names.forEach((name: string) =>
      pipeline.hmget(`zakupka:${name}`, "name", "money", "accessLevel"),
    );

    const zakupki = (await pipeline.exec()).map((el: any) => ({
      name: el[1][0],
      price: +el[1][1],
      accessLevel: +el[1][2],
    }));

    return zakupki;
  }

  public async setZakupkaFields(name: string, fields: any): Promise<void> {
    await this._redis.hmset(`zakupka:${name}`, ...fields);
  }

  public async existsZakupka(name: string): Promise<number | null> {
    return await this._redis.exists(`zakupka:${name}`);
  }

  public async createZakupka(zakupka: Zakupka): Promise<void> {
    const { name, description, price, accessLevel } = zakupka;
    await this.setZakupkaFields(name, [
      "name",
      name,
      "description",
      description,
      "price",
      price,
      "accessLevel",
      accessLevel,
    ]);
    await this._redis.zadd("zakupki", Date.now().toString(), name);
  }
}

export const redis = new Database();
