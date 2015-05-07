/*
 * ArrayInterface.h
 *
 *  Created on: Apr 25, 2015
 *      Author: Atanas Pavlov
 *      Copyright: SysMo Ltd., Bulgaria
 */

#ifndef ARRAYINTERFACE_H_
#define ARRAYINTERFACE_H_

#include "core/Definitions.h"
#include <vector>
#include <iterator>
#include <stdlib.h>
#include <iostream>

#define MEMORY_VIEW_MAX_NDIMS 8

/****************************
 * MemoryViewIterator
 *****************************/

template <class T> class MemoryViewIterator;
template<class T> std::ostream& operator<<(std::ostream& out, const MemoryViewIterator<T>& iter);

template <class T> class MemoryViewBase;
template <class T>
class MemoryViewIterator : public std::iterator<std::random_access_iterator_tag, T> {
public:
	MemoryViewIterator(MemoryViewBase<T>* view, ssize_t* indices, bool isEnd = false);
	MemoryViewIterator(const MemoryViewIterator<T>& other);
	T& operator*();
	bool operator==(const MemoryViewIterator& other) const;
	bool operator!=(const MemoryViewIterator& other) const{
		return !(*this == other);
	}
	MemoryViewIterator& operator++();
	MemoryViewIterator& operator--();
	MemoryViewIterator operator+(ssize_t diff) const;
	MemoryViewIterator operator-(ssize_t diff) const;
	ssize_t operator-(const MemoryViewIterator& other) const;
	bool operator<(const MemoryViewIterator& other) const;
	bool operator>(const MemoryViewIterator& other) const;
	friend std::ostream& operator<< <T>(std::ostream& out, const MemoryViewIterator<T>& iter);
protected:
	MemoryViewBase<T>* view;
	ssize_t indices[MEMORY_VIEW_MAX_NDIMS];
	bool isEnd;
};

/**
 * MemoryView iterator
 */

template <class T>
MemoryViewIterator<T>::MemoryViewIterator(MemoryViewBase<T>* view, ssize_t* indices, bool isEnd)
: view(view), isEnd(isEnd) {
	if (!isEnd) {
		for (int i = 0; i < view->ndim(); i++) {
			this->indices[i] = indices[i];
		}
	} else {
		for (int i = 0; i < view->ndim(); i++) {
			this->indices[i] = 0;
		}
	}
}

template <class T>
MemoryViewIterator<T>::MemoryViewIterator(const MemoryViewIterator<T>& other)
: view(other.view), isEnd(other.isEnd){
	for (int i = 0; i < view->ndim(); i++) {
		this->indices[i] = other.indices[i];
	}}

template <class T>
T& MemoryViewIterator<T>::operator*() {
	return *view->getItemPointer(indices);
}

template <class T>
bool MemoryViewIterator<T>::operator==(const MemoryViewIterator<T>& other) const {
	if (this->view != other.view) {
		return false;
	}
	if (this->isEnd || other.isEnd) {
		return (this->isEnd == other.isEnd);
	}
	for (int i = 0; i < view->ndim(); i++) {
		if (this->indices[i] != other.indices[i]) {
			return false;
		}
	}
	return true;
}

template <class T>
MemoryViewIterator<T>& MemoryViewIterator<T>::operator++() {
	int i = view->ndim() - 1;
	bool dimensionOverflow = true;
	while (dimensionOverflow && !isEnd) {
		dimensionOverflow = false;
		// Increment the index
		this->indices[i] += 1;
		// If the index is more than it can be, then we wrap
		// and increase next dimension
		if (this->indices[i] >= view->_shape[i]) {
			this->indices[i] = 0;
			dimensionOverflow = true;
		}
		// If even dimension 0 overflows, we have reached the end
		if (i == 0 && dimensionOverflow) {
			isEnd = true;
		} else {
			--i;
		}
	}
	return (*this);
}

template <class T>
MemoryViewIterator<T>& MemoryViewIterator<T>::operator--() {
	if (isEnd) {
		for (int i = 0; i < view->ndim(); i++) {
			indices[i] = view->_shape[i] - 1;
		}
		isEnd = false;
	} else {
		int i = view->ndim() - 1;
		bool dimensionUnderflow = true;
		while (dimensionUnderflow) {
			dimensionUnderflow = false;
			// Decrement the index
			this->indices[i] -= 1;
			// If the index is less than 0, then we wrap
			// and decrease next dimension
			if (this->indices[i] < 0) {
				this->indices[i] = view->_shape[i] - 1;
				dimensionUnderflow = true;
			}
			// If even dimension 0 overflows, we have reached the end
			if (i == 0 && dimensionUnderflow) {
				RaiseError("Operator-- attempted to go beyond the begin of a MemoryView")
			} else {
				--i;
			}
		}
	}
	return (*this);
}

template <class T>
MemoryViewIterator<T> MemoryViewIterator<T>::operator+(ssize_t diff) const {
	if (diff < 0) {
		return this->operator-(-diff);
	}
	MemoryViewIterator<T> result(*this);
	if (diff == 0) {
		return result;
	}
	ssize_t i = 0;
	div_t divresult;
	while (diff > 0) {
		if (view->_indexStrides[i] <= diff) {
			divresult = div(diff, view->_indexStrides[i]);
			result.indices[i] += divresult.quot;
			if (result.indices[i] >= view->_shape[i]) {
				ssize_t extraSteps = result.indices[i] - view->_shape[i];
				result.indices[i] = view->_shape[i] - 1;
				++result;
				result.indices[i] += extraSteps;
			}
			if (result.indices[i] >= view->_shape[i]) {
				RaiseError("MemoryViewIterator::operator+: went beyond the end of the array!")
			}
			diff = divresult.rem;
		}
		++i;
	}
	return result;
}

template <class T>
MemoryViewIterator<T> MemoryViewIterator<T>::operator-(ssize_t diff) const {
	if (diff < 0) {
		return this->operator-(-diff);
	}
	MemoryViewIterator<T> result(*this);
	if (diff == 0) {
		return result;
	}
	if (result.isEnd) {
		--result;
		--diff;
	}
	ssize_t i = 0;
	div_t divresult;
	while (diff > 0) {
		if (view->_indexStrides[i] <= diff) {
			divresult = div(diff, view->_indexStrides[i]);
			result.indices[i] -= divresult.quot;
			if (result.indices[i] < 0) {
				ssize_t extraSteps = -result.indices[i] - 1;
				result.indices[i] = 0;
				--result;
				result.indices[i] -= extraSteps;
			}
			if (result.indices[i] < 0) {
				RaiseError("MemoryViewIterator::operator-: went beyond the beginning of the array!")
			}
			diff = divresult.rem;
		}
		++i;
	}
	return result;
}

template <class T>
ssize_t MemoryViewIterator<T>::operator-(const MemoryViewIterator<T>& other) const {
	ssize_t diff = 0;
	if (this->isEnd && other.isEnd) {
		diff = 0;
	} else if (this->isEnd) {
		MemoryViewIterator<T> tmp(*this);
		--tmp;
		diff = tmp - other + 1;
	} else if (other.isEnd) {
		MemoryViewIterator<T> tmp(other);
		--tmp;
		diff = (*this) - tmp - 1;
	} else {
		for (int i = 0; i < view->ndim(); i++) {
			diff += (indices[i] - other.indices[i]) * view->_indexStrides[i];
		}
	}
	return diff;
}

template <class T>
bool MemoryViewIterator<T>::operator<(const MemoryViewIterator<T>& other) const {
	for (int i = 0; i < view->ndim(); i++) {
		if (indices[i] < other.indices[i]) {
			return true;
		} else if (indices[i] > other.indices[i]) {
			return false;
		}
	}
	return false;
}

template <class T>
bool MemoryViewIterator<T>::operator>(const MemoryViewIterator<T>& other) const {
	for (int i = 0; i < view->ndim(); i++) {
		if (indices[i] > other.indices[i]) {
			return true;
		} else if (indices[i] < other.indices[i]) {
			return false;
		}
	}
	return false;
}

template <class T>
std::ostream& operator<< (std::ostream& out, const MemoryViewIterator<T>& iter) {
	out << "(";
	for (int i = 0; i < iter.view->ndim(); i++) {
		out << iter.indices[i];
		if (i !=  iter.view->ndim() - 1) {
			out << ", ";
		}
	}
	out << ")";
	return out;
}

/**
 * MemoryViewBase
 */

template <class T>
class MemoryViewBase {
public:
	//typedef MemoryViewIterator<T> Iterator;
	friend class MemoryViewIterator<T>;
protected:
	T* buf;
	ssize_t _len;
	int readonly;
	const char *format;
	int _ndim;
	std::vector<ssize_t> _shape;
	std::vector<ssize_t> _strides;
	std::vector<ssize_t> _indexStrides;
	ssize_t itemsize;
protected:
	void computeLen();
	inline T* getItemPointer(ssize_t* indices) {
		char *pointer = (char*) buf;
		for (int i = 0; i <  _ndim; i++) {
			if (indices[i] < 0 || indices[i] >= this->_shape[i]) {
				RaiseError("MemoryView: index " << i << " (" << indices[i] << ") out of bounds [0, " << this->_shape[i] - 1 << "]\n");
			}
			pointer += _strides[i] * indices[i];
		}
		return (T*) pointer;
	}
public:
	MemoryViewBase(T* buf, int ndim);
	MemoryViewBase(T* buf, int ndim, ssize_t* shape, ssize_t* strides);
	virtual ~MemoryViewBase(){};
	inline T* data() {
		return this->buf;
	}
	inline ssize_t len() {
		return _len;
	}
	inline int ndim() {
		return _ndim;
	}
	inline int shape(int iDim) {
		if (iDim < this->_ndim) {
			return _shape[iDim];
		} else {
			RaiseError("Index to MemoryView::shape " << iDim << " out of range 1 - " << iDim - 1)
		}
	}
	inline int strides(int iDim) {
		if (iDim < this->_ndim) {
			return _strides[iDim];
		} else {
			RaiseError("Index to MemoryView::shape " << iDim << " out of range 1 - " << iDim - 1)
		}
	}
	MemoryViewIterator<T> begin();
	MemoryViewIterator<T> end();
	void copyTo(T* destination);
	void copyFrom(T* source);
};

template <class T>
MemoryViewBase<T>::MemoryViewBase(T* buf, int ndim)
: buf(buf), _ndim(ndim), _shape(ndim), _strides(ndim), _indexStrides(ndim) {
	itemsize = sizeof(T);
	readonly = 0;
}

template <class T>
MemoryViewBase<T>::MemoryViewBase(T* buf, int ndim, ssize_t* shape, ssize_t* strides)
: buf(buf), _ndim(ndim), _shape(shape, shape + ndim), _strides(strides, strides + ndim),  _indexStrides(ndim) {
	itemsize = sizeof(T);
	readonly = 0;
	computeLen();
}

template <class T>
void MemoryViewBase<T>::computeLen() {
	_len = _shape[_ndim - 1];
	_indexStrides[_ndim - 1] = 1;
	for (int i = _ndim - 2; i >= 0; i--) {
		_len *= _shape[i];
		_indexStrides[i] = _indexStrides[i + 1] * _shape[i + 1];
	}
}

//Iterator begin();
template <class T>
MemoryViewIterator<T> MemoryViewBase<T>::begin() {
	ssize_t ind[MEMORY_VIEW_MAX_NDIMS];
	for (int i = 0; i < _ndim; i++) {
		ind[i] = 0;
	}
	return MemoryViewIterator<T>(this, ind);
}

template <class T>
MemoryViewIterator<T> MemoryViewBase<T>::end() {
	ssize_t ind[MEMORY_VIEW_MAX_NDIMS];
	return MemoryViewIterator<T>(this, ind, true);
}

template <class T>
void MemoryViewBase<T>::copyTo(T* destination) {
	MemoryViewIterator<T> it = this->begin();
	for (int i = 0; i < len(); i++) {
		destination[i] = *it;
		++it;
	}
}

template <class T>
void MemoryViewBase<T>::copyFrom(T* source) {
	MemoryViewIterator<T> it = this->begin();
	for (int i = 0; i < len(); i++) {
		*it = source[i];
		++it;
	}
}



/**
 * MemoryView1D
 */

template <class T>
class MemoryView1D : public MemoryViewBase<T> {
public:
	MemoryView1D(T* data, ssize_t dim1, ssize_t stride1);
	MemoryView1D(T* data, ssize_t* shape, ssize_t* strides);
	inline T& operator()(ssize_t n) {
		return *this->getItemPointer(&n);
	}
//	inline T& operator[](ssize_t n) {
//		return (T&)*((char*)(this->buf) + this->_strides[0] * n);
//	}
};

template <class T>
MemoryView1D<T>::MemoryView1D(T* data, ssize_t dim1, ssize_t stride1)
: MemoryViewBase<T>(data, 1) {
	this->_shape[0] = dim1;
	this->_strides[0] = stride1;
	this->computeLen();
}

template <class T>
MemoryView1D<T>::MemoryView1D(T* data, ssize_t* shape, ssize_t* strides)
: MemoryViewBase<T>(data, 1, shape, strides) {}

/*
 * MemoryView2D
 */

template <class T>
class MemoryView2D : public MemoryViewBase<T> {
public:
	MemoryView2D(T* data, ssize_t dim1, ssize_t dim2, ssize_t stride1, ssize_t stride2);
	inline T& operator()(ssize_t n1, ssize_t n2) {
		ssize_t ind[2] = {n1, n2};
		return *this->getItemPointer(ind);
	}
};

template <class T>
MemoryView2D<T>::MemoryView2D(T* data,  ssize_t dim1, ssize_t dim2, ssize_t stride1, ssize_t stride2)
: MemoryViewBase<T>(data, 2) {
	this->_shape[0] = dim1;
	this->_shape[1] = dim2;
	this->_strides[0] = stride1;
	this->_strides[1] = stride2;
	this->computeLen();
}

/*
 * MemoryView3D
 */

template <class T>
class MemoryView3D : public MemoryViewBase<T> {
public:
	MemoryView3D(T* data, ssize_t dim1, ssize_t dim2, ssize_t dim3, ssize_t stride1, ssize_t stride2, ssize_t stride3);
	inline T& operator()(ssize_t n1, ssize_t n2, ssize_t n3) {
		ssize_t ind[3] = {n1, n2, n3};
		return *this->getItemPointer(ind);
	}
};

template <class T>
MemoryView3D<T>::MemoryView3D(T* data, ssize_t dim1, ssize_t dim2, ssize_t dim3, ssize_t stride1, ssize_t stride2, ssize_t stride3)
: MemoryViewBase<T>(data, 3) {
	this->_shape[0] = dim1;
	this->_shape[1] = dim2;
	this->_shape[2] = dim3;
	this->_strides[0] = stride1;
	this->_strides[1] = stride2;
	this->_strides[2] = stride3;
	this->computeLen();
}

/**
 * Tests
 */

void testMemoryView2D(MemoryView2D<double>* view);

#endif /* ARRAYINTERFACE_H_ */
