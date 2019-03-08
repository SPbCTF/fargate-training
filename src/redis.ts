import Redis from "ioredis";

import { User } from "./common";

class Database {
  _redis: Redis.Redis;

  constructor() {
    this._redis = new Redis(process.env.REDIS_URL);
  }

  async getUser(name: string): Promise<User | null> {
    const userData = await this._redis.hgetall(`users:${name}`);
    if (userData) {
      return { username: name, ...userData };
    }

    return null;
  }

  async userExists(name: string): Promise<boolean> {
    return !!this._redis.exists(`users:${name}`);
  }

  async getUserPassword(name: string): Promise<string | null> {
    return this._redis.hget(`users:${name}`, "password");
  }

  async setUserFields(name: string, field: string, data: any): Promise<void> {
    await this._redis.hmset(`users:${name}`, field, ...data);
  }

  async setUserPassword(name: string, password: any): Promise<void> {
    await this.setUserFields(name, "password", password);
  }
}

// let _redis: Redis.Redis;

// const getRedis = () => {
//   if (!_redis) {
//     _redis = new Redis();
//     return _redis;
//   } else {
//     return _redis;
//   }
// };

export const redis = new Database();
