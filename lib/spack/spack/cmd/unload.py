# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import sys
import os

import llnl.util.tty as tty

import spack.cmd
import spack.cmd.common.arguments as arguments
import spack.util.environment
import spack.user_environment as uenv
import spack.error

description = "remove package from the user environment"
section = "user environment"
level = "short"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    arguments.add_common_arguments(subparser, ['installed_specs'])

    shells = subparser.add_mutually_exclusive_group()
    shells.add_argument(
        '--sh', action='store_const', dest='shell', const='sh',
        help="print sh commands to activate the environment")
    shells.add_argument(
        '--csh', action='store_const', dest='shell', const='csh',
        help="print csh commands to activate the environment")
    shells.add_argument(
        '--fish', action='store_const', dest='shell', const='fish',
        help="print fish commands to load the package")

    subparser.add_argument('-a', '--all', action='store_true',
                           help='unload all loaded Spack packages.')


def unload(parser, args):
    """Unload spack packages from the user environment."""
    if args.specs and args.all:
        raise spack.error.SpackError("Cannot specify specs on command line"
                                     " when unloading all specs with '--all'")

    hashes = os.environ.get(uenv.spack_loaded_hashes_var, '').split(':')
    if args.specs:
        specs = [spack.cmd.disambiguate_spec_from_hashes(spec, hashes)
                 for spec in spack.cmd.parse_specs(args.specs)]
    else:
        specs = spack.store.db.query(hashes=hashes)

    if not args.shell:
        specs_str = ' '.join(args.specs) or "SPECS"
        msg = [
            "`spack unload` works best with spack's shell support.",
            ""
        ] + spack.cmd.common.shell_init_instructions() + [
            'Or, if you want to use `spack unload` without shell',
            'support, you can run one of these:',
            '',
            '    eval `spack unload --sh   %s`  # bash/zsh/sh' % specs_str,
            '    eval `spack unload --csh  %s`  # csh/tcsh' % specs_str,
            '    eval `spack unload --fish %s`  # fish' % specs_str,
            '',
        ]
        tty.msg(*msg)
        return 1

    env_mod = spack.util.environment.EnvironmentModifications()
    for spec in specs:
        env_mod.extend(
            uenv.environment_modifications_for_spec(spec).reversed())
        env_mod.remove_path(uenv.spack_loaded_hashes_var, spec.dag_hash())
    cmds = env_mod.shell_modifications(args.shell)

    sys.stdout.write(cmds)
