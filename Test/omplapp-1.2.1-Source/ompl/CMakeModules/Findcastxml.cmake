include(FindPackageHandleStandardArgs)

if(NOT CASTXML)
    find_program(CASTXML NAMES castxml)
endif()

if (CASTXML)
    set(CASTXMLCFLAGS "-std=c++11")

    if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        set(CASTXMLCOMPILER "g++")
    else()
        if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
            set(CASTXMLCOMPILER "clang++")
        else()
            if (MSVC)
                set(CASTXMLCOMPILER "msvc8")
            endif()
        endif()
    endif()

    set(CASTXMLCONFIG "[gccxml]\nxml_generator=castxml\nxml_generator_path=${CASTXML}\ncompiler=${CASTXMLCOMPILER}\ncompiler_path=${CMAKE_CXX_COMPILER}\n")

    set(_candidate_include_path
        "${OMPL_INCLUDE_DIR}"
        "${OMPLAPP_INCLUDE_DIR}"
        "${PYTHON_INCLUDE_DIRS}"
        "${Boost_INCLUDE_DIR}"
        "${ASSIMP_INCLUDE_DIRS}"
        "${ODEINT_INCLUDE_DIR}"
        "${EIGEN3_INCLUDE_DIR}"
        "${OMPL_INCLUDE_DIR}/../py-bindings")
    if(MINGW)
        execute_process(COMMAND "${CMAKE_CXX_COMPILER}" "-dumpversion"
            OUTPUT_VARIABLE _version OUTPUT_STRIP_TRAILING_WHITESPACE)
        get_filename_component(_path "${CMAKE_CXX_COMPILER}" DIRECTORY)
        get_filename_component(_path "${_path}" DIRECTORY)
        list(APPEND _candidate_include_path
            "${_path}/include"
            "${_path}/lib/gcc/mingw32/${_version}/include"
            "${_path}/lib/gcc/mingw32/${_version}/include/c++"
            "${_path}/lib/gcc/mingw32/${_version}/include/c++/mingw32")
    endif()
    list(REMOVE_DUPLICATES _candidate_include_path)
    set(CASTXMLINCLUDEPATH ".")
    foreach(dir ${_candidate_include_path})
        if(EXISTS ${dir})
            set(CASTXMLINCLUDEPATH "${CASTXMLINCLUDEPATH};${dir}")
        endif()
    endforeach()
    set(CASTXMLCONFIG "${CASTXMLCONFIG}include_paths=${CASTXMLINCLUDEPATH}\n")
    if(CASTXMLCFLAGS)
        set(CASTXMLCONFIG "${CASTXMLCONFIG}cflags=${CASTXMLCFLAGS}\n")
    endif()
    set(CASTXMLCONFIGPATH "${PROJECT_BINARY_DIR}/castxml.cfg")
    file(WRITE "${CASTXMLCONFIGPATH}" "${CASTXMLCONFIG}")
    set(CASTXMLCONFIGPATH "${CASTXMLCONFIGPATH}" PARENT_SCOPE)
endif()

find_package_handle_standard_args(castxml DEFAULT_MSG CASTXML)
