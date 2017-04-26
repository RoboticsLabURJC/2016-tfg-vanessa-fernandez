include_directories(
	${GAZEBO_INCLUDE_DIRS}
    ${INTERFACES_CPP_DIR}
    ${LIBS_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${easyiceconfig_INCLUDE_DIRS}
)

link_directories(${GAZEBO_LIBRARY_DIRS}
    ${easyiceconfig_LIBRARY_DIRS}
)

#set( CMAKE_CXX_FLAGS "-Wall" )
    
add_library(lasertaxi SHARED laser.cc)
target_link_libraries(lasertaxi 
	RayPlugin 
	${GAZEBO_libraries} 
	${ZeroCIce_LIBRARIES} 
	colorspacesmm
    	JderobotInterfaces
	${easyiceconfig_LIBRARIES}
) 

INSTALL (TARGETS lasertaxi 
	DESTINATION share/jderobot/gazebo/plugins/taxiLaser/ 
	COMPONENT core)

FILE(GLOB_RECURSE CFG_FILES ${CMAKE_CURRENT_SOURCE_DIR}/cfg/*.cfg)
INSTALL (FILES ${CFG_FILES} DESTINATION share/jderobot/gazebo/plugins/taxiLaser/ COMPONENT core)

#MIO endif()
