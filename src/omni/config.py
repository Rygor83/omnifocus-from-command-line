#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------
""" Configuration file management """

import errno
import os
from configparser import ConfigParser
import pathlib
from typing import Union, NamedTuple
import click
import shutil


class OmniConfig(NamedTuple):
    """Object containing configuration's parameters"""

    host: str
    port: int
    from_mail: str
    to_mail: str


class Config:
    """Configuration file management"""

    def __init__(self, config_path: Union[str, pathlib.Path] = None):
        self.ini_name = "omni_config.ini"
        self.plugin_folder_name = "plugins"
        self.config_path = os.path.join(config_path, self.ini_name) if config_path else os.path.join(self.set_path,
                                                                                                     self.ini_name)
        self.plugin_path = os.path.join(config_path, 'plugins') if config_path else os.path.join(self.set_path,
                                                                                                self.plugin_folder_name)

    def read(self) -> OmniConfig:
        """Return OmniConfig object after reading configuration file"""
        parser = ConfigParser(interpolation=None)
        if not self.exists():
            self.create()

        parser.read(self.config_path)  # Examples for live.com/outlook.com
        host = parser.get("GENERAL", "host")  # host = "smtp-mail.outlook.com"
        port = parser.getint("GENERAL", "port")  # port = "587"
        from_mail = parser.get("GENERAL", "from")  # FROM = "test@live.com"
        to_mail = parser.get("GENERAL", "to")  # TO = "test@sync.omnigroup.com"

        return OmniConfig(host, port, from_mail, to_mail)

    def create(self) -> None:
        """Creating a configuration file"""

        folder, file = os.path.split(self.config_path)

        parser = ConfigParser(allow_no_value=True)
        parser["GENERAL"] = {
            "; host - SMTP server name. For example for live.com/outlook.com - smtp-mail.outlook.com": None,
            "host": "smtp-mail.outlook.com",
            "; port - SMTP port. For example for live.com/outlook.com - 587": None,
            "port": '587',
            "; FROM - mail address from which you send mails": None,
            "from": 'test@live.com',
            "; TO - mail address to which you send mails. You can read more here https://support.omnigroup.com/omnifocus-mail-drop/": None,
            "to": 'test@sync.omnigroup.com',
        }

        if not os.path.exists(self.plugin_path):
            os.mkdir(self.plugin_path)

        with open(self.config_path, "w+", encoding="utf-8") as configfile:
            parser.write(configfile)

    def exists(self) -> bool:
        """Checking if config file exists"""
        return os.path.exists(self.config_path)

    @property
    def set_path(self) -> Union[str, pathlib.Path]:
        """Setting path for saving config file"""
        path = click.get_app_dir('omnifocus', roaming=False)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        return path

    def open_config(self) -> None:
        """Open configuration file for editing"""
        click.launch(self.config_path)

    def remove_config(self):
        """ Remove encryption keys """
        os.remove(self.config_path)

    def remove_plugin_folder(self):
        """ Remove encryption keys """
        shutil.rmtree(self.plugin_path)
