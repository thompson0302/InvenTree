# -*- coding: utf-8 -*-

import logging

from django.conf.urls import url, include
from django.conf import settings

import plugins.plugin as plugin


logger = logging.getLogger("inventree")


class MixinBase:
    """general base for mixins"""

    def add_mixin(self, key: str, fnc_enabled=True, cls=None):
        if not hasattr(self, '_mixins'):
            self._mixins = {}
        self._mixins[key] = fnc_enabled
        self.setup_mixin(key, cls=cls)

    def setup_mixin(self, key, cls=None):
        if not hasattr(self, '_mixinreg'):
            self._mixinreg = {}

        # get human name
        human_name = getattr(cls.Meta, 'MIXIN_NAME', key) if cls and hasattr(cls, 'Meta') else key

        # register
        self._mixinreg[key] = {
            'key': key,
            'human_name': human_name,
        }

    @property
    def registered_mixins(self, with_base: bool=False):
        mxins =  getattr(self, '_mixinreg', None)
        if mxins:
            # filter out base
            if not with_base and 'base' in mxins:
                del mxins['base']
            # only return dict
            mxins = [a for a in mxins.values()]
        return mxins

# region mixins
class SettingsMixin:
    """Mixin that enables settings for the plugin"""
    class Meta:
        MIXIN_NAME = 'Settings'

    def __init__(self):
        super().__init__()
        self.add_mixin('settings', 'has_settings', __class__)
        self.settings = self.setup_settings()

    def setup_settings(self):
        """
        setup settings for this plugin
        """
        return getattr(self, 'SETTINGS', None)

    @property
    def has_settings(self):
        """
        does this plugin use custom settings
        """
        return bool(self.settings)

    @property
    def settingspatterns(self):
        if self.has_settings:
            return {f'PLUGIN_{self.plugin_name().upper()}_{key}': value for key, value in self.settings.items()}
        return None


class UrlsMixin:
    """Mixin that enables urls for the plugin"""
    class Meta:
        MIXIN_NAME = 'URLs'

    def __init__(self):
        super().__init__()
        self.add_mixin('urls', 'has_urls', __class__)
        self.urls = self.setup_urls()

    def setup_urls(self):
        """
        setup url endpoints for this plugin
        """
        return getattr(self, 'URLS', None)

    @property
    def base_url(self):
        return f'{settings.PLUGIN_URL}/{self.plugin_name()}/'

    @property
    def urlpatterns(self):
        """
        retruns the urlpatterns for this plugin
        """
        if self.has_urls:
            return url(f'^{self.plugin_name()}/', include((self.urls, self.plugin_name())), name=self.plugin_name())
        return None

    @property
    def has_urls(self):
        """
        does this plugin use custom urls
        """
        return bool(self.urls)


class NavigationMixin:
    """Mixin that enables adding navigation links with the plugin"""
    class Meta:
        MIXIN_NAME = 'Navigation Links'

    def __init__(self):
        super().__init__()
        self.add_mixin('navigation', 'has_naviation', __class__)
        self.navigation = self.setup_navigation()

    def setup_navigation(self):
        """
        setup navigation links for this plugin
        """
        nav_links = getattr(self, 'NAVIGATION', None)
        if nav_links:
            # check if needed values are configured
            for link in nav_links:
                if False in [a in link for a in ('link', 'name', )]:
                    raise NotImplementedError('Wrong Link definition', link)
        return nav_links

    @property
    def has_naviation(self):
        """
        does this plugin define navigation elements
        """
        return bool(self.navigation)
# endregion


class IntegrationPlugin(MixinBase, plugin.InvenTreePlugin):
    """
    The IntegrationPlugin class is used to integrate with 3rd party software
    """

    def __init__(self):
        self.add_mixin('base')

    def mixin(self, key):
        return key in self._mixins

    def mixin_enabled(self, key):
        if self.mixin(key):
            fnc_name = self._mixins.get(key)
            return getattr(self, fnc_name, True)
        return False
