from marabunta import core as core_orig

from .config import Config, get_args_parser


def main():
    """Run wrapped marabunta."""
    parser = get_args_parser()
    args = parser.parse_args()
    config = Config.from_parse_args(args)
    core_orig.migrate(config)


if __name__ == '__main__':
    main()
