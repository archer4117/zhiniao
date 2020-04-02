# coding:utf-8
import redis

pool = redis.ConnectionPool(host="localhost", port=6379, db=3)


def get_connection():
    return redis.Redis(connection_pool=pool)


if __name__ == '__main__':
    key_pref = "20200113:"
    r_conn = get_connection()
    keys = r_conn.keys(key_pref + "*")

    for key in keys:
        value = r_conn.get(key)
        print key, value
