import argparse
import sys
import os
import json
from datetime import datetime
from src.introspect import introspect_database

def handle_introspect(args):
    """Handle the introspect command
    
    Args:
        args: Parsed command line arguments containing:
            conn (str): Database connection string
            schema (str): Database schema name
            format (str): Output format (json)
            output_dir (str): Directory for output files
            
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        result = introspect_database(args.conn, args.schema)
        
        ensure_output_dir(args.output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"schema_introspection_{args.schema}_{timestamp}.json"
        filepath = os.path.join(args.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(result)
        
        print(f"Schema introspection saved to: {filepath}")
        
        result_dict = json.loads(result)
        if 'error' in result_dict:
            print("Error:", result_dict['error'])
            return 1
        return 0
        
    except Exception as e:
        print(f"Error during introspection: {str(e)}")
        return 1

COMMANDS = {
    'introspect': {
        'handler': handle_introspect,
        'help': 'Introspect database schema',
        'arguments': [
            {
                'name': '--conn',
                'required': True,
                'help': 'Database connection string (e.g. postgresql://user:pass@localhost:5432/mydb)'
            },
            {
                'name': '--schema',
                'default': 'public',
                'help': 'Database schema to introspect (default: public)'
            },
            {
                'name': '--format',
                'choices': ['json'],
                'default': 'json',
                'help': 'Output format (default: json)'
            },
            {
                'name': '--output-dir',
                'default': 'output',
                'help': 'Directory to store output files (default: output)'
            }
        ]
    }
}

def ensure_output_dir(directory):
    """Create output directory if it doesn't exist
    
    Args:
        directory (str): Path to directory to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def setup_parser():
    """Set up command line argument parser
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Database Schema Introspection Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version argument
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add commands from registry
    for cmd_name, cmd_info in COMMANDS.items():
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_info['help'])
        for arg in cmd_info['arguments']:
            kwargs = {k: v for k, v in arg.items() if k != 'name'}
            cmd_parser.add_argument(arg['name'], **kwargs)
    
    return parser

def main():
    """Main entry point for the application
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    handler = COMMANDS[args.command]['handler']
    return handler(args)

if __name__ == "__main__":
    sys.exit(main())
