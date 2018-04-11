#include "opencv2/imgproc.hpp"
#include "opencv2/highgui.hpp"

import cv2{

Mat src = Mat::zeros( 400, 400, CV_8UC3);

Rect r(100,100,50,50);

Point point0 = Point(r.x, r.y);
Point point1 = Point(r.x + r.width, r.y);
Point point2 = Point(r.x + r.width, r.y + r.height);
Point point3 = Point(r.x, r.y + r.height);

rectangle( src, r, Scalar::all(255));

circle( src, point0, 10, Scalar( 0, 0, 255) );
circle( src, point1, 10, Scalar( 0, 0, 255) );
circle( src, point2, 10, Scalar( 0, 0, 255) );
circle( src, point3, 10, Scalar( 0, 0, 255) );

imshow( "coodinates of all corner of rectangle", src );
waitKey();

return 0;
}