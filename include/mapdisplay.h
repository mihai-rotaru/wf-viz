#ifndef MAPDISPLAY_H
#define MAPDISPLAY_H

#include "gui_utils.h"
#include "control.h"

namespace xmx {

class MapDisplay: public Control
{
public:
    MapDisplay( int width_, int height_, std::string text_ ):
        Control( 0, 0, width_, height_, "mapdisplay", true ),
        shapefile( "" ), file_loaded( false )
        {   setTextColor( &BLACK );
            setBackgroundColor( &GAINSBORO );
            setBorderColor( &LIGHT_GREY );
            setBorderWidth( 1 );
        }
    void draw();
    void clickEvent( int x_, int y_, int button, int state ) {};

    void loadFromShapefile( std::string );

protected:
    std::string shapefile;
    bool file_loaded;
};

} // namespace xmx
#endif /* MAPDISPLAY_H */
