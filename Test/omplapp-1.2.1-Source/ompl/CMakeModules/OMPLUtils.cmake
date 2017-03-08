macro(add_ompl_test test_name)
  add_executable(${ARGV})
  target_link_libraries(${test_name}
    ompl
    ${Boost_PROGRAM_OPTIONS_LIBRARY}
    ${Boost_SERIALIZATION_LIBRARY}
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_UNIT_TEST_FRAMEWORK_LIBRARY})
  add_test(NAME ${test_name} COMMAND $<TARGET_FILE:${test_name}>)
endmacro(add_ompl_test)

macro(add_ompl_python_test test_file)
  get_filename_component(test_name "${test_file}" NAME)
  add_test(${test_name} "${PYTHON_EXEC}" "${CMAKE_CURRENT_SOURCE_DIR}/${test_file}" "-v")
endmacro(add_ompl_python_test)

# Computes the link flags and package dependencies for a list of targets. This command:
#
#   target_link_flags(target1 target2 ...)
#
# sets the following variables in the calling context:
#
#   target1_LINK_FLAGS
#   target1_PKG_DEPS
#
# Note that the link flags for *all* targets are combined into two variables.
# The second variable is used for libraries that were found with pkg-config.
# This function is intended for generating pkg-config *.pc files.
function(target_link_flags)
    set(_link_flags "")
    set(_pkg_deps "")
    foreach(_target ${ARGV})
        get_target_property(_link_libs ${_target} LINK_LIBRARIES)
        foreach(_lib ${_link_libs})
            get_filename_component(_basename ${_lib} NAME_WE)
            get_filename_component(_ext ${_lib} EXT)
            # add -lfoo to link flags
            if (_lib MATCHES "-l.+")
                list(APPEND _link_flags "${_lib}")
            else()
                # add link flags for dynamic libraries
                if(_ext STREQUAL ${CMAKE_SHARED_LIBRARY_SUFFIX})
                    string(REPLACE ${CMAKE_SHARED_LIBRARY_PREFIX} "" _libname ${_basename})
                    list(APPEND _link_flags "-l${_libname}")
                else()
                    # OS X frameworks, which are also dynamic libraries
                    if (_ext STREQUAL ".framework")
                        list(APPEND _link_flags "-framework ${_basename}")
                    else()
                        # libraries found by pkg-config are just returned as "foo",
                        # not "libfoo.so".
                        if(NOT _ext)
                            list(FIND ARGV ${_basename} _index)
                            if (_index EQUAL -1)
                                list(APPEND _pkg_deps "${_basename}")
                          endif()
                        endif()
                    endif()
                endif()
            endif()
        endforeach()
    endforeach()
    list(REMOVE_DUPLICATES _link_flags)
    foreach(_flag ${_link_flags})
        set(_link_flags_str "${_link_flags_str} ${_flag}")
    endforeach()
    string(STRIP "${_link_flags_str}" _link_flags_str)
    set(${ARGV0}_LINK_FLAGS "${_link_flags_str}" PARENT_SCOPE)

    list(REMOVE_DUPLICATES _pkg_deps)
    foreach(_dep ${_pkg_deps})
        set(_pkg_dep_str "${_pkg_dep_str} ${_dep}")
    endforeach()
    string(STRIP "${_pkg_dep_str}" _pkg_dep_str)
    set(${ARGV0}_PKG_DEPS "${_pkg_dep_str}" PARENT_SCOPE)
endfunction()

option(OMPL_VERSIONED_INSTALL "Append version suffix to binaries, libraries, and include dir." OFF)
if (OMPL_VERSIONED_INSTALL)
    set(OMPL_INSTALL_SUFFIX "-${OMPL_MAJOR_VERSION}.${OMPL_MINOR_VERSION}")
else()
    set(OMPL_INSTALL_SUFFIX "")
endif()
