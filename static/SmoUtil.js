smoModule = angular.module('smo', []);

smoModule.factory('util', function util () {
			functions = {};
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
