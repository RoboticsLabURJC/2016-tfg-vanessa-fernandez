# Install script for directory: /home/vanejessi/Escritorio/JdeRobot/src/drivers/gazeboserver/plugins/taxiLaser

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "core")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser" TYPE SHARED_LIBRARY FILES "/home/vanejessi/Escritorio/JdeRobot/src/drivers/gazeboserver/plugins/taxiLaser/liblasertaxi.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so"
         OLD_RPATH "/home/vanejessi/Escritorio/JdeRobot/src/interfaces/cpp/jderobot:/home/vanejessi/Escritorio/JdeRobot/src/libs/colorspaces:/home/vanejessi/Escritorio/JdeRobot/src/libs/jderobotutil:/home/vanejessi/Escritorio/JdeRobot/src/libs/progeo:/home/vanejessi/Escritorio/JdeRobot/src/libs/pioneer:/home/vanejessi/Escritorio/JdeRobot/src/libs/fuzzylib:/home/vanejessi/Escritorio/JdeRobot/src/libs/visionlib:/home/vanejessi/Escritorio/JdeRobot/src/libs/parallelIce:/usr/lib/x86_64-linux-gnu/gazebo-7/plugins:/usr/lib/x86_64-linux-gnu/c++11/libIceUtil.so:/usr/lib/x86_64-linux-gnu/c++11/libIce.so:/usr/lib/x86_64-linux-gnu/c++11/libIceStorm.so:/usr/lib/x86_64-linux-gnu/c++11/libIceBox.so:/usr/lib/x86_64-linux-gnu/c++11/libIceGrid.so:/usr/lib/x86_64-linux-gnu/c++11/libIcePatch2.so:/usr/lib/x86_64-linux-gnu/c++11/libIceSSL.so:/usr/lib/x86_64-linux-gnu/libxml2.so:/usr/lib/x86_64-linux-gnu/libGLU.so:/usr/lib/x86_64-linux-gnu/libGL.so:/usr/lib/x86_64-linux-gnu/libglut.so:/usr/lib/x86_64-linux-gnu/libXmu.so:/usr/lib/x86_64-linux-gnu/libXi.so:/usr/lib/libOpenNI.so:/usr/lib/x86_64-linux-gnu/libtinyxml.so:/home/vanejessi/Escritorio/JdeRobot/src/libs/easyiceconfig_cpp:/usr/lib/x86_64-linux-gnu/c++11:/home/vanejessi/Escritorio/JdeRobot/src/libs/visionlib/colorspaces:/home/vanejessi/Escritorio/JdeRobot/src/interfaces:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/jderobot/gazebo/plugins/taxiLaser/liblasertaxi.so")
    endif()
  endif()
endif()

