# !/usr/bin/python
import sys
from subprocess import *
from shutil import copy

#------------------------------------------------------------------------------
top = '.'
if sys.platform == 'linux2':
    out                = 'build/linux'
elif sys.platform == 'win32':
    out                = 'build/win32'

#------------------------------------------------------------------------------
sources_geometry =  [
                    'src/geometry/point.cc',
                    'src/geometry/line.cc',
                    'src/geometry/layer.cc',
                    'src/geometry/shape.cc',
                    'src/geometry/group.cc',
                    'src/geometry/bezier_curve.cc'
                    ]

sources_gui      =  [
                    'src/GUI/control.cc',
                    'src/GUI/gui_utils.cc',
                    'src/GUI/window.cc',
                    'src/GUI/button.cc',
                    'src/GUI/label.cc',
                    'src/GUI/map_display.cc',
                    'src/GUI/checkbox.cc'
                    ]

sources_platform=   [ '' ] # will be filled when the project is configured

sources         =   [
                    'src/data_utils.cc',
                    'src/globals.cc',
                    'src/xml_data.cc',
                    ]

utils_cc        =   'src/utils.cc' # requires boost regex

main_cc         =   'src/main.cc'

test_runner_cc  =   'tests/runner.cc' # requires boost test

test_sources    =   [
                    'tests/testPoint.cc',
                    'tests/testLine.cc',
                    'tests/testUtils.cc'
                    ]

# options processed by the configure and build commands
#------------------------------------------------------------------------------
def options( opt ):
    opt.add_option('--static_freeglut', action='store_true', default=False,
            help='statically link freeglut')
    opt.add_option('--static_libs',     action='store_true', default=False,
            help='build and link project libraries')
    opt.add_option('--check',           action='store_true', default=False,
            help='compile and run tests')

# set pl
#------------------------------------------------------------------------------
def configure( cnf ):
    cnf.load( 'g++' )

    abspath = cnf.path.abspath()

    cnf.env.BOOST_VER   = '1_52_0'
    cnf.env.GCC_VER     = '4.7.2'

    cnf.env.INCLUDES                = [ './include' ]
    cnf.env.INCLUDES_FREEGLUT       = [ './deps/freeglut/2.8/include' ]
    cnf.env.INCLUDES_SHAPELIB       = [ './deps/shapelib/include' ]
    cnf.env.STLIB_SHAPELIB          = [ 'shp' ]

    cnf.env.CXXFLAGS = [ '-c', '-g', '-O2', '-Wall', '-fpermissive', '-std=c++0x' ]

    # LINUX
    #--------------------------------------------------------------------------
    if sys.platform.startswith( 'linux' ):
        cnf.env.BOOST_PATH          = '/media/Fatty/code/boost_1_52_0'
        cnf.env.boost_suffix = '' #'so.1.52.0'

        cnf.check_cfg(  package='gtkmm-3.0',
                        args=['--cflags', '--libs'],
                        uselib_store = 'PLATFORM',
                        msg="Checking for gtkmm-3.0" )

        cnf.env.STLIBPATH_FREEGLUT  = [ abspath + '/deps/freeglut/2.8/lib/gcc-ubuntu/lib' ]
        if cnf.options.static_freeglut:
            # static linking freeglut
            cnf.env.STLIB_FREEGLUT      = [ 'glut' ]
            cnf.env.DEFINES_FREEGLUT    = [ 'FREEGLUT_STATIC' ]
        else:
            # dynamic linking freeglut
            cnf.env.LIBPATH_FREEGLUT    = [ abspath + '/deps/freeglut/2.8/lib/gcc-ubuntu/bin' ]
            cnf.env.LIB_FREEGLUT        = [ 'glut', 'GLU' ]

        cnf.env.STLIB_BOOST_REGEX   = [ 'boost_regex' + cnf.env.boost_suffix ]

        # platform-specific stuff
        global sources_platform;
        sources_platform            = [ 'src/platform/linux_gtk.cc' ]

        cnf.env.INCLUDES.append( cnf.env.BOOST_PATH )
        cnf.env.LINKFLAGS_MAIN      = [ '-static-libgcc' ]
        cnf.env.STLIBPATH           = [ abspath + '/lib/gcc-ubuntu' ]
        cnf.env.STLIBPATH_SHAPELIB  = [ abspath + '/deps/shapelib/lib/gcc-ubuntu' ]

        # since project-specific dynamic libraries cannot be easily located
        # on Linux, they are statically linked
        if not cnf.options.static_libs:
            cnf.options.static_libs = True

    # WINDOWS
    #--------------------------------------------------------------------------
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        cnf.env.BOOST_PATH          = 'e:/code/boost_' + cnf.env.BOOST_VER
        cnf.env.boost_suffix        = '-mgw47-mt-1_52'
        cnf.env.FREEGLUT_DLL        = abspath + '/deps/freeglut/2.8/lib/gcc-mingw/bin/freeglut.dll'

        cnf.env.STLIBPATH_FREEGLUT  = [ abspath + '/deps/freeglut/2.8/lib/gcc-mingw/lib' ]
        if cnf.options.static_freeglut:
            # static linking freeglut
            cnf.env.STLIB_FREEGLUT      = [ 'freeglut_static' ]
            cnf.env.DEFINES_FREEGLUT    = [ 'FREEGLUT_STATIC' ]
        else:
            # dynamic linking freeglut
            cnf.env.STLIB_FREEGLUT      = [ 'freeglut' ]
            cnf.env.LIB_FREEGLUT        = [ 'freeglut', 'opengl32', 'glu32' ]

        cnf.env.STLIB_BOOST_REGEX   = [ 'boost_regex' + cnf.env.boost_suffix ]

        # platform-specific stuff
        global sources_platform;
        sources_platform            = [ 'src/platform/win32.cc' ]

        cnf.env.INCLUDES.append( cnf.env.BOOST_PATH )
        cnf.env.LINKFLAGS_MAIN      = [ '-static-libgcc', '-static-libstdc++', '-Wl,--subsystem,windows' ]
        cnf.env.LIB_MAIN            = [ 'opengl32', 'gdi32', 'winmm', 'comdlg32', 'glu32' ]
        cnf.env.STLIBPATH           = [ abspath + '/lib/gcc-mingw' ]
        cnf.env.STLIBPATH_SHAPELIB  = [ abspath + '/deps/shapelib/lib/gcc-mingw' ]
        cnf.env.LIBPATH             = [ abspath + '/lib/gcc-mingw' ]

        # for building the test runners
        cnf.env.DEFINES_TEST        = [ 'BOOST_TEST_DYN_LINK' ]
        cnf.env.LIB_TEST            = [ 'boost_unit_test_framework' + cnf.env.boost_suffix ]
        cnf.env.STLIB_TEST          = [ 'freeglut_static', 'boost_regex' + cnf.env.boost_suffix, 'shp' ]
        cnf.env.STLIBPATH_TEST      = cnf.env.STLIBPATH_MAIN

#------------------------------------------------------------------------------
def build( bld ):

    # determine the name of the final executable
    #-------------------------------------------
    version_file_created = call( 'python tools/describe.py ', shell=True )
    if version_file_created == 0:
        bld.env.EXE_NAME = Popen( 'python tools/exe_name.py' , stdout=PIPE, stderr=PIPE, shell=True ).stdout.read().strip()
    else:
        bld.env.EXE_NAME = "wf-viz"

    # build platform-independent objects
    #-----------------------------------
    bld.objects(
            source      = sources,
            target      = 'objects'
            )
    bld.objects(
            source      = utils_cc,
            target      = 'utils',
            use         = [ 'BOOST_REGEX', 'FREEGLUT' ]
            )

    # options to build geometry lib
    #-----------------------------------
    geometry_dict = dict( 
            source      = sources_geometry,
            target      = 'geometry',
            use         = [ 'objects', 'utils', 'FREEGLUT' ]
            )

    # options to build GUI lib
    #-----------------------------------
    gui_dict = dict(
            source      = sources_gui,
            target      = 'GUI',
            use         = [ 'objects', 'utils', 'SHAPELIB', 'FREEGLUT' ]
            )
    
    # static or dynamic local libs
    #-----------------------------------
    if bld.options.static_libs:
        bld.stlib( **geometry_dict )
        bld.stlib( **gui_dict )
    else:
        bld.shlib( **geometry_dict )
        bld.shlib( **gui_dict )


    # build platform-specific object, to be linked into the main program
    #-------------------------------------------------------------------
    bld.objects(
            source      = sources_platform,
            target      = 'platform',
            use         = 'PLATFORM' # on linux, GTKMM stuff; blank on Win
            )

    # build main program
    #-------------------------------------------------------------------
    bld.program(
            target      = bld.env.EXE_NAME,
            features    = [ 'cxxprogram' ],
            source      = main_cc,
            use         = [ 'objects', 'MAIN', 'geometry', 'GUI', 'platform','FREEGLUT' ]
            )

    if sys.platform == 'win32' or sys.platform == 'cygwin' and not bld.options.static_freeglut:
        copy( bld.env.FREEGLUT_DLL, out )

    # build test runner
    #---------------------------------------------------
    if( bld.options.check ):
        print 'building tests...'
        bld.program(
                target      = 'runner',
                features    = [ 'cxxprogram' ],
                source      = [ test_runner_cc ] + test_sources,
                use         = [ 'objects','linux-gtkmm', 'MAIN', 'TEST', 'GTKMM-3.0' ]
                )

        if sys.platform == 'win32' or sys.platform == 'cygwin':
            copy( bld.env.LIBPATH_TEST[0] + '/libboost_unit_test_framework-mgw47-mt-1_52.dll', out )

    if version_file_created == 0:
        copy( 'VERSION', out )
        call( 'python tools/append_date.py ' + out + '/VERSION', shell=True )

# vim:filetype=python
