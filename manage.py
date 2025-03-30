#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def create_migration(message):
    """Create a new migration with alembic."""
    subprocess.run(['alembic', 'revision', '--autogenerate', '-m', message])

def upgrade_db(revision='head'):
    """Upgrade database to the specified revision (default: head)."""
    subprocess.run(['alembic', 'upgrade', revision])

def downgrade_db(revision='-1'):
    """Downgrade database by a given number of revisions (default: -1)."""
    subprocess.run(['alembic', 'downgrade', revision])

def show_history():
    """Show migration history."""
    subprocess.run(['alembic', 'history'])

def main():
    parser = argparse.ArgumentParser(description='Database migration management')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('message', help='Migration message')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('revision', nargs='?', default='head', help='Target revision (default: head)')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', nargs='?', default='-1', help='Revisions to downgrade (default: -1)')
    
    # History command
    subparsers.add_parser('history', help='Show migration history')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_migration(args.message)
    elif args.command == 'upgrade':
        upgrade_db(args.revision)
    elif args.command == 'downgrade':
        downgrade_db(args.revision)
    elif args.command == 'history':
        show_history()
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 