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

