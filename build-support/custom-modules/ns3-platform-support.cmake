# Copyright (c) 2023 Universidade de Brasília
#
# SPDX-License-Identifier: GPL-2.0-only
#
# Author: Gabriel Ferreira <gabrielcarvfer@gmail.com>

# This is where we check for platform specifics

# WSLv1 doesn't support tap features
if(EXISTS "/proc/version")
  file(READ "/proc/version" CMAKE_LINUX_DISTRO)
  string(FIND "${CMAKE_LINUX_DISTRO}" "Microsoft" res)
  if(res EQUAL -1)
    set(WSLv1 False)
  else()
    set(WSLv1 True)
  endif()
endif()

# cmake-format: off
# Windows injects **BY DEFAULT** its %PATH% into WSL $PATH
# Detect and warn users how to disable path injection
# cmake-format: on
if("$ENV{PATH}" MATCHES "/mnt/c/")
  message(
    WARNING
      "To prevent Windows path injection on WSL, append the following to /etc/wsl.conf, then use `wsl --shutdown` to restart the WSL VM:
[interop]
appendWindowsPath = false"
  )
endif()

# Set Linux flag if on Linux
if(UNIX AND NOT APPLE)
  if("${CMAKE_SYSTEM_NAME}" STREQUAL "Linux")
    set(LINUX TRUE)
  else()
    set(BSD TRUE)
  endif()
  add_definitions(-D__LINUX__)
endif()

if(APPLE)
  add_definitions(-D__APPLE__)
  # cmake-format: off
    # Configure find_program to search for AppBundles only if programs are not found in PATH.
    # This prevents Doxywizard from being launched when the Doxygen.app is installed.
    # https://gitlab.kitware.com/cmake/cmake/-/blob/master/Modules/FindDoxygen.cmake
    # cmake-format: on
  set(CMAKE_FIND_APPBUNDLE "LAST")
endif()

if(WIN32)
  set(NS3_PRECOMPILE_HEADERS OFF
      CACHE BOOL "Precompile module headers to speed up compilation" FORCE
  )

  # For whatever reason getting M_PI and other math.h definitions from cmath
  # requires this definition
  # https://docs.microsoft.com/en-us/cpp/c-runtime-library/math-constants?view=vs-2019
  add_definitions(/D_USE_MATH_DEFINES)
endif()

set(cat_command cat)

if(CMAKE_XCODE_BUILD_SYSTEM)
  set(XCODE True)
else()
  set(XCODE False)
endif()

if(${XCODE})
  # Prevent multi-config generators from placing output files into per
  # configuration directory
  foreach(OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES})
    string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG}
        ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
    )
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG}
        ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}
    )
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG}
        ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY}
    )
  endforeach()
endif()