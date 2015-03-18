=======================
Internet Explorer fixes
=======================

Google Visualization Tables
===========================

Table pagination is not working with Internet Explorer 8, 
leads to "Invalid argument" error (and possibly also other versions as well). The issue
may be fixed in the new release of GViz 
(https://code.google.com/p/google-visualization-api-issues/issues/detail?id=1909).

Thus, in the ``smoDataSeriesView`` directive, in the :func:`drawTable` function, a check if the browser is IE is performed through
the global variable ``isIE``::
   
  var drawOptions;
  //GViz fix for IE, relying on global variable isIE. Pagination of tables in IE leads to "Invalid argument" error 
  if (isIE == true)
     drawOptions = {showRowNumber: true, sort:'disable'}
  else
     drawOptions = {showRowNumber: true, sort:'disable', page:'enable', pageSize:14}
  
  tableView.draw($scope.dataView, drawOptions);

