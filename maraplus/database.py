import time
import psycopg2

from marabunta import database as database_orig


class Database(database_orig.Database):
    """Database subclass to allow waiting for open DB connection."""

    def wait_for_connection(self, timeout):
        """Wait for given connection specified amount of seconds.

        Args:
            timeout (int): number of seconds to wait till connection
                opens up.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                conn = psycopg2.connect(**self.dsn())
                conn.close()
                return True
            except psycopg2.OperationalError:
                pass
            time.sleep(1)
        # Timed out.
        return False
