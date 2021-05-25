import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--profile', action='store_true', default=False, help="Enable profiling; print report on exit")
parser.add_argument('--callgraph', action='store_true', default=False, help="Enable profiling; show call graph on exit")
parser.add_argument('--dbg-on', type=str, default=None, help="Start debugging console to catch exceptions matching pattern", dest="dbg_on")
parser.add_argument('-x', '--exit-on-error', action="store_true", default=False, dest="exit_on_error", help='Whether to exit immidiately on the first exception during initial Manager setup')
parser.add_argument('-p', '--pdb-on-error', action="store_true", default=False, dest="pdb_on_error", help='Start PDB on exception during initial Manager setup')
parser.add_argument('-c', '--config', type=str, help='Configuration file to load')
parser.add_argument('-a', '--config-name', type=str, nargs="*", dest="config_name", default=(), help='Named configuration(s) to load')
parser.add_argument('-m', '--module', type=str, nargs="*", default=(), help='Module name(s) to load')
parser.add_argument('-b', '--base-dir', type=str, dest="base_dir", help='Base directory to use')
parser.add_argument('-s', '--storage-dir', type=str, dest="storage_dir", help='Storage directory to use')
parser.add_argument('-n', '--no-manager', action="store_true", default=False, dest="no_manager", help='Do not load manager module')
parser.add_argument('-d', '--disable', type=str, nargs="*", help='Disable the device(s) specified')
parser.add_argument('-D', '--disable-all', action="store_true", default=False, dest="disable_all", help='Disable all devices')

args = parser.parse_args()
