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

smoModule.factory('materials', function() {
	var materials = {
		solids : {
			'StainlessSteel304': {'title': 'stainless steel 304'}, 
			'Aluminium6061': {'title': 'aluminium 6061'}
		},
		fluids : {
			"ParaHydrogen" : {title : "ParaHydrogen"},
			"OrthoHydrogen" : {title : "OrthoHydrogen"},
			"Hydrogen" : {title : "Hydrogen"},
			"Water" : {title : "Water"},
			"Air" : {title : "Air"},
			"Nitrogen" : {title : "Nitrogen"},
			"Oxygen" : {title : "Oxygen"},
			"CarbonDioxide" : {title : "CarbonDioxide"},
			"CarbonMonoxide" : {title : "CarbonMonoxide"},
			"R134a" : {title : "R134a"},
			"R1234yf" : {title : "R1234yf"},
			"R1234ze(Z)" : {title : "R1234ze(Z)"},
			"Ammonia" : {title : "Ammonia"},
			"Argon" : {title : "Argon"},
			"Neon" : {title : "Neon"},
			"Helium" : {title : "Helium"},
			"Methane" : {title : "Methane"},
			"Ethane" : {title : "Ethane"},
			"Ethylene" : {title : "Ethylene"},
			"n-Propane" : {title : "n-Propane"},
			"n-Butane" : {title : "n-Butane"},
			"IsoButane" : {title : "IsoButane"},
			"n-Pentane" : {title : "n-Pentane"},
			"Isopentane" : {title : "Isopentane"},
			"Methanol" : {title : "Methanol"},
			"Ethanol" : {title : "Ethanol"}
		}
	};
	return materials;
});

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
				if ($scope.fieldVar.value < $scope.fieldVar.minValue) {
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('minVal', false);
				}		
				else if ($scope.fieldVar.value > $scope.fieldVar.maxValue){
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('maxVal', false);
				}
				if ($scope[$scope.fieldVar.name + 'Form'].$valid == true) {
					$scope.updateValue();
				}
			}
			
			$scope.revertOnInvalidity = function(){
				if ($scope[$scope.fieldVar.name + 'Form'].$valid == false) {
					$scope.fieldVar.value = $scope.smoDataSource[$scope.fieldVar.name];
					var offset = 0;
					if ('offset' in $scope.fieldVar.dispUnitDef) {
						offset = $scope.fieldVar.dispUnitDef.offset;
					}
					$scope.fieldVar.displayValue = util.formatNumber(($scope.fieldVar.value - offset) / $scope.fieldVar.dispUnitDef.mult);
				}
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
			
		},
		link : function(scope, element, attr) {
			scope.util = util;
			var template = '\
					<div class="field-label">' + scope.fieldVar.label + '</div>';
			if (scope.viewType == 'input')
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="fieldVar.displayValue" ng-blur="revertOnInvalidity()" ng-change="checkValueValidity();">\
						</div>\
					</div>';
			else if (scope.viewType == 'output')
				template += '\
					<div class="field-output"> \
						<div class="output" ng-bind="fieldVar.displayValue"></div>\
					</div>';
			
			template += '\
					<div class="field-select quantity"> \
						<select ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
			if (scope.viewType == 'input')
				template += '\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.pattern">Enter a number</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.required">Required value</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.minVal">Number is below min value</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.maxVal">Number exceeds max value</div>';
			
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
					showFieldCode = 'ng-show="' + field.show.replace('self', 'smoDataSource') + '"';
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
			var template = '<div class="field-group-label">' + (scope.smoFieldGroup.label || "") + '</div><br>' 
				+ groupFields.join("");

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
						var fieldGroup = superGroup.groups[j];
						// Attach the field value to the quantity so that the original value is updated when the quantity value changes
						superGroupFields.push('<div smo-field-group="smoSuperGroupSet[' + i + '].groups[' + j + ']" view-type="viewType" smo-data-source="smoDataSource"></div>');
					}
					
					navTabPanes.push(superGroupFields.join(""));
				}
				var template = '<ul class="nav nav-tabs super-group" role="tablist">' + navTabs.join("") + '</ul>' +
				'<div class="super-group">' + navTabPanes.join("") + '</div>';
			} else if (scope.smoSuperGroupSet.length == 1) {
				var superGroup = scope.smoSuperGroupSet[0];
				var superGroupFields = [];
				for (var j = 0; j < superGroup.groups.length; j++) {
					var fieldGroup = superGroup.groups[j];
					// Attach the field value to the quantity so that the original value is updated when the quantity value changes
					superGroupFields.push('<div smo-field-group="smoSuperGroupSet[0].groups[' + j + ']" view-type="viewType" smo-data-source="smoDataSource"></div>');
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
			
smoModule.directive('smoInputView', ['$compile', 'smoJson', function($compile, smoJson) {
	return {
		restrict : 'A',
		scope : {
			it: '=smoInputView'
		},
		controller: function($scope, $http){
			$scope.it.inputsObtained = false;
			$scope.it.loading = false;
			$scope.it.errorLoading = false;
			$scope.it.fetchData = function(parameters) {
				$scope.it.inputsObtained = false;
				$scope.it.loading = true;
				$scope.it.errorLoading = false;
				var parameters = parameters || {};				
				$http({
			        method  : 'POST',
			        url     : $scope.it.dataUrl,
			        data    : {action : $scope.it.action, parameters: parameters},
			        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
			        transformResponse: [smoJson.transformResponse]
				})
			    .success(function(data) {
			    	$scope.it.loading = false;
			    	$scope.it.inputsObtained = true;
			    	$scope.it.data = data;
			    })
			    .error(function(data) {
			    	$scope.it.loading = false;
			    	$scope.it.errorLoading = true;
			    });
			}
			if ($scope.it.autoFetch || $scope.it.autoFetch == 'undefined'){
				$scope.it.fetchData();
			} else {
				$scope.it.inputsObtained = true;
			}
		},
		link : function(scope, element, attr) {
			var template = '<div ng-if="it.loading"><h2 class="loading">Loading...</h2></div>\
							<div ng-if="it.errorLoading"><h2 class="error">Error loading!</h2></div>\
							<div ng-if="it.inputsObtained">\
								<div  smo-super-group-set="it.data.definitions" view-type="input" smo-data-source="it.data.values"></div>\
							</div>';				

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);


smoModule.directive('smoOutputView', ['$compile', 'smoJson', function($compile, smoJson) {
	return {
		restrict : 'A',
		scope : {			
			it: '=smoOutputView'
		},
		controller: function($scope, $http){
			$scope.it.outputsObtained = false;
			$scope.it.loading = false;
			$scope.it.errStatus = false;
			$scope.it.fetchData = function(parameters) {
				$scope.it.outputsObtained = false;
				$scope.it.loading = true;
				$scope.it.errorLoading = false;
				var parameters = parameters || {};
				$http({
			        method  : 'POST',
			        url     : $scope.it.dataUrl,
			        data    : { action : $scope.it.action, parameters: parameters},
			        headers : { 'Content-Type': 'application/x-www-form-urlencoded' },  // set the headers so angular passing info as form data (not request payload)
			        transformResponse: [smoJson.transformResponse]
				})
			    .success(function(data) {
			    	$scope.it.errStatus = data.errStatus;
			    	if (!$scope.it.errStatus) {
			    		$scope.it.loading = false;
				    	$scope.it.outputsObtained = true;
				    	$scope.it.data = data;
			    	}
			    	else {
			    		$scope.it.loading = false;
			    		$scope.it.outputsObtained = false;
				    	$scope.it.error = data.error || 'Error loading!';
			    	}
			    });
			}
		},
		link : function(scope, element, attr) {
			var template = '<div ng-if="it.loading"><h2 class="loading">Loading...</h2></div>\
							<div ng-if="it.errStatus" style="margin-left:20px;">\
								<br>\
								<div class="alert alert-danger" role="alert">\
								  <span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>\
								  <span class="sr-only">Error:</span>\
								  {{it.error}}\
								</div>\
							</div>\
							<div ng-if="it.outputsObtained">\
								<div smo-super-group-set="it.data.definitions" view-type="output" smo-data-source="it.data.values"></div>\
							</div>';		
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);

smoModule.directive('converterInputView', ['$compile', 'variables', function($compile, variables) {
	return {
		restrict : 'A',
		scope : {
			it: '=converterInputView'
		},
		controller: function($scope, $http){
			$scope.it.inputsObtained = false;
			$scope.it.loading = false;
			$scope.it.errorLoading = false;
			$scope.it.fetchData = function(parameters) {
				$scope.it.inputsObtained = false;
				$scope.it.loading = true;
				$scope.it.errorLoading = false;
				var parameters = parameters || {};
				$http({
			        method  : 'POST',
			        url     : $scope.it.dataUrl,
			        data    : {action : $scope.it.action, parameters: parameters},
			        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
			    })
			    .success(function(data) {
			    	$scope.it.loading = false;
			    	$scope.it.inputsObtained = true;
			    	$scope.it.quantities = data;
			    	$scope.renderConverter();
			    })
			    .error(function(data) {
			    	$scope.it.loading = false;
			    	$scope.it.errorLoading = true;
			    });
			}
			if ($scope.it.autoFetch || $scope.it.autoFetch == 'undefined'){
				$scope.it.fetchData();
			}
			$scope.renderConverter = function() {
				$scope.quantities = {};
				for (name in $scope.it.quantities) {
					var value = $scope.it.quantities[name];
					if (value.SIUnit == '-')
						continue
					else {
						$scope.quantities[value.title] = new variables.Quantity(name, value.title, value.nominalValue, value.SIUnit, value.units);
					}
				}
				$scope.choiceVar = $scope.quantities[Object.keys($scope.quantities)[0]];
			}
		},
		link : function(scope, element, attr) {
			var template = '<div ng-if="it.loading"><h2 class="loading">Loading...</h2></div>\
							<div ng-if="it.errorLoading"><h2 class="error">Error loading!</h2></div>\
							<div class="converter" ng-if="it.inputsObtained">\
								<div class="super-group">\
									<div class="choice-group">\
										<div class="select-text">Select a quantity:</div>\
										<div>\
											<select ng-model="choiceVar" ng-options="value as name for (name, value) in quantities"></select> \
										</div>\
									</div>\
									<div class="results-group">\
										<div class="field" ng-repeat="unit in choiceVar.unitsArr track by $index">\
											<div ng-form name="Form{{$index}}" class="field-input">\
												<input name="input" type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="unit[2]" ng-change="choiceVar.updateValues($index, Form{{$index}}.input.$error.pattern)">\
											</div>\
											<div class="field-label" ng-bind="unit[0]"></div>\
											<div class="input-error" ng-show="Form{{$index}}.input.$error.pattern">Enter a valid number</div>\
										</div>\
									</div>\
								</div>\
							</div>';

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);

//<div ng-show="Form{{$index}}.input.$error.pattern"></div>\