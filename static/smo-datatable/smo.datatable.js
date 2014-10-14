(function ( angular ) {
	'use strict';

	angular.module('smoDataTableModule', ['ui.bootstrap'])
	.directive('smoDataTable', ['$compile', function ($compile) {
		return {
	        restrict: 'E',
	        link: function(scope, element, attrs) {
		        scope.columnTable = {columns:[], data:[]}
	        	var template = "";
		        var columnTable = attrs.tableModel;
		        
		        scope.formatTypeChoices = ["standard", "fixed", "exponential"];
	    		scope.fixedFormatChoices = [".0f", ".1f", ".2f", ".3f", ".4f", ".5f",
	    		                           ".6f", ".7f", ".8f"];
	    		scope.expFormatChoices = [".0e", ".1e", ".2e", ".3e", ".4e", ".5e",
	    		                           ".6e", ".7e", ".8e"];
		        			    				    			
	    		scope.initTable = function(){
		    		scope.toggled = false;
		    		scope.toggleText = "Show selected";
		    		scope.toAll = false;
		    		scope.checkAlltext = "Uncheck all";
		    		
		    		for (var i = 0; i < scope[columnTable].columns.length; i++){
		    			if (i == 0) {
		    				var leftmostColumn = {name: '#', show:true, isleftmostColumn: true};
		    				scope[columnTable].columns.unshift(leftmostColumn);
		    			} else {
		    				scope[columnTable].columns[i].numFormatType = 'standard';
			    			scope[columnTable].columns[i].numFormatPattern = '';
			    			scope[columnTable].columns[i].defaultFixedPattern = true;
			    			scope[columnTable].columns[i].defaultExpPattern = true;
			    			scope[columnTable].columns[i].isModelColumn = false;
			    			scope[columnTable].columns[i].isleftmostColumn = false;
			    			scope[columnTable].columns[i].show = true;
		    			}
		    			
		    		}	
		    		
		    		for (var i = 0; i < scope[columnTable].data.length; i++){
		    			scope[columnTable].data[i].unshift(i+1);
		    		}	
		    		
		    		scope.modelColumn = {},
		    		scope.modelColumn.numFormatType = 'standard';
		    		scope.modelColumn.numFormatPattern = '';
		    		scope.modelColumn.defaultFixedPattern = true;
		    		scope.modelColumn.defaultExpPattern = true;
		    		scope.modelColumn.isModelColumn = true;
		    		scope.modelColumn.show = true;
		    		
		    		scope.fileName = "data.csv";
	    			
	    		}
	    		
	    		scope.initTable();
	    		
	    		scope.isNumFormatStandard = function(column) {
	    			if (column.numFormatType == "standard"){
	    				return true;
	    			} else {
	    				return false;
	    			}
	    		}
	    		
	    		scope.isNumFormatFixed = function(column) {
	    			if (column.numFormatType == "fixed"){
	    				return true;
	    			} else {
	    				return false;
	    			}
	    		};
	    		
	    		scope.setDefaultPattern = function(column){
	    			if (column.numFormatType == 'fixed' && column.defaultFixedPattern){
	    				column.numFormatPattern = '.0f';
	    				column.defaultFixedPattern = false;
	    				column.defaultExpPattern = true;
	    			} else if (column.numFormatType == 'exponential' && column.defaultExpPattern) {
	    				column.numFormatPattern = '.0e';
	    				column.defaultExpPattern = false;
	    				column.defaultFixedPattern = true;
	    			} else {
	    				column.defaultFixedPattern = true;
	    				column.defaultExpPattern = true;
	    			}			
	    						
	    			if (column.isModelColumn){
	    				scope.toAll = true;
	    			}
	    			if (!column.isModelColumn){
	    				scope.setDefaultPatternToModelColumn(column);
	    			}
	    		}
	    		
	    		scope.setDefaultPatternToModelColumn = function(column){
	    			if (!column.isModelColumn){
	    				scope.toAll = false;
	    				scope.modelColumn.numFormatType = 'standard';
	    				scope.setDefaultPattern(scope.modelColumn);
	    			}
	    		}
	    		
	    		scope.checkAll = function(){
	    			scope.modelColumn.show = !scope.modelColumn.show;
	    			if (scope.modelColumn.show){
	    				for (var i = 0; i < scope[columnTable].columns.length; i++){
	    					scope[columnTable].columns[i].show = true;
	    				}
	    				scope.checkAlltext = "Uncheck all";
	    			} else {
	    				for (var i = 0; i < scope[columnTable].columns.length; i++){
	    					scope[columnTable].columns[i].show = false;
	    				}
	    				scope.checkAlltext = "Check all";
	    			}				
	    		}
	    		
	    		scope.SetToAll = function(modelColumn){
	    			for (var i = 1; i < scope[columnTable].columns.length; i++){
	    				scope[columnTable].columns[i].numFormatType = modelColumn.numFormatType;
	    				scope[columnTable].columns[i].numFormatPattern = modelColumn.numFormatPattern;
	    				scope[columnTable].columns[i].defaultFixedPattern = true;
	    				scope[columnTable].columns[i].defaultExpPattern = true;
	    			}	
	    		}
	    		
	    		scope.toggleTable = function(){						
	    			scope.toggled = !scope.toggled;
	    			if (scope.toggleText == "Show selected"){
	    				scope.toggleText = "Show all";
	    			}
	    			else{
	    				scope.toggleText = "Show selected"
	    			}
	    			
	    			if (scope.toggled == true){
	    				for (var i = 1; i < scope[columnTable].columns.length; i++){
	    					scope[columnTable].columns[i].numDecimalPoints = scope[columnTable].columns[i].numFormatPattern[1];					
	    				}
	    				scope.showInputField = false;
	    			}			
	    		}
	    		
	    		scope.display = function(row){
	    			var displayRow = [];
	    			displayRow.push(row[0]);
	    			for (var i = 1; i < row.length; i++){
	    				if (scope[columnTable].columns[i].numFormatType =='standard'){
	    					displayRow.push(row[i]);
	    				} else if (scope[columnTable].columns[i].numFormatType =='fixed'){
	    					displayRow.push(row[i].toFixed(scope[columnTable].columns[i].numDecimalPoints));
	    				} else {
	    					displayRow.push(row[i].toExponential(scope[columnTable].columns[i].numDecimalPoints));
	    				}
	    			}
	    			return displayRow;
	    		};
	    		
	    		scope.enterCSVfileName = function(){
	    			scope.showInputField = true;
	    		}
	    		
	    		scope.exportCSV = function (fileName){
	    			// prepare CSV data
	    			var columns = scope[columnTable].columns;
	    			var data = scope[columnTable].data;
	    			var csvContent  = "";
	    			var columnsArray = new Array();
	    			var columnNamesString;
	    			var dataString;
	    			
	    			columns.forEach(function(column, index, array){
	    				if (column.isleftmostColumn){
	    					return;
	    				}
	    				if (!column.show){
	    					return;
	    				}
	    				columnsArray.push('"' + column.name + '"');		
	    			});
	    			columnNamesString = columnsArray.join(",");
	    			csvContent += columnNamesString + "\n"; 
	    			data.forEach(function(item, index, dataArray){
	    				var resultItem = new Array();
	    				for (var i=1; i < item.length; i++){
	    					if (columns[i].show){
	    						resultItem.push(item[i]);
	    					}
	    				}
	    				
	    			   dataString = resultItem.join(",");
	    			   csvContent += dataString+ "\n";
	    			}); 

	    			// download stuff
	    		 	var blob = new Blob([csvContent], {
	    		 	  "type": "text/csv;charset=utf8;"			
	    		 	});
	    		 	var link = document.createElement("a");
	    						
	    		 	if(link.download !== undefined) { // feature detection
	    		 	  // Browsers that support HTML5 download attribute
	    		 	  link.setAttribute("href", window.URL.createObjectURL(blob));
	    		 	  link.setAttribute("download", fileName);
	    		 	 } else {
	    		 		// it needs to implement server side export
	    				//link.setAttribute("href", "http://www.example.com/export");
	    		 		  alert("Needs to implement server side export");
	    		 		  return;
	    		 	}
	    		 	document.body.appendChild(link);
	    		 	link.click();
	    		 	scope.showInputField = false;
	    		};	
		         
	    		var	innerTemplate =
    				'<div class="scrollable-container">' +
    					'<table class = "my-table">' +						
    						'<tr ng-if="!toggled">' +
    							'<th ng-repeat="column in ' + columnTable + '.columns track by $index">' +
    								'<span ng-bind="column.name"></span>' +
    								'<input ng-if="$index !=0" type="checkbox" ng-model="column.show"></input>' +
    								'<br>' +
    								'<select ng-if="$index !=0" ng-model = "column.numFormatType" ng-options = "type for type in formatTypeChoices" ng-change="setDefaultPattern(column)"></select>' +
    								'<br>' +										
    								'<div ng-if="$index !=0" ng-show="!isNumFormatStandard(column)">' + 
    									'<select ng-if="isNumFormatFixed(column)"  ng-model="column.numFormatPattern" ng-options = "pattern for pattern in fixedFormatChoices" ng-change="setDefaultPatternToModelColumn(column)"></select>' +
    									'<select ng-if="!isNumFormatFixed(column)" ng-model = "column.numFormatPattern" ng-options = "pattern for pattern in expFormatChoices" ng-change="setDefaultPatternToModelColumn(column)"></select>' +
    								'</div>' +
    							'</th>' +
    						'</tr>' +
    						'<tr ng-if="toggled">' +
    							'<th ng-if="column.show" ng-repeat="column in ' + columnTable + '.columns">' +
    								'<span ng-bind="column.name"></span>' +
    							'</th>' +
    						'</tr>' +
    						'<tr ng-if="!toggled" ng-repeat="rowValue in ' + columnTable + '.data">' +
    							'<td ng-repeat = "value in rowValue track by $index">' +
    								'<div ng-show="' + columnTable + '.columns[$index].show" ng-bind="value"></div>' +
    								'<div ng-hide="' + columnTable + '.columns[$index].show"></div>' +
    							'</td>' +
    						'</tr>' +
    						'<tr ng-if="toggled" ng-repeat="rowValue in ' + columnTable + '.data">' +
    							'<td ng-if="' + columnTable + '.columns[$index].show" ng-repeat = "value in display(rowValue) track by $index">' +
    								'<div ng-show="' + columnTable + '.columns[$index].show" ng-bind="value"></div>' +
    								'<div ng-hide="' + columnTable + '.columns[$index].show"></div>' +
    							'</td>' +
    						'</tr>' +				
    					'</table>' +
    				'</div>';

	    		var template = //bootstrap-dependent
//	    		'<div class="container">' +
//		    		'<br>' +
		    		'<div class="row">' +
		    			'<div class="col-md-2" style="vertical-align: top; text-align:right; padding-top:15px;  padding-bottom:10px;">' +
		    				'<div ng-if="!toggled">' +
		    					'<div><button class="btn btn-default btn-sm" ng-click="checkAll()" style="font-weight:bold; color:black;" ng-bind="checkAlltext"></button></div>' +
		    					'<div><select ng-model = "modelColumn.numFormatType" ng-options = "type for type in formatTypeChoices" ng-change="setDefaultPattern(modelColumn)"></select></div>' +										
		    					'<div ng-if="!isNumFormatStandard(modelColumn) && toAll">' + 
		    						'<select ng-if="isNumFormatFixed(modelColumn)"  ng-model="modelColumn.numFormatPattern" ng-options = "pattern for pattern in fixedFormatChoices"></select>' +
		    						'<select ng-if="!isNumFormatFixed(modelColumn)" ng-model = "modelColumn.numFormatPattern" ng-options = "pattern for pattern in expFormatChoices"></select>' +
		    					'</div>' +	
		    					'<div><button class="btn btn-default btn-sm" ng-click="SetToAll(modelColumn)" style="font-weight:bold; color:black;">Set Format to All</button></div>' +
		    					'<br>' +
		    				'</div>' +
		    				'<button class="btn btn-default" ng-click="toggleTable()" ng-bind="toggleText"></button>' +
		    				'<div ng-if="!toggled && !showInputField"><button class="btn btn-default" ng-click="enterCSVfileName()">Export to CSV</button></div>' +
		    				'<div ng-if="!toggled && showInputField">' +
		    					'File name:<input type="text" ng-model="fileName" style="width:72%;"></input>' +
		    					'<button class="btn btn-default" ng-click="exportCSV(fileName)">Submit</button>' +
		    				'</div>' +	
		    			'</div>' +
		    			'<div class="col-md-10">' +	
		    				innerTemplate + 
		    			'</div>' +	
		    		'</div>';
//		    	'</div>';
		        
		        
	        	element.html('').append( $compile ( template )( scope ) );
	        }
		}
	}]);
})( angular );