#include "ArrayInterface.h"

#include <iostream>

typedef MemoryViewIterator<double> Iter;

void testMemoryView2D(MemoryView2D<double>* A) {
	ShowMessage("C++");
	ShowMessage(
			"Shape: " << A->shape(0) << ", " << A->shape(1) <<
			"; Strides: " << A->strides(0) << ", " << A->strides(1)
	);
	Iter it = A->begin();
	Iter it1 = A->begin();
	ShowMessage("A" << it << ": " << *it );
	++it;
	ShowMessage("A" << it << ": " << *it );
	++it;
	ShowMessage("A" << it << ": " << *it );
	it = it + 1;
	ShowMessage("A" << it << ": " << *it );
	it = it + 9;
	ShowMessage("A" << it << ": " << *it );
	it = it - 4;
	ShowMessage("A" << it << ": " << *it );
	it = it - 1;
	ShowMessage("A" << it << ": " << *it );
	it = it - 4;
	ShowMessage("A" << it << ": " << *it );

	ShowMessage("it - it1 " << it << ", " << it1 << " : " << (it - it1) );
	ShowMessage("it == it1 " << it << ", " << it1 << " : " << (it == it1) );
	ShowMessage("it != it1 " << it << ", " << it1 << " : " << (it != it1) );
	ShowMessage("it > it1 " << it << ", " << it1 << " : " << (it > it1) );
	ShowMessage("it < it1 " << it << ", " << it1 << " : " << (it < it1) );

	it1 = it1 + 4;
	ShowMessage("it - it1 " << it << ", " << it1 << " : " << (it - it1) );
	ShowMessage("it == it1 " << it << ", " << it1 << " : " << (it == it1) );
	ShowMessage("it != it1 " << it << ", " << it1 << " : " << (it != it1) );
	ShowMessage("it > it1 " << it << ", " << it1 << " : " << (it > it1) );
	ShowMessage("it < it1 " << it << ", " << it1 << " : " << (it < it1) );

	it1 = it1 + 7;
	ShowMessage("it - it1 " << it << ", " << it1 << " : " << (it - it1) );
	ShowMessage("it == it1 " << it << ", " << it1 << " : " << (it == it1) );
	ShowMessage("it != it1 " << it << ", " << it1 << " : " << (it != it1) );
	ShowMessage("it > it1 " << it << ", " << it1 << " : " << (it > it1) );
	ShowMessage("it < it1 " << it << ", " << it1 << " : " << (it < it1) );

	ShowMessage("Checking iterator substraction");
	ShowMessage("Begin - Begin: " << (A->begin() - A->begin()));
	ShowMessage("End - End: " << (A->end() - A->end()));
	ShowMessage("End - Begin: " << (A->end() - A->begin()));
	ShowMessage("Begin - End: " << (A->begin() - A->end()));


	ShowMessage("Iterating");
	for (Iter it2 = A->begin(); it2 != A->end(); ++it2) {
		ShowMessage("A" << it2 << ": " << *it2 );
	}
}
