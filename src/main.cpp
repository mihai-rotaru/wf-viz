#include <iostream>
#include <fstream>
#include <sstream>
#include <list>
#include <vector>
using namespace std;

#ifdef _MSC_VER
#include <windows.h>
#endif

#include <boost/shared_ptr.hpp>
#include <boost/foreach.hpp>
using boost::shared_ptr;

#include "globals.h"
#include "utils.h"
#include "Point.h"
#include "Line.h"
#include "BezierCurve.h"
#include "Shape.h"
#include "Group.h"
#include "Layer.h"
#include "window.h"
#include "label.h"
using namespace xmx;

#include <GL/glu.h>
#include <GL/glut.h>

vector < shared_ptr<Window> > windows;
shared_ptr< Label > label1;
shared_ptr< Window > focused_window;

string VERSION    = "?";
string BUILD_ID   = "?";
string BUILD_TIME = "?";
string build_info = "";

// holds the map of the world
Group world;

//------------------------------------------------------------------------------
void gl_init()
{
    glClearColor( 0.9, 0.9, 0.9, 0.0 );

    // initialize viewing values
    glMatrixMode( GL_PROJECTION );
    glLoadIdentity();
    gluOrtho2D( 0, GLUT_WINDOW_HEIGHT, 0, GLUT_WINDOW_WIDTH );
}

//------------------------------------------------------------------------------
void app_init()
{
    // read version number and build info
    ifstream ver_file( "VERSION", ifstream::in );
    getline( ver_file, VERSION );
    VERSION = "World Statistics, " + VERSION;
    getline( ver_file, BUILD_ID );
    getline( ver_file, BUILD_TIME );
    build_info = "Build info: " + BUILD_ID + " @ " + BUILD_TIME;

    // create a couple of windows
    shared_ptr< Window > window1 = shared_ptr< Window >( new Window( 100, 100, 300, 100, "Window #1" ) );
    shared_ptr< Window > window2 = shared_ptr< Window >( new Window( 200, 200, 200, 200, "Another Window" ) );
    label1 = shared_ptr< Label >( new Label( 200, 18, "This is a label" ) ); 
    window1->addControl( label1, 2, 20 );
    windows.push_back( window1 );
    windows.push_back( window2 );
    window1->giveFocus();
    focused_window = window1;
}

//------------------------------------------------------------------------------
void gl_display_callback()
{
    glClear( GL_COLOR_BUFFER_BIT );
    glRenderMode( GL_RENDER );

    BOOST_FOREACH( shared_ptr< Window > window, windows )
        window->draw();

    glColor3ub( 60, 60, 60 );
    printText( 10, glutGet( GLUT_WINDOW_HEIGHT ) - 18, VERSION );
    printText( 10, glutGet( GLUT_WINDOW_HEIGHT ) - 32, build_info );

    glutSwapBuffers();
}

//------------------------------------------------------------------------------
void gl_reshape_callback( int nWidht, int nHeight )
{
    window_width = nWidht;
    window_height = nHeight;
    glViewport( 0, 0, (GLsizei)nWidht, (GLsizei)nHeight );
    glMatrixMode( GL_PROJECTION );
    glLoadIdentity();
    gluOrtho2D( 0, nWidht, 0, nHeight);
    glutPostRedisplay();
}

//------------------------------------------------------------------------------
void gl_mouse_callback( int button, int state, int x, int y )
{
    label1->setText( "click: x = " + to_string( x ) + ", y = " + to_string( y )); 

    BOOST_FOREACH( shared_ptr< Window > window, windows )
    {
        if(     x >= window->getX() && x <= window->getX() + window->getWidth()
             && y >= window->getY() && y <= window->getY() + window->getHeight())
        {
            focused_window->losfFocus();
            window->giveFocus();
            focused_window = window;
        }
    }
}

//------------------------------------------------------------------------------
void gl_keyboard_callback( unsigned char key, int x, int y )
{
    switch( key )
    {
        case 27:
            exit(0);
            break;
    }
}

//------------------------------------------------------------------------------
int main( int argc, char *argv[] )
{
    glutInit( &argc, argv );
    glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB | GLUT_MULTISAMPLE );
     
    // window
    window_width = 800;
    window_height = 600;
    glutInitWindowSize( window_width, window_height );
    glutInitWindowPosition( 100, 100 );
    glutCreateWindow( "World Factbook" );

    gl_init();  // OpenGL-specific initializations
    app_init(); // application-specific initializations

    // callbacks
    glutDisplayFunc( gl_display_callback );
    glutKeyboardFunc( gl_keyboard_callback );
    glutReshapeFunc( gl_reshape_callback );
    glutMouseFunc( gl_mouse_callback );

    glutMainLoop();
    
    return 0;
}
