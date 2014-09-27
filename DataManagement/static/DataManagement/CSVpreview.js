angular.module('csvImportApp', ['angularFileUpload', 'ui.bootstrap'])
	.config(['$httpProvider', function($httpProvider) {
	    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
	    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	}])
	.controller('CsvImportController', 
			[ '$scope', '$upload', '$window', '$http', 
		function($scope, $upload, $window, $http) {
			$scope.numRowsInPreview = 10;
			$scope.showPreviewTable = false;
			$scope.fileSelect = function($files){
				$scope.uploadFile = $files;	
			}
			
			// Define the column properties structure
			ColumnProps = function (name, dataType, use) {
				this.name = name;
				this.dataType = dataType;
				this.use = use;
			}
			$scope.columnTypeChoices = ['float', 'integer', 'string'];
			
			$scope.sendFile = function() { //$file: a file selected, having name, size, and type.
				var file = $scope.uploadFile;		      
				$scope.upload = $upload.upload({
					url: '/DataManagement/ImportCSV/',//'server/upload/url', upload.php script, node.js route, or servlet url
					method: 'POST',
					data: {numRowsInPreview: $scope.numRowsInPreview},
					file: file, // or list of files ($files) for html5 only
				}).progress(function(evt) {
					$scope.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
					//console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
				}).success(function(csvPreviewData, status, headers, config) {
					$scope.columnProps = [];
					$scope.csvPreviewData = csvPreviewData;
					for (var i = 0; i < csvPreviewData.numColumns; i++) {
						$scope.columnProps.push(new ColumnProps("C" + (i + 1), 'float', true));
					}
					$scope.firstDataRow = 1;
					$scope.showPreviewTable = true;
				});
			}

			$scope.onRowHeaderClick = function(row) {
				$scope.firstDataRow = row;
			}

			$scope.onRowHeaderDblClick = function(row) {
				for (var i = 0; i < $scope.columnProps.length; i++) {
					$scope.columnProps[i].name = $scope.csvPreviewData.tableValues[row - 1][i];
				}
			}

			$scope.cellStyle = function(row, col) {
				var style = {};
				if (row >= $scope.firstDataRow)
					style['background-color'] = '#CCCCFF';
				else
					style['background-color'] = 'white';
				if ($scope.columnProps[col - 1].use) {
					style['color'] = 'black';
				} else {
					style['color'] = '#AAAAAA';
				}
				return style;
			}
          		
			$scope.importHdf = function() {
				alert(angular.toJson($scope.columnProps));
				$http.post('/DataManagement/CSVtoHDF/', {
					columnProps : $scope.columnProps,
					firstDataRow : $scope.firstDataRow,
					importerId : $scope.csvPreviewData.importerId
				})
				.success(function(data){
					$scope.statusMessage = "File successfully imported!";
				})
				.error(function(data){
					$scope.statusMessage = "Error, could not import file!";
				});
   		  }
}]);		