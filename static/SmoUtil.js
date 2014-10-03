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
