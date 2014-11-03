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
		'Dimensionless' : {title : 'dimensionless quantity', nominalValue : 1, SIUnit : '-', 
				units : {'-' : {mult : 1}}},
		'Length' : {title : 'length', nominalValue : 1, SIUnit : 'm', 
			units : {'m' : {mult : 1}, 'km' : {mult : 1e3}, 'cm' : {mult : 1e-2}, 'mm' : {mult : 1e-3}, 
			'um' : {mult : 1e-6}, 'nm' : {mult : 1e-9}, 'in' : {mult : 2.54e-2}, 'ft' : {mult : 3.048e-1}}},
		'Area' : {title : 'area', nominalValue : 1, SIUnit : 'm**2', 
			units : {'m**2' : {mult : 1}, 'cm**2' : {mult : 1e-4}, 'mm**2' : {mult : 1e-6}}},
		'Volume' : {title : 'volume', nominalValue : 1, SIUnit : 'm**3', 
			units : {'m**3' : {mult : 1}, 'L' : {mult : 1e-3}, 'cm**3' : {mult : 1e-6}, 'mm**3' : {mult : 1e-9}}},
		'Time' : {title : 'time', nominalValue : 1, SIUnit : 's', 
			units : {'s' : {mult : 1}, 'ms' : {mult : 1e-3}, 'us' : {mult : 1e-6}, 'min' : {mult : 60}, 'h' : {mult : 3600}, 'day' : {mult : 8.64e4}, 'year' : {mult : 3.15576e7}}},
		'Velocity' : {title : 'velocity', nominalValue : 1, SIUnit : 'm/s', 
				units : {'m/s' : {mult : 1}, 'km/h' : {mult : 1/3.6}, 'km/s' : {mult : 1e3}, 'mm/s' : {mult : 1e-3}}},
		'Mass' : {title : 'mass', nominalValue : 1, SIUnit : 'kg', 
			units : {'kg' : {mult : 1}, 'g' : {mult : 1e-3}, 'ton' : {mult : 1e3}}},
		'Pressure' : {title : 'pressure', nominalValue : 1e5, SIUnit : 'Pa', defDispUnit : 'bar',
			units : {'Pa' : {mult : 1}, 'kPa' : {mult : 1e3}, 'MPa' : {mult : 1e6}, 'GPa' : {mult : 1e9}, 
				'bar' : {mult : 1e5}, 'psi' : {mult : 6.89475e3}, 'ksi' : {mult : 6.89475e6}}},
		'Temperature' : {title : 'temperature', nominalValue : 273.15, SIUnit : 'K', 
			units : {'K' : {mult : 1}, 'degC' : {mult : 1, offset : 273.15}, 'degF' : {mult : 5./9, offset : 255.372}}},
		'Density' : {title : 'density', nominalValue : 1, SIUnit : 'kg/m**3', 
			units : {'kg/m**3' : {mult : 1}, 'g/L' : {mult : 1}, 'g/cm**3' : {mult : 1e3}}},
		'SpecificEnthalpy' : {title : 'specific enthalpy', nominalValue : 1e6, SIUnit : 'J/kg', defDispUnit : 'kJ/kg', 
			units : {'J/kg' : {mult : 1}, 'kJ/kg' : {mult : 1e3}}},
		'SpecificInternalEnergy' : {title : 'specific internal energy', nominalValue : 1e6, SIUnit : 'J/kg', defDispUnit : 'kJ/kg', 
			units : {'J/kg' : {mult : 1}, 'kJ/kg' : {mult : 1e3}}},
		'SpecificEntropy' : {title : 'specific entropy', nominalValue : 1, SIUnit : 'J/kg-K', defDispUnit : 'kJ/kg-K',
			units : {'J/kg-K' : {mult : 1}, 'kJ/kg-K' : {mult : 1e3}}},
		'VaporQuality' : {title : 'vapor quality', nominalValue : 1, SIUnit : '-', 
			units : {'-' : {mult : 1}}},
		'MassFlowRate' : {title : 'mass flow rate', nominalValue : 1, SIUnit : 'kg/s', 
			units : {'kg/s' : {mult : 1}, 'g/s' : {mult : 1e-3}, 'kg/min' : {mult : 1./60}, 'g/min' : {mult : 1e-3/60}, 
				'kg/h' : {mult : 1/3.6e3}, 'g/h' : {mult : 1e-3/3.6e3}}},
		'VolumetricFlowRate' : {title : 'volumetric flow rate', nominalValue : 1, SIUnit : 'm**3/s', 
			units : {'m**3/s' : {mult : 1}, 'm**3/h' : {mult : 1./3.6e3}, 'L/s' : {mult : 1e-3},
				'L/min' : {mult : 1e-3/60}, 'L/h' : {mult : 1e-3/3.6e3}}}
	};

	// Object for handling quantity
	var Quantity = function (quantity, value, unit, displayUnit) {
		this.quantity = quantity;
		unit = unit || units.quantities[this.quantity].SIUnit;
		this.displayUnit = displayUnit || units.quantities[this.quantity].defDispUnit || unit;
		
		var unitDef = units.quantities[this.quantity].units[unit];		
		var offset = unitDef.offset || 0;
		
		this.value = value * unitDef.mult + offset;		

		var dispUnitDef = units.quantities[this.quantity].units[this.displayUnit];
		offset = dispUnitDef.offset || 0;
		this.displayValue = (this.value - offset) / dispUnitDef.mult; 

		this.attachedVars = [];
	}

	Quantity.prototype.updateQuantity = function() {
		var dispUnitDef = units.quantities[this.quantity].units[this.displayUnit];
		var offset = 0;
		if ('offset' in dispUnitDef) {
			offset = dispUnitDef.offset;
		}
		this.value = this.displayValue * dispUnitDef.mult + offset ;
		for (var i = 0; i < this.attachedVars.length; i++) {
			this.attachedVars[i].value = this.value;
		}
	}
	Quantity.prototype.changeUnit = function() {
		var dispUnitDef = units.quantities[this.quantity].units[this.displayUnit];
		var offset = 0;
		if ('offset' in dispUnitDef) {
			offset = dispUnitDef.offset;
		}
		this.displayValue = (this.value - offset) / dispUnitDef.mult; 
	}
	Quantity.prototype.attachVar = function(variable) {
		variable.value = this.value;
		this.attachedVars.push(variable);
	}
	units.Quantity = Quantity;
	return units;
});

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

smoModule.directive('smoInputQuantity', ['$compile', 'util', 'units', function($compile, util, units) {
	return {
		restrict : 'A',
		scope : {
			smoQuantityVar: '=',
			title: '@smoTitle',
		},
	link : function(scope, element, attr) {
			scope.util = util;
			scope.units = units;

			var baseDivStyle = 'display: inline-block; white-space: nowrap;';
			var labelDivStyle = baseDivStyle + 'text-align: left; width: 150px; height: 30px;';
			var inputDivStyle = baseDivStyle + 'margin-left: 5px; margin-right: 5px;';
			var unitDivStyle = baseDivStyle + 'text-align: right;';
			var inputSize = 'width: 120px; height: 30px;';
			var unitSize = 'width: 80px; height: 30px;';

			var template = ' \
				<div style="' + labelDivStyle + '">' + scope.title + '</div> \
				<div style="' + inputDivStyle + '"> \
					<input style="' + inputSize + '" type="number" step="any" ng-init="smoQuantityVar.changeUnit()" ng-model="smoQuantityVar.displayValue" ng-change="smoQuantityVar.updateQuantity()">\
				</div> \
				<div style="' + unitDivStyle + '"> \
					<select style="' + unitSize + '" ng-model="smoQuantityVar.displayUnit" ng-options="name as name for (name, conv) in units.quantities[smoQuantityVar.quantity].units" ng-change="smoQuantityVar.changeUnit()"></select> \
				</div>' ;
			attr.$set('style', "margin-top: 5px; margin-bottom: 5px; white-space: nowrap;");
			element.html('').append($compile(template)(scope));
		}
	}
}]);

smoModule.directive('smoInputChoice', ['$compile', 'util', 'units', function($compile, util, units) {
	return {
		restrict : 'A',
		scope : {
			choiceVar: '=smoChoiceVar', 
			options: '=smoOptions',
			title: '@smoTitle',
		},
	link : function(scope, element, attr) {
		var template = ' \
		<div style="display: inline-block;text-align: left;width: 150px;">' + scope.title + '</div>\
		<div style="display: inline-block;"> \
			<select style="width: 209px; height: 30px; margin-left: 5px;" ng-model="choiceVar" ng-options="key as value.title for (key, value) in options"></select> \
		</div>';
		attr.$set('style', "margin-top: 5px; margin-bottom: 5px; white-space: nowrap;");
		element.html('').append($compile(template)(scope));

		}
	}
}]);


smoModule.directive('smoOutputQuantity', ['$compile', 'util', 'units', function($compile, util, units) {
	return {
		restrict : 'A',
		scope : {
			smoQuantityVar: '=',
			title: '@smoTitle',
		},
		link : function(scope, element, attr) {
			scope.util = util;
			scope.units = units;

			var baseDivStyle = 'display: inline-block; white-space: nowrap;';
			var labelDivStyle = baseDivStyle + 'text-align: left; width: 150px; height: 30px;';
			var outputDivStyle = baseDivStyle + 'margin-left: 5px; margin-right: 5px;';
			var unitDivStyle = baseDivStyle + 'text-align: right;';
			var outputStyle = baseDivStyle + 'width : 120px; height: 30px; border: 1px solid #888; padding: 1px;';
			var unitSize = 'width: 80px; height: 30px;';
			
			var template = ' \
				<div style="' + labelDivStyle + '">' + scope.title + '</div> \
				<div style="' + outputDivStyle + '"> \
					<div style="' + outputStyle + '" ng-bind="util.formatNumber(smoQuantityVar.displayValue)"></div>\
				</div> \
				<div style="' + unitDivStyle + '"> \
					<select style="' + unitSize + '" ng-model="smoQuantityVar.displayUnit" ng-options="name as name for (name, conv) in units.quantities[smoQuantityVar.quantity].units" ng-change="smoQuantityVar.changeUnit()"></select> \
				</div>';
			attr.$set('style', "margin-top: 5px; margin-bottom: 5px; white-space: nowrap;");
			element.html('').append($compile(template)(scope));
		}
	}
}]);

smoModule.directive('smoInputView', ['$compile', 'units', function($compile,  units) {
	return {
		restrict : 'A',
		scope : {
			smoDataSource : '='
		},
		controller: {
			
		}
		link : function(scope, element, attr) {
			scope.toJson = angular.toJson;
			scope.views = {};
			var groupFields = [];
			for (var i = 0; i < scope.smoDataSource.length; i++) {
				var group = scope.smoDataSource[i];
				var groupView = {};
				groupFields.push('<div display="inline-block;"><h3>' + group.name + '</h3>');
				for (var j = 0; j < group.fields.length; j++) {
					var field = group.fields[j];
					var fieldType = field.type || 'quantity';
					if (fieldType == 'quantity') {
						groupView[field.name] = new units.Quantity(field.quantity, field.value, field.unit);
						groupView[field.name].attachVar(field);
						groupFields.push('<div smo-input-quantity smo-quantity-var="views[\'' + group.name + '\'][\'' + field.name + '\']"' + 
							' smo-title="' + field.title + '"></div>');
					} else if (fieldType == 'choice') {
						groupFields.push('<div smo-input-choice smo-choice-var="smoDataSource[' + i + '].fields[' + j + '].value"' +
							' smo-options="smoDataSource[' + i + '].fields[' + j + '].options" smo-title="' + field.title + '"></div>');
//						groupFields.push('<div ng-bind="toJson(smoDataSource, true)"></div>');						
					}
				}
				scope.views[group.name] = groupView;
				groupFields.push('</div>');
			} 
			var template = groupFields.join("");
			element.html('').append($compile(template)(scope));
		}	
	}
}]);


smoModule.directive('smoResultView', ['$compile', 'units', function($compile,  units) {
	return {
		restrict : 'E',
		scope : {
			smoDataSource : '='
		},
		link : function(scope, element, attr) {
			scope.views = {};
			var groupFields = [];
			for (var i = 0; i < scope.smoDataSource.length; i++) {
				var group = scope.smoDataSource[i];
				var groupView = {};
				groupFields.push('<div class="col-md-5"><h3>' + group.name + '</h3>');
				for (var j = 0; j < group.fields.length; j++) {
					var field = group.fields[j];
					groupView[field.name] = new units.Quantity(field.quantity, field.value);
					groupFields.push('<div smo-output-quantity smo-quantity-var="views[\'' + group.name + '\'][\'' + field.name + '\']"' + 
					' smo-title="' + field.title + '"></div>');
				}
				scope.views[group.name] = groupView;
				groupFields.push('</div>');
			} 
			var template = groupFields.join("");
			element.html('').append($compile(template)(scope));
		}
	}
}]);
