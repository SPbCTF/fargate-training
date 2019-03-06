import Redis from "ioredis";

let _redis: Redis.Redis;

const getRedis = () => {
  if (!_redis) {
    _redis = new Redis();
    return _redis;
  } else {
    return _redis;
  }
};

export const redis = getRedis();
