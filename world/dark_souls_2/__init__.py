from .base_world import *
from .base_world import DS2World
from .WeaponUpgradeIntegration import install_weapon_upgrade_integration

# base_world.py preserves the original implementation while this package wrapper owns the
# public world module. Keep metadata identical to a class defined directly in __init__.py.
DS2World.__module__ = __name__
DS2World.__file__ = __file__
DS2World.settings_key = "dark_souls_2_options"

install_weapon_upgrade_integration(DS2World)
