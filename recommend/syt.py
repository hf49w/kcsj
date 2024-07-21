import os
from django.conf import settings
from django.core.management.base import BaseCommand
class Command(BaseCommand):
      help = 'Example command using settings.configure()'
      def handle(self, *args, **options):
          os.environ.setdefault("DJANGO_SETTINGS_MODULE","myproject.settings")
          settings.configure()
          import sqlite3
          from pathlib import Path
          from models import Tag
          path = Path(r'C:\Users\dell\Desktop\video_data0.db')
          conn = sqlite3.connect(path)
          cursor = conn.cursor()
          cursor.execute('SELECT DISTINCT tags FROM video_info')
          for row in cursor.fetchall():
           tags_str = row[0]
           tags_list = tags_str.split(',') if tags_str else []
           for tag_name in tags_list:
             tag_name = tag_name.strip() 
             if tag_name:    
                Tag.objects.get_or_create(name=tag_name)
                print(f"处理标签：{tag_name}")
          conn.close()

syt=Command()
syt.handle()