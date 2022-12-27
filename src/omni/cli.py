#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

# TODO: Как сделать так, чтобы не вводить пароль постоянно. Ввел 1 раз и пару часов не нужно вводить. Где хранить?
#  https://martinheinz.dev/blog/59

import sys
import smtplib
import getpass
import logging
from email.message import EmailMessage
import click
import rich_click as click
import click_log
from omni.config import Config
from omni import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'],
                        show_default=True, token_normalize_func=lambda x: x.lower())
log_level = ['--log_level', '-l']
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


def open_config(ctx, param, value):
    """
    Open configuration file for editing
    """
    if not value or ctx.resilient_parsing:
        return
    cfg = Config()
    cfg.open_config()
    ctx.exit()


def open_user_folder(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.launch(click.get_app_dir('kalc', roaming=False))
    ctx.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-s", "--step", "stepbystep", help="Create task/action step by step", is_flag=True, default=False)
@click.option("-config", is_flag=True, help="Open config", callback=open_config, expose_value=False, is_eager=True)
@click.option('-path', '--config_path', 'config_path', help="Path to external omni_config.ini folder",
              type=click.Path(exists=True, dir_okay=True))
@click_log.simple_verbosity_option(logger, *log_level, default='ERROR')
@click.version_option(version=__version__)
def omni_cli(stepbystep, config_path):
    """
    \b
    OmniFocus (iOS powerful task management) Mail Drop from command line (https://shorturl.at/dlBLZ)
    \b
    Launch 'omni -s' for step by step task creation or 'omni' to type task as one sentence
    \b
    Example for 'omni' command:
    --Fix bathroom wiring! @house ::maintenance #friday #next monday $30 min //It's driving me crazy.
    \b
    Syntax rules:
    -- for Task/Action
    !  for Flag at the end of Task/Action
    >  or :: for Project
    @  for Tag
    #  for Start date. Use date expression (https://shorturl.at/cDHIN)
    #  for Due dates. Use date expression (https://shorturl.at/cDHIN)
    $  for Time estimate, like 5m, 1h, and so on
    // for Notes
    """

    cfg = Config(config_path)
    _config = cfg.read()

    HOST = _config.host
    PORT = _config.port
    FROM = _config.from_mail
    TO = _config.to_mail

    logger.info(f"host: {HOST}")
    logger.info(f"port: {PORT}")
    logger.info(f"from_mail: {FROM}")
    logger.info(f"to_mail: {TO}")

    text = ""

    if stepbystep:
        # https://www.omni-automation.com/omnifocus/task.html -> Transport Text Parsing

        # The first line and any other lines starting with -- (double-hyphens) become new actions.
        # Other lines become notes for the preceding action.
        text = text + " --" + click.prompt('-- Task')
        # To flag the action, use ! (exclamation point) at the end of the action title.
        ans = click.confirm("! Flag the action/task?", default=False)
        if ans:
            text = text + "!"
        # To specify a project, use > (greater-than sign) or :: (double-colons), followed by a project name
        # or abbreviation. The colons are nicer for the iPhone because they are on the first shifted keyboard
        # rather than the less-accessible math keyboard. The project string is matched exactly as if it was
        # entered in a project cell in OmniFocus.
        ans = click.prompt('>  Project', default='', show_default=False)
        if ans:
            text = text + " >" + ans
        # To specify a tag, use @ (at sign), followed by a tag name or abbreviation.
        # Like project names, the context name is matched exactly as it would be in OmniFocus.
        ans = click.prompt('@  Tag ', default='', show_default=False)
        if ans:
            text = text + " @" + ans
        # To enter start or due dates, use # (number sign), followed by some date expression (like 9-30-2014).
        # If there is only one date, it becomes the due date. If there are two (each with its own number sign),
        # the first becomes the start date and the second becomes the due date.
        ans = click.prompt('#  Start date', default='', show_default=False)
        if ans:
            text = text + " #" + ans
        ans = click.prompt('#  Due date', default='', show_default=False)
        if ans:
            text = text + " #" + ans
        # To enter a time estimate, use $ (dollar sign—time is money) followed by some duration
        # expression (like 5m, 1h, and so on); you can use the same duration expressions that you use in OmniFocus.
        ans = click.prompt('$  Duration', default='', show_default=False)
        if ans:
            text = text + " $" + ans
        # You can also add a note on the same line as an action title by separating them with // (double-slashes).
        # Anything after the double-slashes becomes a note, but double-slashes in a URL like omnigroup.com don’t count.
        ans = click.prompt('// Notes', default='', show_default=False)
        if ans:
            text = text + " //" + ans

        logger.info(f"TASK: {text}")

    else:
        text = click.prompt('Task')

    send_mail(HOST, PORT, FROM, TO, text)


def send_mail(host, port, from_mail, to_mail, message):
    """
    Send email

    :param host: SMTP server name for mail address from which you send mails
    :param port: SMTP port
    :param from_mail: mail address from which we send mails
    :param to_mail: mail address to which we send mails
    :param message: message we need to send
    :return: 
    """
    msg = EmailMessage()
    msg['Subject'] = message
    msg['From'] = from_mail
    msg['To'] = to_mail
    pwd = getpass.getpass(prompt=f"Password for '{from_mail}': ", stream=None)
    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    try:
        server.login(from_mail, pwd)
    except Exception as err:
        print(f"ERROR: {err=}, {type(err)=}")
        sys.exit()
    server.send_message(msg)
    server.quit()


if __name__ == "__main__":
    omni_cli()
