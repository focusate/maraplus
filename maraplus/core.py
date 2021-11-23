import time

from marabunta import core as core_orig
from marabunta import parser as parser_orig
from marabunta import model as model_orig
from marabunta import runner as runner_orig
from marabunta import database as database_orig
from marabunta import web as web_orig

from .config import Config, get_args_parser
from .parser import YamlParser
from .model import Version, VersionMode
from .runner import VersionRunner


def migrate(config):
    """Perform a migration according to config.

    Args:
        config (Config): The configuration to be applied

    """
    # This is override function to be able to inject extra functionality
    webapp = web_orig.WebApp(
        config.web_host,
        config.web_port,
        custom_maintenance_file=config.web_custom_html,
        resp_status=config.web_resp_status,
        resp_retry_after=config.web_resp_retry_after,
        healthcheck_path=config.web_healthcheck_path
    )

    webserver = core_orig.WebServer(webapp)
    webserver.daemon = True
    webserver.start()
    extra_mig_files = config.extra_mig_files or []
    # Pass extra migration files alongside main one.
    migration_parser = YamlParser.parse_from_file(
        config.migration_file,
        *extra_mig_files,
    )
    migration = migration_parser.parse()

    database = database_orig.Database(config)

    with database.connect() as lock_connection:
        application_lock = core_orig.ApplicationLock(lock_connection)
        application_lock.start()

        while not application_lock.acquired:
            time.sleep(0.5)
        else:
            if application_lock.replica:
                # when a replica could finally acquire a lock, it
                # means that the concurrent process has finished the
                # migration or that it failed to run it.
                # In both cases after the lock is released, this process will
                # verify if it has still to do something (if the other process
                # failed mainly).
                application_lock.stop = True
                application_lock.join()
            # we are not in the replica or the lock is released: go on for the
            # migration

        try:
            table = database_orig.MigrationTable(database)
            runner = runner_orig.Runner(config, migration, database, table)
            runner.perform()
        finally:
            application_lock.stop = True
            application_lock.join()


def main():
    """Run wrapped marabunta."""
    parser = get_args_parser()
    args = parser.parse_args()
    config = Config.from_parse_args(args)
    migrate(config)


# Patch marabunta to use new subclasses.
parser_orig.Version = Version
runner_orig.VersionRunner = VersionRunner
model_orig.VersionMode = VersionMode

if __name__ == '__main__':
    main()
