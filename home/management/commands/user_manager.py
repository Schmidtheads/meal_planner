from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import os
import json
import sys

parent_path = os.path.abspath("..") + "\\meal_planner"
sys.path.append(parent_path)

CURDIR = os.path.dirname(os.path.abspath(__file__))

class Command(BaseCommand):

    help = 'Creates user groups in Django database for use with Meal Planner'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config', type=str,
            default='<DEFAULT>',
            help='Path to JSON file with group permissions'
        )

        return super().add_arguments(parser)


    def handle(self, *args, **kwargs):

        permission_config = kwargs['config']

        # if not specified at command line, use default for config file
        if permission_config == '<DEFAULT>':
            permission_config = os.path.join(CURDIR, 'user_permissions.json')

        with open(permission_config, 'r', encoding='utf-8') as infile:
            config = json.load(infile)

        groups = config['settings']['groups']
        self.setup_groups(groups)
        print('Done')


    def setup_groups(self, groups: list):

        for group in groups:
            g_name = group['name']
            permissions = group['permissions']

            print(f'Processing group {g_name}')
            group_obj, created = Group.objects.get_or_create(name=g_name)

            if created:
                print('  Group created')
            else:
                print('  Updating group permissions')

            # clear all group permissions prior to re-establishing them
            group_obj.permissions.clear()  # type: ignore

            for permission in permissions:
                try:
                    permission_obj = Permission.objects.get(codename=permission)
                except Exception as ex:
                    print(f'**ERR** Unable to get permission "{permission}"\n{ex}')
                    permission_obj = None

                if permission_obj is not None:
                    group_obj.permissions.add(permission_obj)  # type: ignore
