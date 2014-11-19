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
				$scope.updateValue();							
				if ($scope.fieldVar.value < $scope.fieldVar.minValue) {
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('minVal', false);
				}		
				else if ($scope.fieldVar.value > $scope.fieldVar.maxValue){
					$scope[$scope.fieldVar.name + 'Form'].input.$setValidity('maxVal', false);
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
							<input name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="fieldVar.displayValue" ng-change="checkValueValidity();">\
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
				}
			}
			var template = '<h3>' + (scope.smoFieldGroup.label || "") + '</h3><br>' 
				+ groupFields.join("");

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);

smoModule.directive('smoSuperGroup', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			smoSuperGroup : '=',
			smoDataSource : '=',
			viewType: '@viewType'
		},
		link : function(scope, element, attr) {	
			
			var navTabs = [];
			var navTabPanes = [];
			for (var i = 0; i < scope.smoSuperGroup.length; i++) {
				var superGroup = scope.smoSuperGroup[i];
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
					superGroupFields.push('<div smo-field-group="smoSuperGroup[' + i + '].groups[' + j + ']" view-type="viewType" smo-data-source="smoDataSource"></div>');
				}
				
				navTabPanes.push(superGroupFields.join(""));
			}
			var template = '<ul class="nav nav-tabs super-group" role="tablist">' + navTabs.join("") + '</ul>' +
			'<div class="tab-content super-group">' + navTabPanes.join("") + '</div>';

			
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);
			
smoModule.directive('smoInputView', ['$compile', function($compile) {
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
								<div  smo-super-group="it.data.definitions" view-type="input" smo-data-source="it.data.values"></div>\
							</div>';				

			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}	
	}
}]);


smoModule.directive('smoOutputView', ['$compile', function($compile) {
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
							<div ng-if="it.errStatus">\
								<br>\
								<div class="alert alert-danger" role="alert">\
								  <span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>\
								  <span class="sr-only">Error:</span>\
								  {{it.error}}\
								</div>\
							</div>\
							<div ng-if="it.outputsObtained">\
								<div smo-super-group="it.data.definitions" view-type="output" smo-data-source="it.data.values"></div>\
							</div>';		
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);
