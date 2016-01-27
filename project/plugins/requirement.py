"""Types related to project requirements."""
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod

from project.internal.metaclass import with_metaclass


class RequirementRegistry(object):
    """Allows creating Requirement instances based on project config."""

    def find_by_env_var(self, env_var, options):
        """Create a requirement instance given an environment variable name.

        Args:
            env_var (str): environment variable name
            options (dict): options from the project file for this requirement

        Returns:
            instance of Requirement
        """
        # future goal will be to un-hardcode this
        if env_var == 'REDIS_URL':
            from .requirements.redis import DefaultRedisRequirement
            return DefaultRedisRequirement(env_var=env_var, options=options)
        else:
            return EnvVarRequirement(env_var=env_var, options=options)


class Requirement(with_metaclass(ABCMeta)):
    """Describes a requirement of the project (from the project config)."""

    def __init__(self, options):
        """Construct a Requirement.

        Args:
            options (dict): dict of requirement options from the project config
        """
        if options is None:
            options = dict()
        self.options = options

    @property
    @abstractmethod
    def title(self):
        """Human-readable title of the requirement."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def config_key(self):
        """When we store config for this requirement, we use this as the key."""
        pass  # pragma: no cover

    @abstractmethod
    def why_not_provided(self, environ):
        """Return why the requirement hasn't been met, or None if it was been.

        Args:
            environ (dict): use this rather than the system environment directly

        Returns:
            Error message string or None
        """
        pass  # pragma: no cover

    @abstractmethod
    def find_providers(self, registry):
        """List all possible providers from the registry."""
        pass  # pragma: no cover


class EnvVarRequirement(Requirement):
    """A requirement that a certain environment variable be set."""

    def __init__(self, env_var, options=None):
        """Construct an EnvVarRequirement for the given ``env_var`` with the given options."""
        super(EnvVarRequirement, self).__init__(options)
        self.env_var = env_var

    @property
    def title(self):
        """Override superclass title."""
        return self.env_var

    @property
    def config_key(self):
        """Override superclass config key."""
        return self.env_var

    def why_not_provided(self, environ):
        """Override superclass to check that the env var is set."""
        value = environ.get(self.env_var, None)
        if value is not None and value != "":
            return None
        else:
            return "Environment variable {env_var} is not set".format(env_var=self.env_var)

    def find_providers(self, registry):
        """Override superclass to look for providers that handle this env var."""
        return registry.find_by_env_var(self, self.env_var)