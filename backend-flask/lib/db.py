from psycopg_pool import ConnectionPool
import os # to load env vars


connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)