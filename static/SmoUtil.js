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
	functions['formatNumber'] = function (n) {
		if (n > 1e5 || n < 1e-3) {
			return n.toExponential(5);
		}
		var sig = 6;
		var mult = Math.pow(10,
				sig - Math.floor(Math.log(n) / Math.LN10) - 1);
		return Math.round(n * mult) / mult;
	} 
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
		'Dimensionless' : {title : 'dimensionless quantity', nominalValue : 1, defUnit : '-', 
				units : {'-' : {mult : 1}}},
		'Length' : {title : 'length', nominalValue : 1, defUnit : 'm', 
			units : {'m' : {mult : 1}, 'km' : {mult : 1e3}, 'cm' : {mult : 1e-2}, 'mm' : {mult : 1e-3}, 
			'um' : {mult : 1e-6}, 'nm' : {mult : 1e-9}, 'in' : {mult : 2.54e-2}, 'ft' : {mult : 3.048e-1}}},
		'Area' : {title : 'area', nominalValue : 1, defUnit : 'm**2', 
			units : {'m**2' : {mult : 1}, 'cm**2' : {mult : 1e-4}, 'mm**2' : {mult : 1e-6}}},
		'Volume' : {title : 'volume', nominalValue : 1, defUnit : 'm**3', 
			units : {'m**3' : {mult : 1}, 'L' : {mult : 1e-3}, 'cm**3' : {mult : 1e-6}, 'mm**3' : {mult : 1e-9}}},
		'Time' : {title : 'time', nominalValue : 1, defUnit : 's', 
			units : {'s' : {mult : 1}, 'ms' : {mult : 1e-3}, 'us' : {mult : 1e-6}, 'min' : {mult : 60}, 'h' : {mult : 3600}, 'day' : {mult : 8.64e4}, 'year' : {mult : 3.15576e7}}},
		'Velocity' : {title : 'velocity', nominalValue : 1, defUnit : 'm/s', 
				units : {'m/s' : {mult : 1}, 'km/h' : {mult : 1/3.6}, 'km/s' : {mult : 1e3}, 'mm/s' : {mult : 1e-3}}},
		'Mass' : {title : 'mass', nominalValue : 1, defUnit : 'kg', 
			units : {'kg' : {mult : 1}, 'g' : {mult : 1e-3}, 'ton' : {mult : 1e3}}},
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
			units : {'-' : {mult : 1}}},
		'MassFlowRate' : {title : 'mass flow rate', nominalValue : 1, defUnit : 'kg/s', 
			units : {'kg/s' : {mult : 1}, 'g/s' : {mult : 1e-3}, 'kg/min' : {mult : 1./60}, 'g/min' : {mult : 1e-3/60}, 
				'kg/h' : {mult : 1/3.6e3}, 'g/h' : {mult : 1e-3/3.6e3}}},
		'VolumetricFlowRate' : {title : 'volumetric flow rate', nominalValue : 1, defUnit : 'm**3/s', 
			units : {'m**3/s' : {mult : 1}, 'm**3/h' : {mult : 1./3.6e3}, 'L/s' : {mult : 1e-3},
				'L/min' : {mult : 1e-3/60}, 'L/h' : {mult : 1e-3/3.6e3}}}
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

smoModule.factory('materials', function() {
	var materials = {
		solids : {
			'StainlessSteel304' : {title : 'stainless steel 304', 'rho' : 7800},
			'Aluminium6061' : {title : 'aluminium 6061', 'rho' : 2700}
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

smoModule.directive('smoInputQuantity', ['$compile', function($compile) {
	return {
		restrict : 'E',
		link : function(scope, element, attr) {
			var qVar = attr.smoQuantityVar;
			var title = attr.smoTitle;
			var template = '<div><div style="display: inline-block;text-align: right;width: 10em;">' + title + '</div>&nbsp;' + 
			'<div style="display: inline-block;"><input type="number" step="any" ng-init="' + qVar + '.changeUnit()" ng-model="' + qVar + '.displayValue" ng-change="' + qVar + '.updateQuantity()">' +
			'<select ng-model="' + qVar + '.displayUnit" ng-options="name as name for (name, conv) in units.quantities[' + qVar + '.quantity].units" ng-change="' + qVar + '.changeUnit()"></select></div></div>';
			element.html('').append($compile(template)(scope));
		}
	}
}]);

smoModule.directive('smoOutputQuantity', ['$compile', function($compile) {
	return {
		restrict : 'E',
		link : function(scope, element, attr) {
			var qVar = attr.smoQuantityVar;
			var title = attr.smoTitle;
			var outputStyle = "display: inline-block; border: 1px solid #888; padding: 1.7pt; width : 10em;";
			var template = '<div><div style="display: inline-block;text-align: right;width: 10em;">' + title + '</div>&nbsp;<div style="' + outputStyle + '" ng-bind="util.formatNumber(' + qVar + '.displayValue)"></div>' +
			'&nbsp;<select ng-model="' + qVar + '.displayUnit" ng-options="name as name for (name, conv) in units.quantities[' + qVar + '.quantity].units" ng-change="' + qVar + '.changeUnit()"></select></div></div>';
			element.html('').append($compile(template)(scope));
		}
	}
}]);


smoModule.directive('smoInputGroup', ['$compile', function($compile) {
	return {
		restrict : 'E',
		link : function(scope, element, attr) {
			var group = attr.smoGroupVar;
			var tableRows = [];
			scope[group].fields.forEach(function(element, index, array) {
				tableRows.push('<tr><td style="text-align:right;">' + element.title + '&nbsp;</td><td><smo-input-quantity smo-quantity-var="' + 
						group + '.fields[' + index + '].quantity"><smo-input-quantity></td></tr>');
			});
			var tableBodyTemplate = tableRows.join("");
			var template = '<h2>' + scope[group].name + '</h2><table><tbody>' + tableBodyTemplate + '</tbody></table>';
			element.html('').append($compile(template)(scope));
		}
	}
}]);


//\'%.2g\' | sprintf : 

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