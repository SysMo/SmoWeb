var csvImportApp = angular.module('csvImportApp', ['angularFileUpload', 'ui.bootstrap']);
	
	csvImportApp.config(['$httpProvider', function($httpProvider) {
	    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
	    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	}]);

	csvImportApp.controller('CsvImportController', [ '$scope', '$upload', '$window', '$http', 
	                                                  function($scope, $upload, $window, $http) {
		
		$scope.rowsInDisplay = 10;
		$scope.hidden = true;
		
		$scope.fileSelect = function($files){
			console.log($files);
			$scope.uploadFile = $files;	
			}
		
		$scope.fileSend= function() { //$file: a file selected, having name, size, and type.
		      var file = $scope.uploadFile;		      
		      $scope.upload = $upload.upload({
		        url: '/DataManagement/ImportCSV/',//'server/upload/url', upload.php script, node.js route, or servlet url
		        method: 'POST',
		        data: {rowsInDisplay: $scope.rowsInDisplay},
		        file: file, // or list of files ($files) for html5 only
		      }).progress(function(evt) {
		        console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
		      }).success(function(data, status, headers, config) {
			    	csvPreviewData = data;
			    	$scope.hidden = false;
			    	$scope.numColumns = csvPreviewData.numColumns;
			    	$scope.tableValues = csvPreviewData.tableValues;
			    	$scope.headerRow = 1;						
		       		$scope.columnPossibleTypes = ['float', 'integer', 'string'];      		
		       		$scope.columnNames = new Array($scope.numColumns);
		       		$scope.useColumn = new Array($scope.numColumns);
		       		$scope.columnTypes = new Array($scope.numColumns);
		       		for (var i = 0; i < $scope.numColumns; i++) {
		       			$scope.columnNames[i] = "C" + (i + 1);
		       			$scope.useColumn[i] = true;
		       			$scope.columnTypes[i] = "float";
		       		}
		       		$scope.firstDataRow = 1;
		      });
		    }
			
       		$scope.onRowHeaderClick = function(row) {
       			$scope.firstDataRow = row;
       		}
       		$scope.onRowHeaderDblClick = function(row) {
       			$scope.headerRow = row;
       			for (var i = 0; i < $scope.numColumns; i++) {
       				$scope.columnNames[i] = $scope.tableValues[row - 1][i];
       			}
       		}
       		$scope.cellStyle = function(row, col) {
       			var style = {};
       			if (row >= $scope.firstDataRow)
       				style['background-color'] = '#CCCCFF';
       			else
       				style['background-color'] = 'white';
       			if ($scope.useColumn[col - 1]) {
       				style['color'] = 'black';
       			} else {
       				style['color'] = '#AAAAAA';
       			}
       			return style;
       		}
			          		
       		$scope.send = function() {
       			//alert("Column names: " + $scope.columnNames + "\n" + "First data row: " + $scope.firstDataRow);
//       			console.log(csvPreviewData);
       			var postData = {
       				columnNames : $scope.columnNames,
       				useColumn : $scope.useColumn,
       				columnTypes : $scope.columnTypes,
       				firstDataRow : $scope.firstDataRow,
       				headerRow: $scope.headerRow
       			};
//       			alert(util.dumpObject(postData, "    "));
       				alert(angular.toJson(postData, true));
       			$http.post('/DataManagement/CSVtoHDF/', postData).success(function(data){
       				$window.location.href = "/";
       			});
       		  }
	}]);		
		
//		csvPreviewApp.config(function($provide) {
//			  $provide.value('DumpObjectIndentedService', function(obj, indent){
//		  		  var result = "";
//				  if (indent == null) indent = "";
//				  for (var property in obj)
//				  {
//				    var value = obj[property];
//				    if (typeof value == 'string')
//				      value = "'" + value + "'";
//				    else if (typeof value == 'object')
//				    {
//				      if (value instanceof Array)
//				      {
//				        // Just let JS convert the Array to a string!
//				        value = "[ " + value + " ]";
//				      }
//				      else
//				      {
//				        // Recursive dump
//				        // (replace "  " by "\t" or something else if you prefer)
//				        var od = DumpObjectIndented(value, indent + "  ");
//				        // If you like { on the same line as the key
//				        //value = "{\n" + od + "\n" + indent + "}";
//				        // If you prefer { and } to be aligned
//				        value = "\n" + indent + "{\n" + od + "\n" + indent + "}";
//				      }
//				    }
//				    result += indent + "'" + property + "' : " + value + ",\n";
//				  }
//				  return result.replace(/,\n$/, "");});
//			});
		
