
include_directories(
	${GAZEBO_INCLUDE_DIRS}
    ${INTERFACES_CPP_DIR}
    ${LIBS_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${easyiceconfig_INCLUDE_DIRS}
)

link_directories(
    ${GAZEBO_LIBRARY_DIRS}
    ${easyiceconfig_LIBRARY_DIRS}
)
#boost_system 
add_library(miniCarMotors SHARED miniCarMotors.cc)
target_link_libraries(miniCarMotors 
	${GAZEBO_libraries} 
	${ZeroCIce_LIBRARIES} 

    ${easyiceconfig_LIBRARIES}
    colorspacesmm
    JderobotInterfaces
)

INSTALL (TARGETS miniCarMotors DESTINATION share/jderobot/gazebo/plugins/miniCar/ COMPONENT core)
FILE(GLOB_RECURSE CFG_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cfg)
INSTALL (FILES ${CFG_FILES} DESTINATION share/jderobot/gazebo/plugins/miniCar/ COMPONENT core)


