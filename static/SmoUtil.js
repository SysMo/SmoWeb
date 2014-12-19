smoModule = angular.module('smo', []);

smoModule.factory('util', function util () {
	var functions = {};
	function dumpObject(obj, indent) {
		var result = "";
		if (indent == null)
			indent = "";
		for ( var property in obj) {
			var value = obj[property];
			if (typeof value == 'string')
				value = "'" + value + "'";
			else if (typeof value == 'object') {
				if (value instanceof Array) {
					// Just let JS convert the Array to a string!
					value = "[ " + value + " ]";
				} else {
					// Recursive dump
					// (replace " " by "\t" or something else if you prefer)
					var od = dumpObject(value, indent + "  ");
					// If you like { on the same line as the key
					// value = "{\n" + od + "\n" + indent + "}";
					// If you prefer { and } to be aligned
					value = "\n" + indent + "{\n" + od + "\n" + indent
							+ "}";
				}
			}
			result += indent + "'" + property + "' : " + value + ",\n";
		}
		return result.replace(/,\n$/, "");
	}
	functions.dumpObject = dumpObject;
	
	function formatNumber (n) {
		if (n == 0) {
			return "0";
		}
		if (Math.abs(n) < 1e-80){
			return "0";
		}
		if (Math.abs(n) > 1e5 || Math.abs(n) < 1e-3) {
			return n.toExponential(5);
		}
		var sig = 6;
		var mult = Math.pow(10,
				sig - Math.floor(Math.log(Math.abs(n)) / Math.LN10) - 1);
		return String(Math.round(n * mult) / mult);
	}
	functions.formatNumber = formatNumber;

	return functions;
});

smoModule.factory('smoJson', function () {
	
	// Adapted from Crockford's JSON.parse (see https://github.com/douglascrockford/JSON-js)
	// This version adds support for NaN, -Infinity and Infinity.
	var at;	 // The index of the current character
	var ch;	 // The current character
	var escapee = {
				'"':  '"',
				'\\': '\\',
				'/':  '/',
				b:	'\b',
				f:	'\f',
				n:	'\n',
				r:	'\r',
				t:	'\t'
			};
	var text;
	function error(m) {
		throw {
			name: 'SyntaxError',
			message: m,
			at:	at,
			text: text
		};
	}
	function next(c) {
		return ch = text.charAt(at++);
	}
	function check(c) {
		if (c !== ch) {
			error("Expected '" + c + "' instead of '" + ch + "'");
		}
		ch = text.charAt(at++);
	}
	function number() {
		var string = '';
		if (ch === '-') {
			string = '-';
			check('-');
		}
		if (ch === 'I') {
			check('I');
			check('n');
			check('f');
			check('i');
			check('n');
			check('i');
			check('t');
			check('y');
			return -Infinity;
		}
		while (ch >= '0' && ch <= '9') {
			string += ch;
			next();
		}
		if (ch === '.') {
			string += '.';
			while (next() && ch >= '0' && ch <= '9') {
				string += ch;
			}
		}
		if (ch === 'e' || ch === 'E') {
			string += ch;
			next();
			if (ch === '-' || ch === '+') {
				string += ch;
				next();
			}
			while (ch >= '0' && ch <= '9') {
				string += ch;
				next();
			}
		}
		return +string;
	}

	function string() {
		var hex,
			i,
			string = '',
			uffff;
		if (ch === '"') {
			while (next()) {
				if (ch === '"') {
					next();
					return string;
				}
				if (ch === '\\') {
					next();
					if (ch === 'u') {
						uffff = 0;
						for (i = 0; i < 4; i ++) {
							hex = parseInt(next(), 16);
							if (!isFinite(hex)) {
								break;
							}
							uffff = uffff * 16 + hex;
						}
						string += String.fromCharCode(uffff);
					} else if (escapee[ch]) {
						string += escapee[ch];
					} else {
						break;
					}
				} else {
					string += ch;
				}
			}
		}
		error("Bad string");
	}
	
	function white () { // Skip whitespace.
		while (ch && ch <= ' ') {
			next();
		}
	}
	
	function word() {
		switch (ch) {
		case 't':
			check('t');
			check('r');
			check('u');
			check('e');
			return true;
		case 'f':
			check('f');
			check('a');
			check('l');
			check('s');
			check('e');
			return false;
		case 'n':
			check('n');
			check('u');
			check('l');
			check('l');
			return null;
		case 'N':
			check('N');
			check('a');
			check('N');
			return NaN;
		case 'I':
			check('I');
			check('n');
			check('f');
			check('i');
			check('n');
			check('i');
			check('t');
			check('y');
			return Infinity;
		}
		error("Unexpected '" + ch + "'");
	}
	
	function array() {
		var array = [];
		if (ch === '[') {
			check('[');
			white();
			if (ch === ']') {
				check(']');
				return array;   // empty array
			}
			while (ch) {
				array.push(value());
				white();
				if (ch === ']') {
					check(']');
					return array;
				}
				check(',');
				white();
			}
		}
		error("Bad array");
	}
	
	function object() {
		var key, object = {};
		if (ch === '{') {
			check('{');
			white();
			if (ch === '}') {
				check('}');
				return object;   // empty object
			}
			while (ch) {
				key = string();
				white();
				check(':');
				if (Object.hasOwnProperty.call(object, key)) {
					error('Duplicate key "' + key + '"');
				}
				object[key] = value();
				white();
				if (ch === '}') {
					check('}');
					return object;
				}
				check(',');
				white();
			}
		}
		error("Bad object");
	}
	
	function value() {
		white();
		switch (ch) {
		case '{':
			return object();
		case '[':
			return array();
		case '"':
			return string();
		case '-':
			return number();
		default:
			return ch >= '0' && ch <= '9' ? number() : word();
		}
	};
	
	function parseJSON(source, reviver){
		var result;
		text = source;
		at = 0;
		ch = ' ';
		result = value();
		white();
		if (ch) {
			error("Syntax error");
		}	
		return typeof reviver === 'function'
		? (function walk(holder, key) {
			var k, v, value = holder[key];
			if (value && typeof value === 'object') {
				for (k in value) {
					if (Object.prototype.hasOwnProperty.call(value, k)) {
						v = walk(value, k);
						if (v !== undefined) {
							value[k] = v;
						} else {
							delete value[k];
						}
					}
				}
			}
			return reviver.call(holder, key, value);
		}({'': result}, ''))
		: result;
	}

	 function transformResponse(data) {
		var JSON_START = /^\s*(\[|\{[^\{])/,
			JSON_END = /[\}\]]\s*$/,
			PROTECTION_PREFIX = /^\)\]\}',?\n/,
			CONTENT_TYPE_APPLICATION_JSON = {'Content-Type': 'application/json;charset=utf-8'};
        // strip json vulnerability protection prefix
        data = data.replace(PROTECTION_PREFIX, '');
        if (JSON_START.test(data) && JSON_END.test(data))
          data = parseJSON(data);
	      return data;
	}
	
	return {'parse': parseJSON, 'transformResponse': transformResponse};
});

smoModule.factory('ModelCommunicator', function($http, smoJson) {
	function ModelCommunicator(url){
		// Communication URL. Can be left empty if the same as the current page URL
		this.url = url || '';
		// true if waiting to load from the server
		this.loading = false;
		// true if there is error in communication (no response from server or incorrect URL)
		this.commError = false;
		// true if there was an error during processing the request on the server 
		this.serverError = false;
		// error message from commError or serverError
		this.errorMsg = "";
		// true if data has arrived from the server
		this.dataReceived = false;
	}
	ModelCommunicator.prototype.fetchData = function(action, parameters, onSuccess, onFailure) {
		this.loading = true;
		this.commError = false;
		this.serverError = false;
		this.dataReceived = false;
		this.errorMsg = "";
		this.stackTrace = "";
		// Empty the receiver object
		this.data = {};
		this.dataReceived = false;
		// Variable introduced so that success and error functions can access this object
		var communicator = this;
		this.onSuccess = onSuccess;
		this.onFailure = onFailure;
		this.action = action;
		$http({
	        method  : 'POST',
	        url     : this.url,
	        data    : {action : action, parameters: parameters},
	        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
	        transformResponse: [smoJson.transformResponse],
	    })
	    .success(function(response) {
			communicator.loading = false;
			communicator.commError = false;
			if (!response.errStatus) {
				communicator.serverError = false;
				communicator.dataReceived = true;
				communicator.data = response.data;
				communicator.dataReceived = true;
				if (!(typeof onSuccess === 'undefined')) {
					communicator.onSuccess(communicator);
				}
			} else {
				communicator.serverError = true;
				communicator.dataReceived = false;
				communicator.errorMsg = response.error;
				communicator.stackTrace = response.stackTrace;
				if (!(typeof onFailure === 'undefined')) {
					communicator.onFailure(communicator);
				}
			}
	    })
	    .error(function(response) {
			communicator.loading = false;
			communicator.commError = true;
			communicator.serverError = false;
			communicator.errorMsg = response;
			if (!(typeof onFailure === 'undefined')) {
				communicator.onFailure(communicator);
			}
	    });
	}
	return ModelCommunicator;
})

smoModule.directive('smoSingleClick', ['$parse', function($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attr) {
          var fn = $parse(attr['smoSingleClick']);
          var delay = 200, clicks = 0, timer = null;
          element.on('click', function (event) {
            clicks++;  //count clicks
            if(clicks === 1) {
              timer = setTimeout(function() {
                scope.$apply(function () {
                    fn(scope, { $event: event });
                }); 
                clicks = 0;             //after action performed, reset counter
              }, delay);
              } else {
                clearTimeout(timer);    //prevent single-click action
                clicks = 0;             //after action performed, reset counter
              }
          });
        }
    };
}]);

smoModule.factory('variables', ['util', function(util) {
	var variables = {};
	function Quantity(quantity, title, nominalValue, SIUnit, units) {
		this.quantity = quantity;
		this.title = title;
		this.value = nominalValue;
		this.SIUnit = SIUnit;
		this.unitsArr = [];
		for (unit in units) {
			if (unit != this.SIUnit) {
				var unitDef = units[unit];
				var offset = unitDef.offset || 0;
				var value = (this.value - offset) / unitDef.mult;
				this.unitsArr.push([unit, value, String(util.formatNumber(value))]);
			} else {
				this.unitsArr.push([unit, nominalValue, String(util.formatNumber(nominalValue))]);
			}
		}
		
		this.updateValues = function(index, inputError){
			if (inputError) {
				return;
			}
			this.unitsArr[index][1] = Number(this.unitsArr[index][2]);
			if (this.unitsArr[index][0] != this.SIUnit) {
				unitDef = units[this.unitsArr[index][0]];
				offset = unitDef.offset || 0;
				this.value = this.unitsArr[index][1] * unitDef.mult + offset;
			} else {
				this.value = this.unitsArr[index][1];
			}
			for (var i=0; i<this.unitsArr.length; i++) {
				unitDef = units[this.unitsArr[i][0]];
				offset = unitDef.offset || 0;			
				if (i != index)	{
					this.unitsArr[i][1] = util.formatNumber((this.value - offset) / unitDef.mult);
					this.unitsArr[i][2] = String(this.unitsArr[i][1]);
				}		
			}
		}
	}
	variables.Quantity = Quantity;
	return variables;
}]);

smoModule.directive('smoQuantity', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			viewType: '@viewType',
			smoDataSource : '='
		},
		controller: function($scope){
			$scope.checkValueValidity = function(){
				$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('minVal', true);
				$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('maxVal', true);
				
				if ($scope[$scope.fieldVar.name + 'Form'].input.$error.required == true 
						|| $scope[$scope.fieldVar.name + 'Form'].input.$error.pattern == true) {
					return;
				}
				
				if (Number($scope.fieldVar.displayValue) < $scope.fieldVar.minDisplayValue) {
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('minVal', false);
					return;
				}	
				
				if (Number($scope.fieldVar.displayValue) > $scope.fieldVar.maxDisplayValue){
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('maxVal', false);
					return;
				}
				
				$scope.updateValue();
			}
			
			$scope.updateValue = function() {
				var offset = 0;
				if ('offset' in $scope.fieldVar.dispUnitDef) {
					offset = $scope.fieldVar.dispUnitDef.offset;
				}
				$scope.fieldVar.value = Number($scope.fieldVar.displayValue) * $scope.fieldVar.dispUnitDef.mult + offset ;
				$scope.smoDataSource[$scope.fieldVar.name] = $scope.fieldVar.value;	
			}
			
			$scope.changeUnit = function() {
				for (var i=0; i < $scope.fieldVar.units.length; i++) {
					if ($scope.fieldVar.displayUnit == $scope.fieldVar.units[i][0]){
						$scope.fieldVar.dispUnitDef = $scope.fieldVar.units[i][1];
					}	
				}
				var offset = 0;
				if ('offset' in $scope.fieldVar.dispUnitDef) {
					offset = $scope.fieldVar.dispUnitDef.offset;
				}
				$scope.fieldVar.displayValue = util.formatNumber(($scope.fieldVar.value - offset) / $scope.fieldVar.dispUnitDef.mult);
				
				$scope.fieldVar.minDisplayValue = ($scope.fieldVar.minValue - offset) / $scope.fieldVar.dispUnitDef.mult;
				$scope.fieldVar.maxDisplayValue = ($scope.fieldVar.maxValue - offset) / $scope.fieldVar.dispUnitDef.mult;
			}
			
			$scope.fieldVar.unit = $scope.fieldVar.unit || $scope.fieldVar.SIUnit;
			$scope.fieldVar.displayUnit = $scope.fieldVar.displayUnit || $scope.fieldVar.defaultDispUnit || $scope.fieldVar.unit;
			for (var i=0; i < $scope.fieldVar.units.length; i++) {
				if ($scope.fieldVar.unit == $scope.fieldVar.units[i][0]){
					$scope.fieldVar.unitDef = $scope.fieldVar.units[i][1];
				}
				if ($scope.fieldVar.displayUnit == $scope.fieldVar.units[i][0]){
					$scope.fieldVar.dispUnitDef = $scope.fieldVar.units[i][1];
				}	
			}
			
			var offset = $scope.fieldVar.unitDef.offset || 0;
			$scope.fieldVar.value = $scope.fieldVar.value * $scope.fieldVar.unitDef.mult + offset;
			offset = $scope.fieldVar.dispUnitDef.offset || 0;
			$scope.fieldVar.displayValue = util.formatNumber(($scope.fieldVar.value - offset) / $scope.fieldVar.dispUnitDef.mult);
			
			$scope.fieldVar.minDisplayValue = ($scope.fieldVar.minValue - offset) / $scope.fieldVar.dispUnitDef.mult;
			$scope.fieldVar.maxDisplayValue = ($scope.fieldVar.maxValue - offset) / $scope.fieldVar.dispUnitDef.mult;				
		},
		link : function(scope, element, attr) {
			scope.util = util;
			var template = '\
					<div class="field-label">' + scope.fieldVar.label + '</div>';
			if (scope.viewType == 'input'){
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="fieldVar.displayValue" ng-change="checkValueValidity();">\
						</div>\
					</div>';
				template += '\
					<div class="field-select quantity"> \
						<select ng-disabled="!' + scope.fieldVar.name + 'Form.$valid" ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
				
			}
			else if (scope.viewType == 'output'){
				template += '\
					<div class="field-output"> \
						<div class="output" ng-bind="fieldVar.displayValue"></div>\
					</div>';
				template += '\
					<div class="field-select quantity"> \
						<select ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
				
			}
			if (scope.viewType == 'input')
				template += '\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.pattern">Enter a number</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.required">Required value</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.minVal">Value should be above {{util.formatNumber(fieldVar.minDisplayValue)}} {{fieldVar.displayUnit}}</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.maxVal">Value should be below {{util.formatNumber(fieldVar.maxDisplayValue)}} {{fieldVar.displayUnit}}</div>';
			
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);

smoModule.directive('smoChoice', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			choiceVar: '=choiceVar', 
			options: '=smoOptions',
			title: '@smoTitle',
		},
		controller: function($scope){
		},
		link : function(scope, element, attr) {
		var template = ' \
			<div class="field-label">' + scope.title + '</div>\
			<div class="field-select choice"> \
				<select ng-model="choiceVar" ng-options="pair[0] as pair[1] for pair in options"></select> \
			</div>';
		
//		element.html('').append($compile(template)(scope));
		var el = angular.element(template);
        compiled = $compile(el);
        element.append(el);
        compiled(scope);

		}
	}
}]);

smoModule.directive('smoString', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			viewType: '@viewType',
			smoDataSource : '='
		},
		controller: function($scope){
			$scope.fieldVar.value = $scope.smoDataSource[$scope.fieldVar.name];
			$scope.updateValue = function(){
				$scope.smoDataSource[$scope.fieldVar.name] = $scope.fieldVar.value;
			}
		},
		link : function(scope, element, attr) {
			if (scope.fieldVar.multiline==true){
				var template = '\
					<div class="multiline-label">' + scope.fieldVar.label + '</div>';
			} else {
				var template = '\
					<div class="field-label">' + scope.fieldVar.label + '</div>';
			}			
			
			if (scope.viewType == 'input')
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input name="input" required type="text" ng-model="fieldVar.value" ng-change="updateValue()">\
						</div>\
					</div>';
			else if (scope.viewType == 'output'){
				if (scope.fieldVar.multiline==true){
					template += '\
						<div class="field-output"> \
							<div class="multiline-output" ng-bind="fieldVar.value"></div>\
						</div>';
				} else {
					template += '\
						<div class="field-output"> \
							<div class="output" ng-bind="fieldVar.value"></div>\
						</div>';
				}
				
			}
			if (scope.viewType == 'input')
				template += '\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.required">Required value</div>';

		var el = angular.element(template);
        compiled = $compile(el);
        element.append(el);
        compiled(scope);

		}
	}
}]);

smoModule.directive('smoBool', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			viewType: '@viewType',
			smoDataSource : '='
		},
		controller: function($scope){
			$scope.fieldVar.value = $scope.smoDataSource[$scope.fieldVar.name];
			$scope.updateValue = function(){
				$scope.smoDataSource[$scope.fieldVar.name] = $scope.fieldVar.value;
			}
		},
		link : function(scope, element, attr) {			
			var template = '\
				<div class="field-label">' + scope.fieldVar.label + '</div>';			
			if (scope.viewType == 'input'){
				template += '\
					<div class="bool-input"> \
						<input name="input" type="checkbox" ng-model="fieldVar.value" ng-change="updateValue()">\
					</div>';
			}
			else if (scope.viewType == 'output'){				
				template += '\
					<div class="field-output"> \
						<div class="output" ng-bind="fieldVar.value"></div>\
					</div>';	
			}
			
		var el = angular.element(template);
        compiled = $compile(el);
        element.append(el);
        compiled(scope);

		}
	}
}]);

smoModule.directive('smoPlot', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			smoDataSource : '='
		},
		controller: function($scope) {
			
			$scope.plotData = function() {
				$scope.chart = new Dygraph(document.getElementById($scope.fieldVar.name + 'PlotDiv'), 
						$scope.smoDataSource[$scope.fieldVar.name],
						$scope.fieldVar.options);
			}
			
			$scope.pngFileName = $scope.fieldVar.name + '.png';
			
			$scope.exportPNG = function(){
				var img = document.getElementById($scope.fieldVar.name + 'Img');
				Dygraph.Export.asPNG($scope.chart, img);
				
				var link = document.getElementById($scope.fieldVar.name + 'PngElem');
				
			 	if(link.download !== undefined) { // feature detection
			 	  // Browsers that support HTML5 download attribute
			 	  link.setAttribute("href", img.src);
			 	  link.setAttribute("download", $scope.pngFileName);
			 	 } else {
			 		// it needs to implement server side export
					//link.setAttribute("href", "http://www.example.com/export");
			 		  alert("Needs to implement server side export");
			 		  return;
			 	}
			 	
			 	link.click();
			}
			
		},
		link : function(scope, element, attr) {
			var template = '\
							<div style="display: inline-block;">\
								<div id="' + scope.fieldVar.name + 'PlotDiv"></div>\
							</div>\
							<div style="margin-left: 55px; margin-top: 10px;">\
								<div id="' + scope.fieldVar.name + 'LegendDiv"></div>\
							</div>\
							<div style = "margin-top: 10px; margin-bottom: 10px;">\
								Export plot&nbsp\
								<input ng-model="pngFileName"></input>\
								<button ng-click="exportPNG()"><span style="color:#428BCA" class="glyphicon glyphicon-download-alt"></span></button>\
								<img id="' + scope.fieldVar.name + 'Img" hidden>\
								<a id="' + scope.fieldVar.name + 'PngElem" hidden></a>\
							</div>';

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope); 
	        scope.$watch(scope.smoDataSource[scope.fieldVar.name], function(value) {
	        	scope.plotData();
		});
		}	
	}
}]);

smoModule.directive('smoTable', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			smoDataSource : '='
		},
		controller: function($scope) {
			$scope.drawTable = function() {				
				var tableArray = $scope.smoDataSource[$scope.fieldVar.name];
				
				//Creating the GViz DataTable object
				$scope.dataTable = google.visualization.arrayToDataTable(tableArray);
				//Drawing the table
				var tableView = new google.visualization.Table(document.getElementById($scope.fieldVar.name + 'TableDiv'));
				
				if(typeof $scope.fieldVar.options.formats === 'string'){
					for (var i=0; i < tableArray[0].length; i++){
						formatter = new google.visualization.NumberFormat({pattern: $scope.fieldVar.options.formats});
						formatter.format($scope.dataTable, i);
					}
				} else {
					for (var i=0; i < tableArray[0].length; i++){
						try {
							formatter = new google.visualization.NumberFormat({pattern: $scope.fieldVar.options.formats[i]});
						}
						catch(err) {
							formatter = new google.visualization.NumberFormat();
						}
						
						formatter.format($scope.dataTable, i);
					}
				}
				
				tableView.draw($scope.dataTable, {showRowNumber: true, sort:'disable', page:'enable', pageSize:14});
			}
			
			$scope.csvFileName = $scope.fieldVar.name + '.csv';
			
			$scope.exportCSV = function(){
				var dataLabels = $scope.smoDataSource[$scope.fieldVar.name][0];
				var dataLabelsString = dataLabels.join(",");
				var csvString = dataLabelsString + "\n";
				
				var dataTable = google.visualization.arrayToDataTable($scope.smoDataSource[$scope.fieldVar.name]);
				var dataTableCSV = google.visualization.dataTableToCsv(dataTable);
				
				csvString += dataTableCSV;
				
				// download stuff
			 	var blob = new Blob([csvString], {
			 	  "type": "text/csv;charset=utf8;"			
			 	});
			 	var link = document.getElementById($scope.fieldVar.name + 'CsvElem');
							
			 	if(link.download !== undefined) { // feature detection
			 	  // Browsers that support HTML5 download attribute
			 	  link.setAttribute("href", window.URL.createObjectURL(blob));
			 	  link.setAttribute("download", $scope.csvFileName);
			 	 } else {
			 		// it needs to implement server side export
					//link.setAttribute("href", "http://www.example.com/export");
			 		  alert("Needs to implement server side export");
			 		  return;
			 	}
//	 		 	document.body.appendChild(link);
			 	link.click();
			}
		},
		link : function(scope, element, attr) {
			var template = '<div id="' + scope.fieldVar.name + 'TableDiv"></div>\
			<div style = "margin-top: 10px; margin-bottom: 10px;">\
				Export data&nbsp\
				<input ng-model="csvFileName"></input>\
				<button ng-click="exportCSV()"><span style="color:#428BCA" class="glyphicon glyphicon-download-alt"></span></button>\
				<a id="' + scope.fieldVar.name + 'CsvElem" hidden></a>\
			</div>';  

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope); 
	        scope.$watch(scope.smoDataSource[scope.fieldVar.name], function(value) {
				scope.drawTable();
		});
		}	
	}
}]);

smoModule.directive('smoFieldGroup', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			smoFieldGroup : '=',
			smoDataSource : '=',
			viewType: '='
		},
		link : function(scope, element, attr) {
			scope.fields = {};
			var groupFields = [];
			for (var i = 0; i < scope.smoFieldGroup.fields.length; i++) {
				var field = scope.smoFieldGroup.fields[i];
				scope.fields[field.name] = field;
				var showFieldCode = "";
				if (!(typeof field.show === "undefined")){
					showFieldCode = 'ng-show="' + field.show.replace(/self/g, 'smoDataSource') + '"';
				}
				if (field.type == 'Quantity') {
					field.value = scope.smoDataSource[field.name];
					field.id = field.name;
					
					// Attach the field value to the quantity so that the original value is updated when the quantity value changes
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showFieldCode + ' smo-quantity view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showFieldCode + ' smo-quantity view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'Choices') {
					if (scope.viewType == 'input')
						groupFields.push('<div ' + showFieldCode + ' smo-choice choice-var="smoDataSource.' + field.name + '"' +
						' smo-options="smoFieldGroup.fields[' + i + '].options" smo-title="' + field.label + '"></div>');
				} else if (field.type == 'String') {
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showFieldCode + ' smo-string view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showFieldCode + ' smo-string view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'Boolean') {
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showFieldCode + ' smo-bool view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showFieldCode + ' smo-bool view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				}			
			}
			
			var template;
			
			if (scope.smoFieldGroup.label) {
				template = '<div class="field-group-label" style="margin-top: 25px;">' + scope.smoFieldGroup.label + '</div><br>' 
				+ groupFields.join("");
			} else {
				template = '<br>' 
				+ groupFields.join("");
			}

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);

smoModule.directive('smoViewGroup', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			smoViewGroup : '=',
			smoDataSource : '='
		},
		controller: function($scope) {
			
		},
		link : function(scope, element, attr) {
			var template;
			if (scope.smoViewGroup.label) {
				template = '<div class="field-group-label" style="margin-top: 25px;">' + scope.smoViewGroup.label + '</div><br>';
			} else {
				template = '<br>';
			}
			
			if (scope.smoViewGroup.fields.length > 1) {
				var navPills = [];
				var navPillPanes = [];
				scope.fields = {};
				
				for (var i = 0; i < scope.smoViewGroup.fields.length; i++) {
					var field = scope.smoViewGroup.fields[i];
					scope.fields[field.name] = field;
					var showFieldCode = "";
					if (!(typeof field.show === "undefined")){
						showFieldCode = 'ng-show="' + field.show.replace(/self/g, 'smoDataSource') + '"';
					}
					
					if (i==0){
						navPills.push('<li class="active"><a id="' + field.name + 'Tab" data-target="#' + field.name + '" role="tab" data-toggle="tab">' + field.label + '</a></li>');
						navPillPanes.push('<div class="tab-pane active" id="' + field.name + '">');
					} else {
						navPills.push('<li><a id="' + field.name + 'Tab" data-target="#' + field.name + '" role="tab" data-toggle="tab">' + field.label + '</a></li>');
						navPillPanes.push('<div class="tab-pane" id="' + field.name + '">');
					}
					
					if (field.type == 'PlotView') {
						navPillPanes.push('<div ' + showFieldCode + ' smo-plot field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					} else if (field.type == 'TableView') {
						navPillPanes.push('<div ' + showFieldCode + ' smo-table field-var="fields.' + field.name + '" smo-data-source="smoDataSource" style="max-width: 840px; overflow: auto;"></div>');
					}
					
					navPillPanes.push('</div>'); 
					
				}
				
				template += '\
					<div style="white-space: nowrap; background-color: white; padding :10px;">\
						<div style="display: inline-block; vertical-align: top; cursor: pointer;">\
							<ul class="nav nav-pills nav-stacked">' + navPills.join("") + '</ul>\
						</div>\
						<div class="tab-content" style="display: inline-block; padding-left: 7px;">'
							+ navPillPanes.join("") + 
						'</div>\
					</div>';
				
			} else if (scope.smoViewGroup.fields.length == 1) {
				var field = scope.smoViewGroup.fields[0];
				var showFieldCode = "";
				if (!(typeof field.show === "undefined")){
					showFieldCode = 'ng-show="' + field.show.replace(/self/g, 'smoDataSource') + '"';
				}
				
				template += '\
					<div style="white-space: nowrap; background-color: white; padding :10px; text-align: center;">';
				
				if (field.type == 'PlotView') {
					template += '<div ' + showFieldCode + ' smo-plot field-var="smoViewGroup.fields[0]" smo-data-source="smoDataSource"></div>';
				} else if (field.type == 'TableView') {
					template += '<div ' + showFieldCode + ' smo-table field-var="smoViewGroup.fields[0]" smo-data-source="smoDataSource" style="max-width: 840px; overflow: auto;"></div>';
				}
				
				template += '</div>';					
			}
			
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        
//	        angular.element('#' + scope.smoViewGroup.name + ' a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
//        		scope.activeTabId = e.target.id; // activated tab
//        		var activeFieldName = scope.activeTabId.slice(0, -3);
//        		scope.activeField = scope.fields[activeFieldName];
//				scope.csvFileName =  scope.activeField.name + '.csv';
//				scope.$digest();
//				});
	        
	        compiled(scope);
		}	
	}
}]);


smoModule.directive('smoSuperGroupSet', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			smoSuperGroupSet : '=',
			smoDataSource : '=',
			viewType: '@viewType'
		},
		link : function(scope, element, attr) {	
			if (scope.smoSuperGroupSet.length > 1) {
				var navTabs = [];
				var navTabPanes = [];
				for (var i = 0; i < scope.smoSuperGroupSet.length; i++) {
					var superGroup = scope.smoSuperGroupSet[i];
					if (i==0){
						navTabs.push('<li class="active"><a id="' + superGroup.name + 'Tab" data-target="#' + superGroup.name + '" role="tab" data-toggle="tab">' + superGroup.label + '</a></li>');
						navTabPanes.push('<div class="tab-pane active" id="' + superGroup.name + '">');
					} else {
						navTabs.push('<li><a id="' + superGroup.name + 'Tab" data-target="#' + superGroup.name + '" role="tab" data-toggle="tab">' + superGroup.label + '</a></li>');
						navTabPanes.push('<div class="tab-pane" id="' + superGroup.name + '">');
					}
					
					var superGroupFields = [];
					for (var j = 0; j < superGroup.groups.length; j++) {
						if (superGroup.groups[j].type == 'FieldGroup') {
							// Attach the field value to the quantity so that the original value is updated when the quantity value changes
							superGroupFields.push('<div smo-field-group="smoSuperGroupSet[' + i + '].groups[' + j + ']" view-type="viewType" smo-data-source="smoDataSource"></div>');
						} else if (superGroup.groups[j].type == 'ViewGroup') {
							superGroupFields.push('<div smo-view-group="smoSuperGroupSet[' + i + '].groups[' + j + ']" smo-data-source="smoDataSource"></div>');
						}						
					}
					
					navTabPanes.push(superGroupFields.join(""));
					navTabPanes.push('</div>');
				}
				var template = '<ul class="nav nav-tabs" role="tablist">' + navTabs.join("") + '</ul>' +
				'<div class="tab-content super-group">' + navTabPanes.join("") + '</div>';
			} else if (scope.smoSuperGroupSet.length == 1) {
				var superGroup = scope.smoSuperGroupSet[0];
				var superGroupFields = [];
				for (var j = 0; j < superGroup.groups.length; j++) {
					if (superGroup.groups[j].type == 'FieldGroup') {
						// Attach the field value to the quantity so that the original value is updated when the quantity value changes
						superGroupFields.push('<div smo-field-group="smoSuperGroupSet[0].groups[' + j + ']" view-type="viewType" smo-data-source="smoDataSource"></div>');
					} else if (superGroup.groups[j].type == 'ViewGroup') {
						superGroupFields.push('<div smo-view-group="smoSuperGroupSet[0].groups[' + j + ']" smo-data-source="smoDataSource"></div>');
					}					
				}
				var template = '<div class="super-group">' +
									'<h1>' + superGroup.label + '</h1>' +
									 superGroupFields.join("") + 
								'</div>';
			}
			

			
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);
			
smoModule.directive('smoModelView', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			communicator: '=',
			name: '@smoModelView',
			viewType: '@viewType'
		},
		controller: function($scope) {
			$scope.formName = $scope.name+'Form';
		},
		link : function(scope, element, attr) {
			var template = '\
				<div ng-if="communicator.loading" class="alert alert-info" role="alert">Loading...</div>\
				<div ng-if="communicator.commError" class="alert alert-danger" role="alert">Communication error: <span ng-bind="communicator.errorMsg"></span></div>\
				<div ng-if="communicator.serverError" class="alert alert-danger" role="alert">Server error: <span ng-bind="communicator.errorMsg"></span>\
					<div>Stack trace:</div><pre><div ng-bind="communicator.stackTrace"></div></pre>\
				</div>\
				<div ng-form name="' + scope.formName + '">\
					<div ng-if="communicator.dataReceived">\
						<div smo-super-group-set="communicator.data.definitions" view-type="' + scope.viewType + '" smo-data-source="communicator.data.values"></div>\
					</div>\
				</div>';

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
			scope.$watch(scope.formName + '.$valid', function(validity) {
					scope.communicator.fieldsValid = validity;					
			});	        
		}	
	}
}]);

smoModule.directive('smoArrayQuantity', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			viewType: '@viewType',
			smoDataSource : '='
		},
		controller: function($scope){
			$scope.fieldVar.value = $scope.smoDataSource[$scope.fieldVar.name];
			$scope.checkValueValidity = function(){
				$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('minVal', true);
				$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('maxVal', true);
				
				if ($scope[$scope.fieldVar.name + 'Form'].input.$error.required == true 
						|| $scope[$scope.fieldVar.name + 'Form'].input.$error.pattern == true) {
					return;
				}
				
				if (Number($scope.fieldVar.displayValue) < $scope.fieldVar.minDisplayValue) {
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('minVal', false);
					return;
				}	
				
				if (Number($scope.fieldVar.displayValue) > $scope.fieldVar.maxDisplayValue){
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('maxVal', false);
					return;
				}
				
				$scope.updateValue();
			}
			
			$scope.updateValue = function() {
				var offset = 0;
				if ('offset' in $scope.fieldVar.dispUnitDef) {
					offset = $scope.fieldVar.dispUnitDef.offset;
				}
				$scope.fieldVar.value = Number($scope.fieldVar.displayValue) * $scope.fieldVar.dispUnitDef.mult + offset ;
				$scope.smoDataSource[$scope.fieldVar.name] = $scope.fieldVar.value;	
			}
			
			$scope.changeUnit = function() {
				for (var i=0; i < $scope.fieldVar.units.length; i++) {
					if ($scope.fieldVar.displayUnit == $scope.fieldVar.units[i][0]){
						$scope.fieldVar.dispUnitDef = $scope.fieldVar.units[i][1];
					}	
				}
				var offset = 0;
				if ('offset' in $scope.fieldVar.dispUnitDef) {
					offset = $scope.fieldVar.dispUnitDef.offset;
				}
				$scope.fieldVar.displayValue = util.formatNumber(($scope.fieldVar.value - offset) / $scope.fieldVar.dispUnitDef.mult);
				
				$scope.fieldVar.minDisplayValue = ($scope.fieldVar.minValue - offset) / $scope.fieldVar.dispUnitDef.mult;
				$scope.fieldVar.maxDisplayValue = ($scope.fieldVar.maxValue - offset) / $scope.fieldVar.dispUnitDef.mult;
			}
			
			$scope.fieldVar.unit = $scope.fieldVar.unit || $scope.fieldVar.SIUnit;
			$scope.fieldVar.displayUnit = $scope.fieldVar.displayUnit || $scope.fieldVar.defaultDispUnit || $scope.fieldVar.unit;
			for (var i=0; i < $scope.fieldVar.units.length; i++) {
				if ($scope.fieldVar.unit == $scope.fieldVar.units[i][0]){
					$scope.fieldVar.unitDef = $scope.fieldVar.units[i][1];
				}
				if ($scope.fieldVar.displayUnit == $scope.fieldVar.units[i][0]){
					$scope.fieldVar.dispUnitDef = $scope.fieldVar.units[i][1];
				}	
			}
			
			var offset = $scope.fieldVar.unitDef.offset || 0;
			$scope.fieldVar.value = $scope.fieldVar.value * $scope.fieldVar.unitDef.mult + offset;
			offset = $scope.fieldVar.dispUnitDef.offset || 0;
			$scope.fieldVar.displayValue = util.formatNumber(($scope.fieldVar.value - offset) / $scope.fieldVar.dispUnitDef.mult);
			
			$scope.fieldVar.minDisplayValue = ($scope.fieldVar.minValue - offset) / $scope.fieldVar.dispUnitDef.mult;
			$scope.fieldVar.maxDisplayValue = ($scope.fieldVar.maxValue - offset) / $scope.fieldVar.dispUnitDef.mult;				
		},
		link : function(scope, element, attr) {
			scope.util = util;
			var template = '\
					<div class="field-label">' + scope.fieldVar.label + '</div>';
			if (scope.viewType == 'input'){
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="fieldVar.displayValue" ng-change="checkValueValidity();">\
						</div>\
					</div>';
				template += '\
					<div class="field-select quantity"> \
						<select ng-disabled="!' + scope.fieldVar.name + 'Form.$valid" ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
				
			}
			else if (scope.viewType == 'output'){
				template += '\
					<div class="field-output"> \
						<div class="output" ng-bind="fieldVar.displayValue"></div>\
					</div>';
				template += '\
					<div class="field-select quantity"> \
						<select ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
				
			}
			if (scope.viewType == 'input')
				template += '\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.pattern">Enter a number</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.required">Required value</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.minVal">Value should be above {{util.formatNumber(fieldVar.minDisplayValue)}} {{fieldVar.displayUnit}}</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.maxVal">Value should be below {{util.formatNumber(fieldVar.maxDisplayValue)}} {{fieldVar.displayUnit}}</div>';
			
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);

smoModule.directive('smoArrayGroup', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			smoArrayGroup: '=',
			smoDataSource : '='
		},
		controller: function($scope){
							
		},
		link : function(scope, element, attr) {
			scope.util = util;
			scope.arrValue = scope.smoDataSource[scope.smoArrayGroup.name];
			
			for (var i=0; i<scope.smoArrayGroup.fields.length; i++){
				scope.smoArrayGroup.fields[i].value = [];
				scope.smoArrayGroup.fields[i].displayValue = [];
				for (row in scope.arrValue){
					scope.smoArrayGroup.fields[i].value.push(scope.arrValue[row][i]);
				}
			}
			
			for (var i=0; i<scope.smoArrayGroup.fields.length; i++){
				scope.smoArrayGroup.fields[i].unit 
					= scope.smoArrayGroup.fields[i].unit || scope.smoArrayGroup.fields[i].SIUnit;
				scope.smoArrayGroup.fields[i].displayUnit 
					= scope.smoArrayGroup.fields[i].displayUnit || scope.smoArrayGroup.fields[i].defaultDispUnit || scope.smoArrayGroup.fields[i].unit;
				
				for (var j=0; j<scope.smoArrayGroup.fields[i].units.length; j++) {
					if (scope.smoArrayGroup.fields[i].unit == scope.smoArrayGroup.fields[i].units[j][0]){
						scope.smoArrayGroup.fields[i].unitDef = scope.smoArrayGroup.fields[i].units[j][1];
					}
					if (scope.smoArrayGroup.fields[i].displayUnit == scope.smoArrayGroup.fields[i].units[j][0]){
						scope.smoArrayGroup.fields[i].dispUnitDef = scope.smoArrayGroup.fields[i].units[j][1];
					}	
				}
				
				var offset = scope.smoArrayGroup.fields[i].unitDef.offset || 0;
				
				
				for (var row=0; row<scope.arrValue.length; row++){
					scope.smoArrayGroup.fields[i].value[row]
						= scope.smoArrayGroup.fields[i].value[row] * scope.smoArrayGroup.fields[i].unitDef.mult + offset;
					offset = scope.smoArrayGroup.fields[i].dispUnitDef.offset || 0;
					scope.smoArrayGroup.fields[i].displayValue[row] 
						= util.formatNumber((scope.smoArrayGroup.fields[i].value[row] - offset) / scope.smoArrayGroup.fields[i].dispUnitDef.mult);
				}
				
			}
			
			
			var template = '\
					<div class="field-label">' + scope.smoArrayGroup.label + '</div>';
			
			template += '\
			<div>\
				<table class="nice-table">\
					<th style="text-align: center;" ng-repeat="field in smoArrayGroup.fields">\
						<div style="margin-bottom: 5px;">\
							{{field.name}}\
						</div>\
						<div class="field-select quantity"> \
							<select ng-model="field.displayUnit" ng-options="pair[0] as pair[0] for pair in field.units"></select>\
						</div>\
					</th>\
					<tr ng-repeat="row in arrValue track by $index">\
						<td ng-repeat="field in smoArrayGroup.fields">\
							<div class="field-input">\
								<input name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="field.displayValue[$index]">\
							</div>\
						</td>\
					</tr>\
				</table>\
			</div>';
			
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);