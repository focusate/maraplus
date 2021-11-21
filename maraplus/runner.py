from marabunta import runner as runner_orig
from marabunta.database import IrModuleModule


class VersionRunner(runner_orig.VersionRunner):
    """Extend to use install operation when running version."""

    def perform_addons(self):
        """Extend to use install operation before upgrade one."""
        version = self.version
        module_table = IrModuleModule(self.database)
        addons_state = module_table.read_state()
        install_operation = version.install_addons_operation(
            addons_state,
            mode=self.config.mode
        )
        exclude = self.runner.upgraded_addons
        self.log('Installation of addons')
        operation = install_operation.operation(exclude_addons=exclude)
        if operation:
            operation.execute(self.log)
        # Exclude already installed modules from allow_serie or upgrade
        # operation.
        self.runner.upgraded_addons |= install_operation.to_install
        super().perform_addons()
