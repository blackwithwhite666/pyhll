#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.
AC_INIT([murmur3], [1.0.0])
AC_CONFIG_SRCDIR([MurmurHash3.cpp])
AC_CONFIG_MACRO_DIR([m4])

# Initialize automake
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

# Checks for language
AC_LANG([C++])

# Checks for programs.
AC_PROG_CPP
AC_PROG_CXX

# Configure libtool.
AC_ENABLE_STATIC
# AM_PROG_AR is not available in automake v0.11 but it's essential in v0.12.
m4_ifdef([AM_PROG_AR], [AM_PROG_AR])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])
LT_INIT

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
