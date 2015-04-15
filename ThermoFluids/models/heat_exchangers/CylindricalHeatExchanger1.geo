Point(1) = { 0, 0, 0, 0.1 };
Point(2) = { -1, 0, 0, 0.1 };
Point(3) = { 0, 1, 0, 0.1 };
Point(4) = { 1, 0, 0, 0.1 };
Point(5) = { 0, -1, 0, 0.1 };
Circle(1) = { 2, 1, 3 };
Circle(2) = { 3, 1, 4 };
Circle(3) = { 4, 1, 5 };
Circle(4) = { 5, 1, 2 };
Line Loop(1) = {1, 2, 3, 4};
Physical Line("OuterBoundary") = { 1, 2, 3, 4 };
Point(6) = { 0, 0, 0, 0.05 };
Point(7) = { -0.125, 0, 0, 0.05 };
Point(8) = { 0, 0.125, 0, 0.05 };
Point(9) = { 0.125, 0, 0, 0.05 };
Point(10) = { 0, -0.125, 0, 0.05 };
Translate { 0.5, 0, 0 } { Point{ 6, 7, 8, 9, 10 }; }
Rotate { {0, 0, 1}, {0, 0, 0}, 2.0 } { Point{ 6, 7, 8, 9, 10 }; }
Circle(5) = { 7, 6, 8 };
Circle(6) = { 8, 6, 9 };
Circle(7) = { 9, 6, 10 };
Circle(8) = { 10, 6, 7 };
Line Loop(2) = {5, 6, 7, 8};
Physical Line("PrimaryChannel") = { 5, 6, 7, 8 };
Point(11) = { 0, 0, 0, 0.05 };
Point(12) = { -0.125, 0, 0, 0.05 };
Point(13) = { 0, 0.125, 0, 0.05 };
Point(14) = { 0.125, 0, 0, 0.05 };
Point(15) = { 0, -0.125, 0, 0.05 };
Translate { 0.5, 0, 0 } { Point{ 11, 12, 13, 14, 15 }; }
Circle(9) = { 12, 11, 13 };
Circle(10) = { 13, 11, 14 };
Circle(11) = { 14, 11, 15 };
Circle(12) = { 15, 11, 12 };
Line Loop(3) = {9, 10, 11, 12};
Physical Line("SecondaryChannel") = { 9, 10, 11, 12 };
Plane Surface(1) = { 1, 2, 3 };
Physical Surface("CrossSection") = { 1 };
