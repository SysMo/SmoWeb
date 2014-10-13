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

smoModule.factory('units', function() {
	var units = {};
	// List of quantities and units
	units.quantities = {
		'Length' : {title : 'length', nominalValue : 1, defUnit : 'm', 
			units : {'m' : {mult : 1}, 'km' : {mult : 1e3}, 'cm' : {mult : 1e-2}, 'mm' : {mult : 1e-3}, 
			'um' : {mult : 1e-6}, 'nm' : {mult : 1e-9}, 'in' : {mult : 2.54e-2}, 'ft' : {mult : 3.048e-1}}},
		'Area' : {title : 'area', nominalValue : 1, defUnit : 'm**2', 
			units : {'m**2' : {mult : 1}, 'cm**2' : {mult : 1e-4}, 'mm**2' : {mult : 1e-6}}}, 
		'Volume' : {title : 'volume', nominalValue : 1, defUnit : 'm**3', 
			units : {'m**3' : {mult : 1}, 'cm**3' : {mult : 1e-6}, 'mm**3' : {mult : 1e-9}}},
		'Time' : {title : 'time', nominalValue : 1, defUnit : 's', 
			units : {'s' : {mult : 1}, 'ms' : {mult : 1e-3}, 'us' : {mult : 1e-6}, 'min' : {mult : 60}, 'h' : {mult : 3600}, 'day' : {mult : 8.64e4}, 'year' : {mult : 3.15576e7}}}, 
		'Mass' : {title : 'mass', nominalValue : 1, defUnit : 'kg', 
			units : {'kg' : {mult : 1}, 'ton' : {mult : 1e3}, 'g' : {mult : 1e-3}}},
		'Pressure' : {title : 'pressure', nominalValue : 1e5, defUnit : 'bar', 
			units : {'Pa' : {mult : 1}, 'kPa' : {mult : 1e3}, 'MPa' : {mult : 1e6}, 'GPa' : {mult : 1e9}, 
				'bar' : {mult : 1e5}, 'psi' : {mult : 6.89475e3}, 'ksi' : {mult : 6.89475e6}}},
		'Temperature' : {title : 'temperature', nominalValue : 273.15, defUnit : 'K', 
			units : {'K' : {mult : 1}, 'degC' : {mult : 1, offset : 273.15}, 'degF' : {mult : 5./9, offset : 255.372}}},
		'Density' : {title : 'density', nominalValue : 1, defUnit : 'kg/m**3', 
			units : {'kg/m**3' : {mult : 1}, 'g/L' : {mult : 1}, 'g/cm**3' : {mult : 1e3}}},
		'SpecificEnthalpy' : {title : 'specific enthalpy', nominalValue : 1e6, defUnit : 'kJ/kg', 
			units : {'J/kg' : {mult : 1}, 'kJ/kg' : {mult : 1e3}}},
		'SpecificInternalEnergy' : {title : 'specific internal energy', nominalValue : 1e6, defUnit : 'kJ/kg', 
			units : {'J/kg' : {mult : 1}, 'kJ/kg' : {mult : 1e3}}},
		'SpecificEntropy' : {title : 'specific entropy', nominalValue : 1, defUnit : 'kJ/kg-K', 
			units : {'J/kg-K' : {mult : 1}, 'kJ/kg-K' : {mult : 1e3}}},
		'VaporQuality' : {title : 'vapor quality', nominalValue : 1, defUnit : '-', 
			units : {'-' : {mult : 1}}}
	};

	// Object for handling quantity
	var Quantity = function (quantity, value, unit, displayUnit) {		
		this.quantity = quantity;
		unit = unit || units.quantities[this.quantity].defUnit;
		this.displayUnit = displayUnit || unit; //units.quantities[this.quantity].defUnit;
		
		var unitDef = units.quantities[this.quantity].units[unit];		
		var offset = unitDef.offset || 0;
		
		this.value = value * unitDef.mult + offset;		

		var dispUnitDef = units.quantities[this.quantity].units[this.displayUnit];
		offset = dispUnitDef.offset || 0;
		this.displayValue = (this.value - offset) / dispUnitDef.mult; 
	}

	Quantity.prototype.updateQuantity = function() {
		var dispUnitDef = units.quantities[this.quantity].units[this.displayUnit];
		var offset = 0;
		if ('offset' in dispUnitDef) {
			offset = dispUnitDef.offset;
		}
		this.value = this.displayValue * dispUnitDef.mult + offset ; 
	}
	Quantity.prototype.changeUnit = function() {
		var dispUnitDef = units.quantities[this.quantity].units[this.displayUnit];
		var offset = 0;
		if ('offset' in dispUnitDef) {
			offset = dispUnitDef.offset;
		}
		this.displayValue = (this.value - offset) / dispUnitDef.mult; 
	}
	units.Quantity = Quantity;
	return units;
});

smoModule.directive('smoInputQuantity', ['$compile', function($compile) {
	return {
		restrict : 'E',
		link : function(scope, element, attr) {
			var qVar = attr.smoQuantityVar;
			var template =  '<input type="number" step="any" ng-init="' + qVar + '.changeUnit()" ng-model="' + qVar + '.displayValue" ng-change="' + qVar + '.updateQuantity()">' +
			'<select ng-model="' + qVar + '.displayUnit" ng-options="name as name for (name, conv) in units.quantities[' + qVar + '.quantity].units" ng-change="' + qVar + '.changeUnit()"></select>';
			element.html('').append($compile(template)(scope));
		}
	}
}]);

/*
 * Some code that could be used for resizing but doesn't work currently
 smoModule.directive('smoResizer', function($document) {

	return function($scope, $element, $attrs) {

		$element.on('mousedown', function(event) {
			event.preventDefault();

			$document.on('mousemove', mousemove);
			$document.on('mouseup', mouseup);
		});

		function mousemove(event) {

			if ($attrs.resizer == 'vertical') {
				// Handle vertical resizer
				var x = event.pageX;

				if ($attrs.resizerMax && x > $attrs.resizerMax) {
					x = parseInt($attrs.resizerMax);
				}

				$element.css({
					left: x + 'px'
				});

				$($attrs.resizerLeft).css({
					width: x + 'px'
				});
				$($attrs.resizerRight).css({
					left: (x + parseInt($attrs.resizerWidth)) + 'px'
				});

			} else {
				// Handle horizontal resizer
				var y = window.innerHeight - event.pageY;

				$element.css({
					bottom: y + 'px'
				});

				$($attrs.resizerTop).css({
					bottom: (y + parseInt($attrs.resizerHeight)) + 'px'
				});
				$($attrs.resizerBottom).css({
					height: y + 'px'
				});
			}
		}

		function mouseup() {
			$document.unbind('mousemove', mousemove);
			$document.unbind('mouseup', mouseup);
		}
	};
});
*/