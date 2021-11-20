import pathlib

from marabunta import config as config_orig


class Config(config_orig.Config):
    """Extend config to support extra arguments."""

    def __init__(
        self,
        migration_file,
        database,
        db_user=None,
        db_password=None,
        db_password_file=None,
        db_port=5432,
        db_host='localhost',
        mode=None,
        allow_serie=False,
        force_version=None,
        web_host='localhost',
        web_port=8069,
        web_resp_status=503,
        web_resp_retry_after=300,  # 5 minutes
        web_custom_html=None,
            web_healthcheck_path=None):
        """Extend to handle extra args."""
        if db_password_file:
            with pathlib.Path(db_password_file).expanduser().open() as f:
                db_password = f.read().strip()
        super().__init__(
            migration_file,
            database,
            db_user=db_user,
            db_password=db_password,
            db_port=db_port,
            db_host=db_host,
            mode=mode,
            allow_serie=allow_serie,
            force_version=force_version,
            web_host=web_host,
            web_port=web_port,
            web_resp_status=web_resp_status,
            web_resp_retry_after=web_resp_retry_after,
            web_custom_html=web_custom_html,
            web_healthcheck_path=web_healthcheck_path,
        )

    @classmethod
    def from_parse_args(cls, args):
        """Override to create config with extra arguments."""
        if not (bool(args.db_password) ^ bool(args.db_password_file)):
            raise TypeError(
                "--db-password and --db-password-file arguments are mutually" +
                " exclusive"
            )
        return cls(
            args.migration_file,
            args.database,
            db_user=args.db_user,
            db_password=args.db_password,
            db_password_file=args.db_password_file,
            db_port=args.db_port,
            db_host=args.db_host,
            mode=args.mode,
            allow_serie=args.allow_serie,
            force_version=args.force_version,
            web_host=args.web_host,
            web_port=args.web_port,
            web_resp_status=args.web_resp_status,
            web_resp_retry_after=args.web_resp_retry_after,
            web_custom_html=args.web_custom_html,
            web_healthcheck_path=args.web_healthcheck_path,
        )


def get_args_parser():
    """Create parser for command line options based on marabunta."""
    parser = config_orig.get_args_parser()
    parser.add_argument(
        '--db-password-file',
        action=config_orig.EnvDefault,
        envvar='MARABUNTA_DB_PASSWORD_FILE',
        required=False,
        help="File path storing Odoo's database password"
    )
    # Move new argument just after `--db-password` for more convenience.
    _actions = parser._actions
    _actions.insert(5, _actions.pop(-1))
    _group_actions = parser._optionals._group_actions
    _group_actions.insert(5, _group_actions.pop(-1))
    # Make --db-password not required. We want to allow
    # --db-password-file as alternative.
    _actions[4].required = False
    return parser