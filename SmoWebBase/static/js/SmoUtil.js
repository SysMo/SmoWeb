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

smoModule.factory('ModelCommunicator', function($http, $window, $timeout, $location, smoJson) {
	function ModelCommunicator(model, modelName, viewName, url){		
		this.model = model;
		this.modelName = modelName;
		this.viewName = viewName;
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
		var postData = {
			modelName: this.modelName,
			viewName: this.viewName,
			parameters: parameters
		}
		
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
		//this.action = action;
		$http({
	        method  : 'POST',
	        url     : this.url,
	        data    : {action : action, data: postData},
	        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
	        transformResponse: [smoJson.transformResponse]
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
	ModelCommunicator.prototype.saveUserInput = function(action, parameters) {
		var communicator = this;
		this.saveFeedbackMsg = "";
		this.saveSuccess = false;
		
		var parameters = parameters || this.data.values;
		var postData = {
			modelName: this.modelName,
			viewName: this.viewName,
			parameters: parameters
		}
		
		$http({
	        method  : 'POST',
	        url     : this.url,
	        data    : {action: action, data: postData},
	        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
	        transformResponse: [smoJson.transformResponse]
	    })
	    .success(function(response) {
			if (!response.errStatus) {
				communicator.currentUrl = $location.absUrl();
				communicator.savedRecordUrl = $location.protocol() + '://' + $location.host() + ':' 
					+ $location.port() + $location.path() 
					+ '?model=' + response.data.model + '&view=' + response.data.view + '&id=' + response.data.id;
				communicator.saveSuccess = true;
				communicator.saveFeedbackMsg = "Input data saved.";
				//$timeout($window.alert("Input data saved"));
			} else {
				//$timeout($window.alert("Failed to save input data"));
				communicator.saveFeedbackMsg = "Failed to save input data";
			}
	    })
	    .error(function(response) {
	    	communicator.saveFeedbackMsg = "Failed to save input data";
	    	//$timeout($window.alert("Failed to save input data"));
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

//<smo-button action="addRow(i)" icon="plus">
smoModule.directive('smoButton', ['$compile', 'util', function($compile, util) {
	return {
		restrict: 'E',
		link : function(scope, element, attr) {
			var action = attr['action'];
			var icon = attr['icon'];
			var tooltip = attr['tip'] || '';
			var size = attr['size'] || 'sm';
			var width = 16;
			if (size == 'lg') {
				width = 32;
			} else if (size == 'md') {
				width = 24;
			}
			var template = '<img class="smo-button" src="/static/icons/' + icon + '.png" ng-click="' + action + '" width="' + width + 'px" data-tooltip="' + tooltip + '">';
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.replaceWith(el);
	        compiled(scope);

		}
	};
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
			fieldVar: '=', 
			smoDataSource : '='
		},
		link : function(scope, element, attr) {
		var template = ' \
			<div class="field-label">' + scope.fieldVar.label + '</div>\
			<div class="field-select choice"> \
				<select ng-model="smoDataSource.' + scope.fieldVar.name + '" ng-options="pair[0] as pair[1] for pair in fieldVar.options"></select> \
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
//								<button ng-click="exportPNG()"><span style="color:#428BCA" class="glyphicon glyphicon-download-alt"></span></button>\
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
								<smo-button icon="save" size="md" action="exportPNG()" tip="Save plot"></smo-button>\
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
			$scope.expanded = false;
			$scope.toggle = function(){
				$scope.expanded = !$scope.expanded;
				if ($scope.expanded == false){
					$scope.drawTable();
				}
			}
			
			
			$scope.init = function(){
				$scope.tableArray = $scope.smoDataSource[$scope.fieldVar.name];
				$scope.displayValuesArray = angular.copy($scope.tableArray.slice(1));
//				console.log($scope.displayValuesArray);
				
				$scope.displayUnits = [];
				$scope.dispUnitDefs = [];
				for (var i=0; i < $scope.fieldVar.columnUnitDefs.length; i++){
					$scope.displayUnits.push($scope.fieldVar.columnUnitDefs[i][0]);
				}
				
				$scope.labelsArray = [];
				for (var i=0; i<$scope.tableArray[0].length; i++){
					$scope.labelsArray.push($scope.tableArray[0][i] + ' [' + $scope.displayUnits[i] + ']');
				}
				$scope.displayTable = angular.copy($scope.displayValuesArray);
				$scope.displayTable.unshift($scope.labelsArray);
				
				//Creating the GViz DataTable object
				$scope.dataTable = google.visualization.arrayToDataTable($scope.displayTable);
				$scope.dataView = new google.visualization.DataView($scope.dataTable);
				//Setting initial visibility
				$scope.columnsShow = [];
				for (var i=0; i<$scope.fieldVar.visibleColumns.length; i++){
					$scope.columnsShow[$scope.fieldVar.visibleColumns[i]] = true;
				}
				$scope.allChecked = true;
				var numEditRows;
				if ($scope.tableArray[0].length % 5){
					numEditRows = Math.floor($scope.tableArray[0].length/5) + 1;
				} else {
					numEditRows = Math.floor($scope.tableArray[0].length/5);
				}
				$scope.editRows = [];
				for (var i=0; i<numEditRows; i++){
					$scope.editRows.push(i);
				}
				$scope.setDataView();
				$scope.drawTable();
			}
						
			$scope.updateChecked = function(){
				$scope.allChecked = false;
				$scope.setDataView();
			}
			
			$scope.setToAll = function(){
				for (i=0; i<$scope.columnsShow.length; i++){
					$scope.columnsShow[i] = $scope.allChecked;
				}
				$scope.setDataView();
			}
			
			$scope.setDataView = function(){
				$scope.viewCloumns = [];
				for (i=0; i<$scope.tableArray[0].length; i++){
					if ($scope.columnsShow[i] == true){
						$scope.viewCloumns.push(i);
					}
				}
				$scope.dataView.setColumns($scope.viewCloumns);
			}	
			
			$scope.changeUnit = function(col) {
				for (var i=0; i < $scope.fieldVar.columnUnitDefs[col][1].length; i++) {
					if ($scope.displayUnits[col] == $scope.fieldVar.columnUnitDefs[col][1][i][0]){
						$scope.dispUnitDefs[col] = $scope.fieldVar.columnUnitDefs[col][1][i][1];
					}
				}
				
				var offset = 0;
				if ('offset' in $scope.dispUnitDefs[col]) {
					offset = $scope.dispUnitDefs[col].offset;
				}
				
				
				for (var row=0; row < $scope.displayValuesArray.length; row ++){
					$scope.displayValuesArray[row][col] 
						= ($scope.tableArray[row+1][col] - offset) / $scope.dispUnitDefs[col].mult; 
				}
				
//				console.log($scope.displayValuesArray[0][col]);
				
				$scope.labelsArray[col] = $scope.tableArray[0][col] + ' [' + $scope.displayUnits[col] + ']';
				
				$scope.displayTable = angular.copy($scope.displayValuesArray);
				$scope.displayTable.unshift($scope.labelsArray);
				
				$scope.dataTable = google.visualization.arrayToDataTable($scope.displayTable);
				$scope.dataView = new google.visualization.DataView($scope.dataTable);
				$scope.setDataView();
			}
			
			$scope.drawTable = function() {
				//Drawing the table
				var tableView = new google.visualization.Table(document.getElementById($scope.fieldVar.name + 'TableDiv'));
				
				if(typeof $scope.fieldVar.options.formats === 'string'){
					for (var i=0; i < $scope.tableArray[0].length; i++){
						formatter = new google.visualization.NumberFormat({pattern: $scope.fieldVar.options.formats});
						formatter.format($scope.dataTable, i);
					}
				} else {
					for (var i=0; i < $scope.tableArray[0].length; i++){
						try {
							formatter = new google.visualization.NumberFormat({pattern: $scope.fieldVar.options.formats[i]});
						}
						catch(err) {
							formatter = new google.visualization.NumberFormat();
						}
						
						formatter.format($scope.dataTable, i);
					}
				}
				
				tableView.draw($scope.dataView, {showRowNumber: true, sort:'disable', page:'enable', pageSize:14});
			}
			
			$scope.csvFileName = $scope.fieldVar.name + '.csv';
			
			$scope.exportCSV = function(){
				var exportTable = $scope.dataView.toDataTable();		
				var labels = [];
				for (var i=0; i<exportTable.getNumberOfColumns(); i++){
					labels.push(exportTable.getColumnLabel(i));
				}
				
				var labelsString = labels.join(",");
				var csvString = labelsString + "\n";
				
//				var dataTable = google.visualization.arrayToDataTable($scope.smoDataSource[$scope.fieldVar.name]);
				var dataTableCSV = google.visualization.dataTableToCsv(exportTable);
				
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
//				<button ng-click="exportCSV()"><span style="color:#428BCA" class="glyphicon glyphicon-download-alt"></span></button>\

			var template = '<div id="' + scope.fieldVar.name + 'TableDiv"></div>\
			<div style = "margin-top: 10px; margin-bottom: 10px;">\
				Export data&nbsp\
				<input ng-model="csvFileName"></input>\
				<smo-button icon="save" size="md" action="exportCSV()" tip="Save data"></smo-button>\
				<a id="' + scope.fieldVar.name + 'CsvElem" hidden></a>\
				<smo-button action="toggle()" icon="settings" tip="Settings" size="md"></smo-button>\
				<div class="table-view-edit" ng-show="expanded">\
					<div style="cursor: pointer; margin-top: 50px; margin-right: 20px;"><smo-button action="toggle()" icon="close" tip="Close editor"></smo-button></div>\
					<table class="nice-table" style="border: none;">\
						<tr>\
							<th style="min-width: 10px;">\
								<input type="checkbox" ng-model="allChecked" ng-change="setToAll()"></input>\
								<span>All</span>\
							</th>\
						</tr>\
						</tr>\
						<tr ng-repeat="row in editRows">\
							<td style="min-width: 10px;" ng-repeat="columnName in tableArray[0].slice(row*5, row*5+5) track by $index">\
								<input type="checkbox" ng-model="columnsShow[row*5 + $index]" ng-change="updateChecked()"></input>\
								<span ng-bind="columnName"></span>\
								<div class="field-select quantity"> \
									<select ng-model="displayUnits[row*5 + $index]" ng-options="pair[0] as pair[0] for pair in fieldVar.columnUnitDefs[row*5 + $index][1]" ng-change="changeUnit(row*5 + $index)"></select>\
								</div>\
							</td>\
						</tr>\
					</table>\
				</div>\
			</div>';  

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope); 
	        scope.$watch(scope.smoDataSource[scope.fieldVar.name], function(value) {
				scope.init();
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
						groupFields.push('<div ' + showFieldCode + ' smo-choice field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
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
				} else if (field.type == 'RecordArray') {
						groupFields.push('<div smo-record-array="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				}	
			}
			
			var template;
			
			if (scope.smoFieldGroup.label) {
				template = '<div class="field-group-label" style="margin-top: 25px;">' + scope.smoFieldGroup.label + '</div>' + 
					'<div class="field-group-container">' +
						groupFields.join("") +
					'</div>';
			} else {
				template = '<div class="field-group-container">' +
					groupFields.join("") +
				'</div>';
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
				template = '<div class="field-group-label" style="margin-top: 25px;">' + scope.smoViewGroup.label + '</div>';
			} else {
				template = '';
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
					<div class="view-group-container" style="white-space: nowrap;">\
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
			modelName: '@modelName',
			viewType: '@viewType'
		},
		link : function(scope, element, attr) {	
			if (scope.smoSuperGroupSet.length > 1) {
				var navTabs = [];
				var navTabPanes = [];
				for (var i = 0; i < scope.smoSuperGroupSet.length; i++) {
					var superGroup = scope.smoSuperGroupSet[i];
					if (i==0){
						navTabs.push('<li class="active"><a id="' + scope.modelName + superGroup.name + 'Tab" data-target="#' + scope.modelName + superGroup.name + '" role="tab" data-toggle="tab">' + superGroup.label + '</a></li>');
						navTabPanes.push('<div class="tab-pane active" id="' + scope.modelName + superGroup.name + '">');
					} else {
						navTabs.push('<li><a id="' + scope.modelName + superGroup.name + 'Tab" data-target="#' + scope.modelName + superGroup.name + '" role="tab" data-toggle="tab">' + superGroup.label + '</a></li>');
						navTabPanes.push('<div class="tab-pane" id="' + scope.modelName + superGroup.name + '">');
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
			

smoModule.directive('smoRecordArray', ['$compile', 'util', function($compile, util) {
	return {
		restrict : 'A',
		scope : {
			smoRecordArray: '=',
			smoDataSource : '='
		},
		controller: function($scope){
			
			$scope.expanded = false;
			$scope.toggle = function(){
				$scope.expanded = !$scope.expanded;
			}
			
			
			$scope.checkValueValidity = function(row, col, form){
				var field = $scope.smoRecordArray.fields[col];
				
				form.input.$setValidity('minVal', true);
				form.input.$setValidity('maxVal', true);
				
				
				if (form.input.$error.required == true 
						|| form.input.$error.pattern == true) {
					return;
				}
				
				if (Number($scope.arrDisplayValue[row][col]) < field.minDisplayValue) {
					form.input.$setValidity('minVal', false);
					return;
				}	
				
				if (Number($scope.arrDisplayValue[row][col]) > field.maxDisplayValue){
					form.input.$setValidity('maxVal', false);
					return;
				}
				
				$scope.updateQuantity(row, col);
			}
			
			$scope.updateQuantity = function(row, col) {
				var field = $scope.smoRecordArray.fields[col];
				
				var offset = 0;
				if ('offset' in field.dispUnitDef) {
					offset = field.dispUnitDef.offset;
				}
				
				$scope.arrValue[row][col] = Number($scope.arrDisplayValue[row][col]) * field.dispUnitDef.mult + offset;
			}
			
			$scope.changeUnit = function(col) {
				var field = $scope.smoRecordArray.fields[col];
				
				for (var i=0; i<field.units.length; i++) {
					if (field.displayUnit == field.units[i][0]){
						field.dispUnitDef = field.units[i][1];
					}	
				}
				
				var offset = 0;
				if ('offset' in field.dispUnitDef) {
					offset = field.dispUnitDef.offset;
				}
				
				for (var row=0; row<$scope.arrValue.length; row++){
					$scope.arrDisplayValue[row][col]
						= util.formatNumber(($scope.arrValue[row][col] - offset) / field.dispUnitDef.mult);
				}
				
				field.minDisplayValue = (field.minValue - offset) / field.dispUnitDef.mult;
				field.maxDisplayValue = (field.maxValue - offset) / field.dispUnitDef.mult;
			}
			
			$scope.addRow = function(row) {
				$scope.smoDataSource[$scope.smoRecordArray.name].splice(row, 0, 
						angular.copy($scope.smoDataSource[$scope.smoRecordArray.name][row]));
				$scope.arrDisplayValue.splice(row, 0, 
						angular.copy($scope.arrDisplayValue[row]));
			}
			
			$scope.delRow = function(row) {
				$scope.smoDataSource[$scope.smoRecordArray.name].splice(row, 1);
				$scope.arrDisplayValue.splice(row, 1);
			}
			
		},
		link : function(scope, element, attr) {
			scope.util = util;
			scope.arrValue = scope.smoDataSource[scope.smoRecordArray.name];
			scope.arrDisplayValue = angular.copy(scope.arrValue);
			
			var headerRowTemplate = '';
			var rowTemplate = '';
			
			for (var col=0; col<scope.smoRecordArray.fields.length; col++){
				var field = scope.smoRecordArray.fields[col];
				
				if (field.type == 'Quantity') {
					headerRowTemplate += '\
							<th>\
								<div style="margin-bottom: 5px;">\
									{{smoRecordArray.fields[' + String(col) + '].label}}\
								</div>\
								<div class="field-select quantity"> \
									<select ng-model="smoRecordArray.fields[' + String(col) + '].displayUnit" \
										ng-options="pair[0] as pair[0] for pair in smoRecordArray.fields[' + String(col) + '].units" \
										ng-change="changeUnit(' + String(col) + ')"></select>\
								</div>\
							</th>';
				} else {
					headerRowTemplate += '\
							<th>\
								<div style="margin-bottom: 5px;">\
									{{smoRecordArray.fields[' + String(col) + '].label}}\
								</div>\
							</th>';
				}
				
				
				if (field.type == 'Quantity') {
					
					field.unit 
						= field.unit || field.SIUnit;
					field.displayUnit 
						= field.displayUnit || field.defaultDispUnit || field.unit;
					
					for (var i=0; i<field.units.length; i++) {
						if (field.unit == field.units[i][0]){
							field.unitDef = field.units[i][1];
						}
						if (field.displayUnit == field.units[i][0]){
							field.dispUnitDef = field.units[i][1];
						}	
					}
					
					var unitOffset = field.unitDef.offset || 0;
					var dispUnitOffset = field.dispUnitDef.offset || 0;
					
					for (var row=0; row<scope.arrValue.length; row++){
						scope.arrValue[row][col]
							= scope.arrValue[row][col] * field.unitDef.mult + unitOffset;
						
						scope.arrDisplayValue[row][col] 
							= util.formatNumber((scope.arrValue[row][col] - dispUnitOffset) / field.dispUnitDef.mult); 
					}
					
					field.minDisplayValue = (field.minValue - dispUnitOffset) / field.dispUnitDef.mult;
					field.maxDisplayValue = (field.maxValue - dispUnitOffset) / field.dispUnitDef.mult;
					
					rowTemplate += '\
						<td>\
							<div class="field-input">\
								<div ng-form name="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form">\
									<input name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" \
										ng-model="arrDisplayValue[i][' + String(col) + ']" ng-change="checkValueValidity(i,' + String(col) + ', ' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form)">\
								</div>\
							</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.pattern">Enter a number</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.required">Required value</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.minVal">Value should be above ' + util.formatNumber(scope.smoRecordArray.fields[col].minDisplayValue) + ' ' + scope.smoRecordArray.fields[col].displayUnit + '</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.maxVal">Value should be below ' + util.formatNumber(scope.smoRecordArray.fields[col].maxDisplayValue) + ' ' + scope.smoRecordArray.fields[col].displayUnit + '</div>\
						</td>';
					
				} else if (field.type == 'Boolean') {
					rowTemplate += '\
						<td>\
							<div class="bool-input">\
								<input name="input" type="checkbox" \
									ng-model="arrValue[i][' + String(col) + ']">\
							</div>\
						</td>';
				} else if (field.type == 'String') {
					rowTemplate += '\
						<td>\
							<div class="field-input">\
								<div ng-form name="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form">\
									<input name="input" required type="text" \
										ng-model="arrValue[i][' + String(col) + ']">\
								</div>\
							</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.required">Required value\
							</div>\
						</td>';
				} else if (field.type == 'Choices') {
					rowTemplate += '\
					<td>\
						<div class="field-select choice"> \
							<select ng-model="arrValue[i][' + String(col) + ']" \
								ng-options="pair[0] as pair[1] for pair in smoRecordArray.fields[' + String(col) + '].options" \
								ng-init="arrValue[i][' + String(col) + ']=smoRecordArray.fields[' + String(col) + '].options[0][0]"></select>\
						</div>\
					</td>';
				}
			}
			
			var template = '\
			<div class="field-label">' + scope.smoRecordArray.label + '</div>\
			<div class="field-input"><smo-button action="toggle()" icon="edit" tip="Edit" size="md"></smo-button></div>';
			//			<div class="field-input"><button class="btn btn-primary" style="height: 30px;" ng-click="toggle()">Edit</button></div>';
			
			template += '\
			<div class="record-array" ng-show="expanded">\
				<div style="cursor: pointer; margin-top: 50px; margin-right: 20px;"><smo-button action="toggle()" icon="close" tip="Close editor"></smo-button></div>\
				<div>\
				<table class="nice-table">\
					<tr>\
						<th style="min-width: 10px;">\
						</th>' +
							headerRowTemplate +
						'<th style="min-width: 10px;">\
						</th>\
					</tr>\
					<tr ng-repeat="row in arrValue track by $index" ng-init="i=$index">\
						<td style="min-width: 10px;">\
							{{i}}\
						</td>' +
							rowTemplate + 
						'<td style="min-width: 10px; cursor: pointer;">\
							<div><smo-button action="addRow(i)" icon="plus" tip="Add row"></smo-button></div>\
							<div><smo-button action="delRow(i)" icon="minus" tip="Remove row"></smo-button></div>\
						</td>\
					</tr>\
				</table>\
				</div>\
			</div>';
			
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);

smoModule.directive('smoViewToolbar', ['$compile', '$rootScope', function($compile, $rootScope) {
	return {
		scope: {
			model: "=",
			viewName: "=",
			actions: "="
		},
		controller: function($scope) {
			var formName = $scope.model.name + $scope.viewName + 'Form';
			$scope.form = $scope.$parent[formName];
			var onFetchSuccess = function(comm){
				if (comm.data.values.recordId){
					comm.model.recordId = comm.data.values.recordId;
				} 
			}
			
			$scope.actionHandler = function(action) {
				var targetView = action.outputView || $scope.viewName;
				var communicator = $scope.model[targetView + 'Communicator'];
				
				if (action.name == 'save') {
					communicator.saveUserInput('save', 
						$scope.model[$scope.viewName + 'Communicator'].data.values);
				} else {
					if (communicator.model.recordId) {
						$scope.model[$scope.viewName + 'Communicator'].data.values.recordId =
							communicator.model.recordId;
					}
					communicator.fetchData(action.name,
						$scope.model[$scope.viewName + 'Communicator'].data.values, onFetchSuccess);
				}
			}
		},
		link : function(scope, element, attr) {
			buttons = [];
			for (var i = 0; i < scope.actions.length; i++) {
				buttons.push('<button type="button" ng-disabled="!form.$valid" class="btn btn-primary" ng-click="actionHandler(actions[' + i + '])">' + scope.actions[i].label + '</button>');
			}
			var template = '<div style="margin-left: 20px;" class="btn-group" role="group">'+ buttons.join("") + '</div>';
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		
		}		
	}
}]);
                                     

smoModule.directive('smoModelView', ['$compile', '$location', 'ModelCommunicator', 
         function($compile, $location, ModelCommunicator) {
	return {
		restrict : 'A',
		scope : {
			modelName: '@',
			viewName: '@smoModelView',
			viewType: '@viewType',
			autoFetch: '=',
			viewRecordId: '@viewRecordId'
		},
		controller: function($scope) {
			$scope.formName = $scope.modelName + $scope.viewName + 'Form';
			$scope.model = $scope.$parent[$scope.modelName];
			$scope.communicator = new ModelCommunicator($scope.model, $scope.modelName, $scope.viewName);
			$scope.model[$scope.viewName + 'Communicator'] = $scope.communicator;
			if ($scope.autoFetch) {
				$scope.communicator.fetchData("load", {viewRecordId: $scope.viewRecordId});				
			}
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
						<div smo-super-group-set="communicator.data.definitions" model-name="' + scope.modelName + '" view-type="' + scope.viewType + '" smo-data-source="communicator.data.values"></div>\
						<div smo-view-toolbar model="model" view-name="viewName" actions="communicator.data.actions"></div>\
						<div ng-if="communicator.saveSuccess">\
							<div class="alert alert-success alert-dismissible" role="alert">\
							<button type="button" class="close" data-dismiss="alert" aria-label="Close">\
								<span aria-hidden="true">&times;</span></button>\
							<span>{{communicator.saveFeedbackMsg}}</span>\
							URL: <a ng-href={{communicator.savedRecordUrl}}>{{communicator.savedRecordUrl}}</a>\
						</div>\
						<div ng-if="!communicator.saveSuccess">\
							<div class="alert alert-danger alert-dismissible" role="alert">\
							<button type="button" class="close" data-dismiss="alert" aria-label="Close">\
								<span aria-hidden="true">&times;</span></button>\
							<span>{{communicator.saveFeedbackMsg}}</span>\
						</div>\
					</div>\
				</div>'

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