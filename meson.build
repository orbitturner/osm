# Copyright(c) 2025  AGPL-3.0 License -  Umar Ba <jUmarB@protonmail.com> github.com/Jukoo
# /!\ Should be compiled inside container /!\
# -------------------------------------------------------
project('osmon', 'c',
  version : '0.1',
  license:['AGPL-3.0-only'],
  default_options : [
    'c_std=gnu99',
    'warning_level=3', 
    'bindir=/usr/local/bin', 
    'datadir=/data'])

# - Quick Summay where the essentials files are stored 
summary({
'config   ->': '/etc/osm',
'data     ->': get_option('datadir'),
'osmon bins ->': get_option('bindir'),
}, section: 'Osm  Dispatching  Summary')


pkg =import('pkgconfig')
cc = meson.get_compiler('c') 

add_project_arguments(
  cc.get_supported_arguments([
    '-Wcomment',
    '-Wformat',
    '-Wunused-parameter',
    '-Wreturn-type',
    '-Wpedantic',
    '-Wparentheses',
    '-Wmissing-braces'
    ]), 
  # - TODO | NOTE: Should be intergrate in special config file 
  # - The NO_BLOCKING_MODE  is disabled by default. Set 1 to enable it 
  '-DNO_BLOCKING_MODE=0',
  # - ALLOW OR NOT OVERRIDING EXISTING ENV VARS
  # - BY DEFAULT IS NOT ENABLE CAUZ THE PRIORITY GOES FOR docker-compose.yml  
  '-DALLOW_OVERIDE_ENVAR=0',
  language:'c'
  )

sources =[
  'src/osmanager.c',
  'src/osminitdb.h',
  'src/config_parser.h'
  ]

# - Integrate Sqlite3 dev level  
libsqlite_v3 = dependency('sqlite3')

executable(meson.project_name(),
  sources,
  dependencies:libsqlite_v3,
  install : true,
  install_dir:get_option('bindir')) 
