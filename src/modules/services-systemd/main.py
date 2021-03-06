#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# === This file is part of Calamares - <https://github.com/calamares> ===
#
#   Copyright 2014, Philip Müller <philm@manjaro.org>
#   Copyright 2014, Teo Mrnjavac <teo@kde.org>
#   Copyright 2017, Alf Gaida <agaida@siduction.org>
#   Copyright 2018, Adriaan de Groot <groot@kde.org>
#
#   Calamares is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Calamares is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Calamares. If not, see <http://www.gnu.org/licenses/>.

import libcalamares


def systemctl(targets, command, suffix):
    """
    For each entry in @p targets, run "systemctl <command> <thing>",
    where <thing> is the entry's name plus the given @p suffix.
    (No dot is added between name and suffix; suffix may be empty)

    Returns a failure message, or None if this was successful.
    Services that are not mandatory have their failures suppressed
    silently.
    """
    for svc in targets:
        if isinstance(svc, str):
            name = svc
            mandatory = False
        else:
            name = svc["name"]
            mandatory = svc.get("mandatory", False)

        ec = libcalamares.utils.target_env_call(
            ['systemctl', command, "{}{}".format(name, suffix)]
            )

        if ec != 0:
            if mandatory:
                return ("Cannot {} systemd {} {}".format(command, suffix, name),
                        "systemctl {} call in chroot returned error code {}".format(command, ec)
                        )
            else:
                libcalamares.utils.warning(
                    "Cannot {} systemd {} {}".format(command, suffix, name)
                    )
                libcalamares.utils.warning(
                    "systemctl {} call in chroot returned error code {}".format(command, ec)
                    )
    return None


def run():
    """
    Setup systemd services
    """
    cfg = libcalamares.job.configuration

    # note that the "systemctl enable" and "systemctl disable" commands used
    # here will work in a chroot; in fact, they are the only systemctl commands
    # that support that, see:
    # http://0pointer.de/blog/projects/changing-roots.html

    r = systemctl(cfg.get("services", []), "enable", ".service")
    if r is not None:
        return r

    r = systemctl(cfg.get("targets", []), "enable", ".target")
    if r is not None:
        return r

    r = systemctl(cfg.get("disable", []), "disable", ".service")
    if r is not None:
        return r

    r = systemctl(cfg.get("disable-targets", []), "disable", ".target")
    if r is not None:
        return r

    r = systemctl(cfg.get("mask", []), "mask", "")
    if r is not None:
        return r


    # This could have just been return r
    return None
