# -*- coding: utf-8 -*-

import itertools
import os
import re
import shutil
import subprocess
import sys

def folders(path):
  for root, dirs, files in os.walk(path):
    for d in dirs:
      yield (root, d)
    return

def files(path):
  return itertools.izip(itertools.repeat(path), os.listdir(path))

months={
    1:u'Январь',
    2:u'Февраль',
    3:u'Март',
    4:u'Апрель',
    5:u'Май',
    6:u'Июнь',
    7:u'Июль',
    8:u'Август',
    9:u'Сентябрь',
    10:u'Октябрь',
    11:u'Ноябрь',
    12:u'Декабрь'
    }

_reWinPhone = re.compile(r'WP_(\d{4})(\d{2})(\d{2})_.*')

def wpFileInfo(name):
  m = _reWinPhone.match(name)
  if not m:
    return None
  return (int(m.group(1), 10), int(m.group(2), 10), int(m.group(3), 10))

_reFolder = re.compile(r'(\d{2})-(\d{2})-(\d{2})')

def _ensure_exists(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)


def resortWpFiles(path):
  for (p, f) in list(files(path)):
    info = wpFileInfo(f)
    if info is None:
      continue
    (year,month,day) = info
    year = year % 100
    full_dir_path = os.path.join(path, "%02d-%02d-%02d" % (year, month, day))
    full_file_path = os.path.join(p, f)
    _ensure_exists(full_dir_path)
    shutil.move(full_file_path, full_dir_path)


def replaceMonth(path, name):
  m = _reFolder.match(name)
  if not m:
    return None
  year = 2000 + int(m.group(1), 10)
  month = int(m.group(2), 10)
  day = int(m.group(3), 10)
  localizedMonth=months[month]
  year_path = "%4d" % year
  day_path = "%4d-%02d.%s-%02d" % (year, month, localizedMonth, day)
  return os.path.join(path, year_path, day_path)


def renameFolders(path):
  for root, f in list(folders(path)):
    newPath=replaceMonth(path, f)
    full_folder_path = os.path.join(root, f)
    _ensure_exists(os.path.dirname(newPath))
    if os.path.exists(newPath):
      raise RuntimeError, "%s already exists" % newPath
    shutil.move(full_folder_path, newPath)


def renamePhotos(_exiftool, path):
  subprocess.check_call([_exiftool, '-FileName<${DateTimeOriginal}-%f.%e', '-d', '%Y-%m-%d-%H-%M-%S', '.'], cwd=path)


def sortPhotosByFolders(_exiftool, path):
  subprocess.check_call([_exiftool, '-r', '-Directory<DateTimeOriginal', '-d', '%y-%m-%d', '.'], cwd=path)


if __name__ == '__main__':
  path = 'sandbox'
  if len(sys.argv) > 1:
    path = sys.argv[1]
  renamePhotos('exiftool.exe', path)
  sortPhotosByFolders('exiftool.exe', path)
  resortWpFiles(path)
  renameFolders(path)
