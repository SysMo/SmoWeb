smoModule = angular.module('smo', []);

smoModule.factory('util', function util () {
	var functions = {};
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
	
	
	function serverExport (obj) {
		var csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
 		var form = $('<form action="' + obj.url + '" method="POST">' + 
						'<input type="hidden" name="csrfmiddlewaretoken" value="' + csrftoken + '">' +
						'<input type="hidden" name="exportOption" value="' + obj.exportOption + '">' +
						'<input type="hidden" name="data" value="' + obj.data + '">' +
					 '</form>');
		$('#' + obj.divID).append(form);
		form.submit();
		$('#' + obj.divID).empty();	
	}
	
	functions.formatNumber = formatNumber;
	functions.serverExport = serverExport;
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
	
	function parseJSON(source, reviver) {
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

smoModule.factory('communicator', function($http, $window, $timeout, $location, smoJson) {
	
	// Generic communicator
	function Communicator(url) {
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
	Communicator.prototype.setPostData = function(parameters) {
		this.postData = {
			parameters: parameters	
		};
	}
	Communicator.prototype.setResponseData = function(responseData) {
		this.data = responseData;
		this.dataReceived = true;
	}
	Communicator.prototype.fetchData = function(action, parameters, onSuccess, onFailure) {
		this.setPostData(parameters);
		this.loading = true;
		this.commError = false;
		this.serverError = false;
		this.dataReceived = false;
		this.errorMsg = "";
		this.stackTrace = "";
		// Initialize the communicator's data object if it does not exist
		if (typeof this.data === 'undefined') {
			this.data = {};
		}
		// Variable introduced so that success and error functions can access this object
		var communicator = this;
		this.onSuccess = onSuccess;
		this.onFailure = onFailure;
		$http({
	        method  : 'POST',
	        url     : this.url,
	        data    : {action : action, data: this.postData},
	        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
	        transformResponse: [smoJson.transformResponse]
	    })
	    .success(function(response) {
			communicator.loading = false;
			communicator.commError = false;
			if (!response.errStatus) {
				communicator.serverError = false;
				communicator.setResponseData(response.data);
				//communicator.dataReceived = true;
				if (typeof onSuccess !== 'undefined') {
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
	
	// Model communicator
	function ModelCommunicator(model, modelName, viewName, url) {
			this.model = model;
			this.modelName = modelName;
			this.viewName = viewName;
			Communicator.call(this, url);	
	}
	
	ModelCommunicator.prototype = Object.create(Communicator.prototype);

	ModelCommunicator.prototype.setPostData = function(parameters) {
		this.postData = {
			modelName: this.modelName,
			viewName: this.viewName,
			parameters: parameters
		};
	}
	
	ModelCommunicator.prototype.setResponseData = function(responseData) {
		var updateRecordId = function(comm) {
			if (comm.data.values.recordId) {
				comm.model.recordId = comm.data.values.recordId;
			}
		};
		
		if (responseData.keepDefaultDefs == false) {
			//If the definitions have been received once, on next occasions they are discarded
			if (this.data.definitions) {
				responseData.definitions = this.data.definitions;
			}
		}
		
		if (this.viewName == 'resultView') {
			var hdfFields = [];
			for (var i=0; i<responseData.definitions.length; i++) {
				for (var j=0; j<responseData.definitions[i].groups.length; j++) {
					if (responseData.definitions[i].groups[j].type == "ViewGroup") {
						for (var k=0; k<responseData.definitions[i].groups[j].fields.length; k++) {
							if (responseData.definitions[i].groups[j].fields[k].type == 'TableView' ||
								responseData.definitions[i].groups[j].fields[k].type == 'PlotView') {
								var field = responseData.definitions[i].groups[j].fields[k];
								if (field.useHdfData == true) {
									hdfFields.push({"name": field.name,
														"hdfFile": field.hdfFile, 
														"hdfGroup": field.hdfGroup, 
														"dataset": responseData.values[field.name],
														"datasetColumns": field.datasetColumns});
								}
							}
						}
					}
				}
			}
			
			if (hdfFields.length > 0) {
				var modelComm = this;
				var onFetchSuccess = function(comm) {
					for (var fieldName in comm.data) {
						responseData.values[fieldName] = angular.copy(comm.data[fieldName]);
					}
					Communicator.prototype.setResponseData.call(modelComm, responseData);
					updateRecordId(modelComm);
				}
				hdfDataComm = new Communicator();
				var onFail = function(comm) {
					console.log(comm);
				};
				hdfDataComm.fetchData('loadHdfValues', hdfFields, onFetchSuccess, onFail);
				return;
			}
		}
		
		Communicator.prototype.setResponseData.call(this, responseData);
		updateRecordId(this);	
	}
	
	ModelCommunicator.prototype.saveUserInput = function() {
		var communicator = this;
		this.saveFeedbackMsg = "";
		this.saveSuccess = false;
		this.setPostData(this.data.values);	
		$http({
	        method  : 'POST',
	        url     : this.url,
	        data    : {action: 'save', data: this.postData},
	        headers : { 'Content-Type': 'application/x-www-form-urlencoded' }, // set the headers so angular passing info as form data (not request payload)
	        transformResponse: [smoJson.transformResponse]
	    })
	    .success(function(response) {
			if (!response.errStatus) {
				var addressToParams;
				if ($location.$$html5){
					addressToParams = $location.protocol() + '://' + $location.host() + ':' 
					+ $location.port() + $location.path();
				} else {
					addressToParams = window.location;
				}
				
				communicator.savedRecordUrl = addressToParams
					+ '?model=' + response.data.model + '&view=' + response.data.view + '&id=' + response.data.id;
				communicator.saveSuccess = true;
				communicator.saveFeedbackMsg = "Input data saved.";
			} else {
				communicator.saveFeedbackMsg = "Failed to save input data";
			}
	    })
	    .error(function(response) {
	    	communicator.saveFeedbackMsg = "Failed to save input data";
	    });
	}
	
	// Asynchronous model communicator
	function AsyncModelCommunicator(model, modelName, viewName, url) {
		this.progressBarDivID = modelName + '_' + viewName + 'ProgressBar';
		this.onFetchSuccess = function(comm) {
			comm.loading = true;
			comm.dataReceived = false;
			//angular.element('#' + this.modelName + '_abortButton').prop('disabled', true);
		}
		ModelCommunicator.call(this, model, modelName, viewName, url);
	}
	
	AsyncModelCommunicator.prototype = Object.create(ModelCommunicator.prototype);
	
	AsyncModelCommunicator.prototype.computeAsync = function(parameters) {
		this.current = 0;
		$('#' + this.modelName + '_computeButton').prop('disabled', true);
		this.fetchData('startCompute', parameters, this.onFetchSuccess);
	}
	
	AsyncModelCommunicator.prototype.abortAsync = function() {
		var onFetchSuccess = function(comm) {
			comm.loading = true;
			comm.dataReceived = false;
			$('#' + this.modelName + '_computeButton').prop('disabled', false);
		}
		if (this.jobID) {
			this.fetchData('abort', {"jobID" : this.jobID}, onFetchSuccess);
		}
	}
	
	AsyncModelCommunicator.prototype.checkProgress = function() {
		var comm = this;
		setTimeout(function(){
			comm.fetchData('checkProgress', {"jobID" : comm.jobID}, comm.onFetchSuccess);
		}, 1000);
	}
	
	AsyncModelCommunicator.prototype.setResponseData = function(responseData) {
		if (responseData.jobID) {
			this.jobID = responseData.jobID;
		}
		if (responseData.fractionOutput) {
			this.fractionOutput = responseData.fractionOutput;
		}
		if (responseData.suffix) {
			this.suffix = responseData.suffix;
		}
		
		this.state = responseData.state;
		if (typeof this.state !== 'undefined') {
			if (this.state == 'PENDING') {
				this.checkProgress();
			}
			if (this.state == 'STARTED') {
				this.current = 0;
				this.total = 1.;
				this.checkProgress();
			} else if (this.state =='PROGRESS') {
				this.current = responseData.current;
				this.total = responseData.total;
				this.checkProgress();
			} else if (this.state == 'SUCCESS') {
				$('#' + this.modelName + '_computeButton').prop('disabled', false);
				this.onSuccess = function(comm) {};
				ModelCommunicator.prototype.setResponseData.call(this, responseData);
			} else if (this.state == 'FAILURE') {
			} else if (this.state == 'REVOKED') {
			}
		} else {
			ModelCommunicator.prototype.setResponseData.call(this, responseData);
		}
	}

	return {"Communicator": Communicator, "ModelCommunicator": ModelCommunicator, 
			"AsyncModelCommunicator": AsyncModelCommunicator}
})


smoModule.factory('quantities', ['util', function(util) {
	var quantities = {};
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
	quantities.Quantity = Quantity;
	return quantities;
}]);

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

smoModule.directive('tooltip', function(){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){
            $(element).hover(function(){
                // on mouseenter
                $(element).tooltip('show');
            }, function(){
                // on mouseleave
                $(element).tooltip('hide');
            });
        }
    };
});

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
			var template = '<img class="smo-button" src="/static/icons/' + icon + '.png" ng-click="' + action + '" width="' + width + 'px" data-toggle="tooltip" title="' + tooltip + '" tooltip>';
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.replaceWith(el);
	        compiled(scope);

		}
	};
}]);

smoModule.directive('smoImg', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			smoDataSource : '=',
			modelName: '@modelName'
		},
		link : function(scope, element, attr) {
			var el_id = scope.modelName + '_' + scope.fieldVar.name;
			var template;
			if (scope.fieldVar.width == null || scope.fieldVar.height == null) {
				template = '<img class="img-responsive" id="' + el_id + '" style="cursor: pointer; width=100%; height=100%;" src="/' + scope.smoDataSource[scope.fieldVar.name] + '">';
			} else {
				template = '<img class="img-responsive" id="' + el_id + '" width=' + scope.fieldVar.width + ' height=' + scope.fieldVar.height +
				' style="cursor: pointer;" src="/' + scope.smoDataSource[scope.fieldVar.name] + '">';
			}
			var el = angular.element(template);
			compiled = $compile(el);
			element.replaceWith(el);
			compiled(scope);
			$("#" + el_id).click(function(){
				var URL = $(this).attr("src");
				window.open(URL, '_blank');
			});
		}
	}
}]);

smoModule.directive('smoInt', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			viewType: '@viewType',
			smoDataSource : '='
		},
		link : function(scope, element, attr) {
			var template = '\
				<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>';
			if (scope.viewType == 'input') {
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input style="width:' + scope.fieldVar.inputBoxWidth + 'px" name="input" required type="number" ng-model="smoDataSource.' + scope.fieldVar.name + '" min="' + scope.fieldVar.minValue + '" max="' + scope.fieldVar.maxValue + '">\
						</div>\
					</div>';
			}
			else if (scope.viewType == 'output') {
				template += '\
					<div class="field-output"> \
						<div class="output" ng-bind="smoDataSource.' + scope.fieldVar.name + '"></div>\
					</div>';		
			}	
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
}]);

smoModule.directive('smoComplex', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			viewType: '@viewType',
			smoDataSource : '='
		},
		controller: function($scope) {
			$scope.Math = window.Math;
		},
		link : function(scope, element, attr) {
			var template = '\
				<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>';
			if (scope.viewType == 'input') {
				template += '\
					<div style="margin-left: 5px; display:inline-block;"> \
						<div style ="width:5px; height: 30px; text-align: center; font-size: 120%; display: inline-block;" >(</div>\
						<div style="display: inline-block;" ng-form name="' + scope.fieldVar.name + 'RealForm">\
							<input style="width:90px; height: 30px; name="input" required type="text" \
								ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" \
								ng-model="smoDataSource.' + scope.fieldVar.name + '[0]"> \
						</div>\
					</div>\
					<div style="display:inline-block;"> \
						<div style="display: inline-block;" ng-form name="' + scope.fieldVar.name + 'ImagForm">\
							<input style="width:90px; height: 30px; name="input" required type="text" \
								ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" \
								ng-model="smoDataSource.' + scope.fieldVar.name + '[1]"> \
						</div>\
						<div style ="width:10px; height: 30px; text-align: center; display: inline-block;"><span>j</span><span style="margin-left: 2px; font-size: 120%;">)</span></div>\
					</div>';
			}
			else if (scope.viewType == 'output') {
				template += '\
					<div class="field-output"> \
						<div class="output">\
							<span>(</span>\
							<span ng-bind="smoDataSource.' + scope.fieldVar.name + '[0]"></span>\
							<span ng-show="smoDataSource.' + scope.fieldVar.name + '[1]>=0">+</span>\
							<span ng-show="smoDataSource.' + scope.fieldVar.name + '[1]<0">-</span>\
							<span>{{Math.abs(smoDataSource.' + scope.fieldVar.name + '[1])}}j</span>\
							<span>)</span>\
						</div>\
					</div>';		
			}
			
			if (scope.viewType == 'input') {
				template += '\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'RealForm.input.$error.pattern">Enter a number</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'RealForm.input.$error.required">Required value</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'ImagForm.input.$error.pattern">Enter a number</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'ImagForm.input.$error.required">Required value</div>';
			}
			
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
		}
	}
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
				<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>';
			if (scope.viewType == 'input'){
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input name="input" style="width:' + scope.fieldVar.inputBoxWidth + 'px" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" ng-model="fieldVar.displayValue" ng-change="checkValueValidity();">\
						</div>\
					</div>';
				template += '\
					<div ng-hide="fieldVar.quantity==\'Float\'" class="field-select quantity"> \
						<select ng-disabled="!' + scope.fieldVar.name + 'Form.$valid" ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
				
			}
			else if (scope.viewType == 'output'){
				template += '\
					<div class="field-output"> \
						<div class="output" ng-bind="fieldVar.displayValue"></div>\
					</div>';
				template += '\
					<div ng-hide="fieldVar.quantity==\'Float\'" class="field-select quantity"> \
						<select ng-model="fieldVar.displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.units" ng-change="changeUnit()"></select> \
					</div>';
				
			}
			if (scope.viewType == 'input')
				template += '\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.pattern">Enter a number</div>\
					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.required">Required value</div>';
				if (scope.fieldVar.quantity == 'Dimensionless') {
					template += '\
						<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.minVal">Value should be above {{util.formatNumber(fieldVar.minDisplayValue)}}</div>\
						<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.maxVal">Value should be below {{util.formatNumber(fieldVar.maxDisplayValue)}}</div>';
				} else {
					template += '\
						<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.minVal">Value should be above {{util.formatNumber(fieldVar.minDisplayValue)}} {{fieldVar.displayUnit}}</div>\
						<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.maxVal">Value should be below {{util.formatNumber(fieldVar.maxDisplayValue)}} {{fieldVar.displayUnit}}</div>';
				}
				
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
				<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>\
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
					<div class="multiline-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>';
			} else {
				var template = '\
					<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>';
			}			
			
			if (scope.viewType == 'input')
				template += '\
					<div class="field-input"> \
						<div ng-form name="' + scope.fieldVar.name + 'Form">\
							<input style="width:' + scope.fieldVar.inputBoxWidth + 'px" name="input" type="text" ng-model="fieldVar.value" ng-change="updateValue()" data-toggle="tooltip" title="{{fieldVar.value}}" tooltip>\
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
//			if (scope.viewType == 'input')
//				template += '\
//					<div class="input-validity-error" ng-show="' + scope.fieldVar.name + 'Form.input.$error.required">Required value</div>';

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
				<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.fieldVar.description + '" tooltip>' + scope.fieldVar.label + '</div></div>';			
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

smoModule.directive('smoDataSeriesView', ['$compile', 'communicator', 'util', function($compile, communicator, util) {
	return {
		restrict : 'A',
		scope : {
			fieldVar: '=',
			smoDataSource : '=',
			modelName: '@modelName'
		},
		
		controller: function($scope) {
			var setTableView = function(){
				//Setting the visible columns of a table based on the visibility controls
				$scope.fieldVar.visibleColumns = [];
				for (i=0; i<$scope.numCols; i++){
					if ($scope.columnsShow[i] == true){
						$scope.fieldVar.visibleColumns.push(i);
					}
				}
				$scope.displayTable = angular.copy($scope.displayValues);
				$scope.displayTable.unshift($scope.labels);
				$scope.dataTable = google.visualization.arrayToDataTable($scope.displayTable);
				$scope.dataView = new google.visualization.DataView($scope.dataTable);
				$scope.dataView.setColumns($scope.fieldVar.visibleColumns);
			}
			
			var setPlotView = function() {
				//Setting the visibile portion of data of a plot based on the visibility controls
				$scope.viewData = [];
				for (var i=0; i<$scope.numRows; i++) {
					var row = [];
					for (var j=0; j<$scope.numCols; j++){
						if ($scope.columnsShow[j] == true){
							row.push($scope.displayValues[i][j]);
						}
					}
					$scope.viewData[i] = row;
				}
				
				//Selecting the corresponding labels and changing the 'definitions' object to remember visibility
				$scope.options = angular.copy($scope.fieldVar.options);
				$scope.fieldVar.visibleColumns = [];
				var viewLabels = [];
				for (var j=0; j<$scope.numCols; j++) {
					if ($scope.columnsShow[j] == true){
						viewLabels.push($scope.labels[j]);
						$scope.fieldVar.visibleColumns.push(j);
					}
				}
				$scope.options.labels = viewLabels;
				
				if ($scope.options.labels.length == 2)
					$scope.options.ylabel = $scope.options.ylabel || $scope.options.labels[1];
				
				$scope.options.xlabel = $scope.options.labels[0];			
			}
			
			var plotData = function() {
				$scope.options.labelsDiv = $scope.modelName + '_' + $scope.fieldVar.name + 'LegendDiv';
				$scope.options.legend = 'always';
				$scope.options.hideOverlayOnMouseOut = false;
				$scope.chart = new Dygraph(document.getElementById($scope.modelName + '_' + $scope.fieldVar.name + 'PlotDiv'), 
						$scope.viewData,
						$scope.options);
			}
			
			var drawTable = function() {
				//Drawing the table
				var tableView 
					= new google.visualization.Table(document.getElementById($scope.modelName + '_' + $scope.fieldVar.name + 'TableDiv'));
				
				if(typeof $scope.fieldVar.options.formats === 'string'){
					for (var i=0; i < $scope.numCols; i++){
						formatter = new google.visualization.NumberFormat({pattern: $scope.fieldVar.options.formats});
						formatter.format($scope.dataTable, i);
					}
				} else {
					for (var i=0; i < $scope.numCols; i++){
						try {
							formatter = new google.visualization.NumberFormat({pattern: $scope.fieldVar.options.formats[i], groupingSymbol : ''});
						}
						catch(err) {
							formatter = new google.visualization.NumberFormat({groupingSymbol : ''});
						}
						
						formatter.format($scope.dataTable, i);
					}
				}
				
				var drawOptions;
				//GViz fix for IE, relying on global variable isIE. Pagination of tables in IE leads to "Invalid argument" error 
				if (isIE == true)
					drawOptions = {showRowNumber: true, sort:'disable'}
				else
					drawOptions = {showRowNumber: true, sort:'disable', page:'enable', pageSize:14}
				
				tableView.draw($scope.dataView, drawOptions);
			}
			
			var exportCSV = function() {
				var exportTable = $scope.dataView.toDataTable();		
				var labels = [];
				for (var i=0; i<exportTable.getNumberOfColumns(); i++){
					labels.push(exportTable.getColumnLabel(i));
				}
				var labelsString = labels.join(",");
				var csvString = labelsString + "\n";
				
				var dataTableCSV = google.visualization.dataTableToCsv(exportTable);
				csvString += dataTableCSV;
				
				var link = document.getElementById($scope.modelName + '_' + $scope.fieldVar.name + 'CsvElem');
			 	if (link.download === undefined) { 
			 		//if HTML5 download attribute is not supported, 
			 		//perform server-side export
			 		obj = {
			 				url: "/SmoWebBase/Export",
			 				exportOption: "csv",
			 				data: csvString,
			 				divID: $scope.modelName + '_' + $scope.fieldVar.name + 'FormDiv'
			 		}
			 		util.serverExport(obj);
			 		
			 	} else {
			 		// download stuff
				 	var blob = new Blob([csvString], {
				 	  "type": "text/csv;charset=utf8;"			
				 	});
			 		link.setAttribute("href", window.URL.createObjectURL(blob));
			 		link.setAttribute("download", $scope.fileName);
			 		link.click();
			 	}
			} 
			
			var exportPNG = function(){
				var img = document.getElementById($scope.modelName + '_' + $scope.fieldVar.name + 'Img');
				Dygraph.Export.asPNG($scope.chart, img);
			 	window.open(img.src, '_blank');
			}
			
			if ($scope.fieldVar.type == 'TableView') {
				$scope.setDataView = setTableView;
				$scope.draw = drawTable;
				$scope.exportData = exportCSV;
				$scope.fileName = $scope.fieldVar.name + '.csv';
			}
			else if ($scope.fieldVar.type == 'PlotView') {
				$scope.setDataView = setPlotView;
				$scope.draw = plotData;
				$scope.exportData = exportPNG;
				$scope.fileName = $scope.fieldVar.name + '.png';
			}
			
			$scope.setToAll = function() {
				var i;
				if ($scope.fieldVar.type == 'PlotView') {
					i = 1;
				} else if ($scope.fieldVar.type == 'TableView') {
					i = 0;
				}
				for (i; i<$scope.numCols; i++) {
					$scope.columnsShow[i] = $scope.allChecked;
				}
			}
			
			$scope.updateChecked = function() {
				var i;
				if ($scope.fieldVar.type == 'PlotView') {
					$scope.columnsShow[0] = true;
					i = 1;
				} else if ($scope.fieldVar.type == 'TableView') {
					i = 0;
				}
				for (i; i<$scope.numCols; i++) {
					if ($scope.columnsShow[i] == false) {
						$scope.allChecked = false;
						return;
					}
				}
				$scope.allChecked = true;
			}	

//Common functionality			
			$scope.expanded = false;
			$scope.toggle = function(){
				$scope.expanded = !$scope.expanded;
				if ($scope.expanded == false){
					$scope.setDataView();
					$scope.draw();
				}
			}
			
			$scope.changeUnit = function(col) {
				var field = $scope.fieldVar.fields[col];
				
				for (var i=0; i<field.units.length; i++) {
					if (field.displayUnit == field.units[i][0]){
						field.dispUnitDef = field.units[i][1];
					}	
				}
				
				var offset = 0;
				if ('offset' in field.dispUnitDef) {
					offset = field.dispUnitDef.offset;
				}
				
				for (var row=0; row<$scope.numRows; row++){
					$scope.displayValues[row][col]
						= ($scope.values[row][col] - offset) / field.dispUnitDef.mult;
				}
				
				$scope.labels[col] = $scope.fieldVar.labels[col] + ' [' + field.displayUnit + ']';
			}
			
			$scope.init = function() {
				$scope.values = $scope.smoDataSource[$scope.fieldVar.name];
				$scope.displayValues = angular.copy($scope.values);
				$scope.labels = angular.copy($scope.fieldVar.labels);
				
				$scope.numCols = $scope.values[0].length;
				$scope.numRows = $scope.values.length;
				
				for (var col=0; col<$scope.numCols; col++){
					var field = $scope.fieldVar.fields[col];
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
					
					for (var row=0; row<$scope.numRows; row++){
						$scope.values[row][col]
							= $scope.values[row][col] * field.unitDef.mult + unitOffset;
						
						$scope.displayValues[row][col] 
							= ($scope.values[row][col] - dispUnitOffset) / field.dispUnitDef.mult;
					}
					
					$scope.labels[col] 
						= $scope.fieldVar.labels[col] + ' [' + field.displayUnit + ']';
				}
				
				//Determining number of rows in edit mode
				var numEditRows;
				if ($scope.numCols % 5){
					numEditRows = Math.floor($scope.numCols / 5) + 1;
				} else {
					numEditRows = Math.floor($scope.numCols / 5);
				}
				$scope.editRows = [];
				for (var i=0; i<numEditRows; i++){
					$scope.editRows.push(i);
				}
				
				//Setting initial visibility
				$scope.columnsShow = [];
				for (var i; i<$scope.numCols; i++) {
					$scope.columnsShow[i] = false;
				}
				for (var i=0; i<$scope.fieldVar.visibleColumns.length; i++) {
					$scope.columnsShow[$scope.fieldVar.visibleColumns[i]] = true;
				}
				if ($scope.fieldVar.visibleColumns.length == $scope.numCols) {
					$scope.allChecked = true;
				} else {
					$scope.allChecked = false;
				}
				
				$scope.setDataView();
				$scope.draw();
			}
			
		},
		link : function(scope, element, attr) {
			var template = '\
				<div style="margin-bottom: 5px; text-align: left;">\
					<smo-button action="toggle()" icon="settings" tip="Settings" size="md"></smo-button>\
					<smo-button icon="save" size="md" action="exportData()" tip="Save"></smo-button>\
				</div>';
			
			if (scope.fieldVar.type == 'TableView')
				template += '<div id="' + scope.modelName + '_' + scope.fieldVar.name + 'TableDiv"></div>';
			else if (scope.fieldVar.type == 'PlotView')
				template += '\
					<div style="display: inline-block;">\
						<div id="' + scope.modelName + '_' + scope.fieldVar.name + 'PlotDiv"></div>\
					</div>\
					<div style="margin-left: 55px; margin-top: 10px;">\
						<div id="' + scope.modelName + '_' + scope.fieldVar.name + 'LegendDiv"></div>\
					</div>';
			
			template += '\
			<div style = "margin-top: 10px; margin-bottom: 10px;">\
				<a id="' + scope.modelName + '_' + scope.fieldVar.name + 'CsvElem" hidden></a>\
				<img id="' + scope.modelName + '_' + scope.fieldVar.name + 'Img" hidden>\
				<a id="' + scope.modelName + '_' + scope.fieldVar.name + 'PngElem" hidden></a>\
				<div id="' + scope.modelName + '_' + scope.fieldVar.name + 'FormDiv" hidden></div>\
				<div class="view-edit" ng-show="expanded" ng-click="toggle()">\
					<table class="nice-table" style="border: none;">\
						<tr>\
							<th style="min-width: 10px;" colspan="5">\
								<input type="checkbox" ng-model="allChecked" ng-change="setToAll()"></input>\
								<span>All</span>\
							</th>\
						</tr>\
						<tr ng-repeat="row in editRows">\
							<td style="min-width: 10px;" ng-repeat="label in fieldVar.labels.slice(row*5, row*5+5) track by $index">\
								<input type="checkbox" ng-model="columnsShow[row*5 + $index]" ng-change="updateChecked()"></input>\
								<span ng-bind="label"></span>\
								<div class="field-select quantity">\
									<select ng-model="fieldVar.fields[row*5 + $index].displayUnit" ng-options="pair[0] as pair[0] for pair in fieldVar.fields[row*5 + $index].units" ng-change="changeUnit(row*5 + $index)"></select>\
								</div>\
							</td>\
							<td ng-if="$last && $index>0 && fieldVar.labels.slice(row*5, row*5+5).length<5" colspan="{{5 - fieldVar.labels.slice(row*5, row*5+5).length}}">\
							</td>\
						</tr>\
					</table>\
				</div>\
			</div>';
				
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope); 
	        $(".view-edit > table").bind('click', function(e){
                e.stopPropagation();
            });
	        if (scope.fieldVar.type == 'PlotView') {
	        	$("#" + scope.fieldVar.name + "Tab").on('click', function(){
		        	scope.draw();
		        });
	        }
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
			dataSource : '=smoDataSource',
			viewType: '@viewType'
		},
		link : function(scope, element, attr) {
			// Passing values from dataSourceRoot if such property exists in a field-group
			if (typeof scope.smoFieldGroup.dataSourceRoot !== 'undefined') {
				scope.smoDataSource = scope.dataSource[scope.smoFieldGroup.dataSourceRoot];
			} else {
				scope.smoDataSource = scope.dataSource;

			}
			scope.fields = {};
			var groupFields = [];
			for (var i = 0; i < scope.smoFieldGroup.fields.length; i++) {
				var field = scope.smoFieldGroup.fields[i];
				scope.fields[field.name] = field;
				var showCode = "";
				if (typeof field.show !== "undefined"){
					showCode = 'ng-show="' + field.show.replace(/self/g, 'smoDataSource') + '"';
				}
				if (field.type == 'Quantity') {
					field.value = scope.smoDataSource[field.name];
					field.id = field.name;
					
					// Attach the field value to the quantity so that the original value is updated when the quantity value changes
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showCode + ' smo-quantity view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showCode + ' smo-quantity view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'Integer') {
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showCode + ' smo-int view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showCode + ' smo-int view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'Choices') {
					if (scope.viewType == 'input')
						groupFields.push('<div ' + showCode + ' smo-choice field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'String') {
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showCode + ' smo-string view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showCode + ' smo-string view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'Boolean') {
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showCode + ' smo-bool view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showCode + ' smo-bool view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'RecordArray') {
						groupFields.push('<div ' + showCode + ' smo-record-array="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} else if (field.type == 'Complex') {
					if (scope.viewType == 'input') 
						groupFields.push('<div ' + showCode + ' smo-complex view-type="input" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
					if (scope.viewType == 'output')
						groupFields.push('<div ' + showCode + ' smo-complex view-type="output" field-var="fields.' + field.name + '" smo-data-source="smoDataSource"></div>');
				} 	
			}
			
			var template = "";
			
			if (scope.smoFieldGroup.label) {
				template += '<div ng-hide="' + scope.smoFieldGroup.hideContainer + '" class="field-group-label" style="margin-top: 25px;">' + scope.smoFieldGroup.label + '</div>';	
			} 
			
			if (scope.smoFieldGroup.hideContainer) {
				var style = "background-color: transparent; border: none;";
			} else {
				style = "";
			}
			
			template += '<div style="' + style + '" class="field-group-container">';
			
			template += groupFields.join("") + '</div>';

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
			dataSource : '=smoDataSource',
			modelName: '@modelName'
		},
		link : function(scope, element, attr) {
			// Passing values from dataSourceRoot if such property exists in a view-group
			if (typeof scope.smoViewGroup.dataSourceRoot !== 'undefined') {
				scope.smoDataSource = scope.dataSource[scope.smoViewGroup.dataSourceRoot];
			} else {
				scope.smoDataSource = scope.dataSource;
			}
			
			var template = "";
			if (scope.smoViewGroup.label) {
				template += '<div ng-hide="' + scope.smoViewGroup.hideContainer + '" class="field-group-label" style="margin-top: 25px;">' + scope.smoViewGroup.label + '</div>';
			}
			
			
			if (scope.smoViewGroup.fields.length > 1) {
				var navPills = [];
				var navPillPanes = [];
				scope.fields = {};
				
				for (var i = 0; i < scope.smoViewGroup.fields.length; i++) {
					var field = scope.smoViewGroup.fields[i];
					scope.fields[field.name] = field;
					var showCode = "";
					if (typeof field.show !== "undefined"){
						showCode = 'ng-show="' + field.show.replace(/self/g, 'smoDataSource') + '"';
					}
					
					
					if (i==0){
						navPills.push('<li class="active"><a id="' + field.name + 'Tab" data-target="#' + field.name + '" role="tab" data-toggle="tab"><div data-toggle="tooltip" data-viewport="[smo-view-group]" title="' + field.description + '" tooltip>' + field.label + '</div></a></li>');
						navPillPanes.push('<div class="tab-pane active" id="' + field.name + '">');
					} else {
						navPills.push('<li><a id="' + field.name + 'Tab" data-target="#' + field.name + '" role="tab" data-toggle="tab"><div data-toggle="tooltip" data-viewport="[smo-view-group]", title="' + field.description + '" tooltip>' + field.label + '</div></a></li>');
						navPillPanes.push('<div class="tab-pane" id="' + field.name + '">');
					}
					
					if (field.type == 'TableView' || field.type == 'PlotView') {
						navPillPanes.push('<div ' + showCode + ' smo-data-series-view field-var="fields.' + field.name + '" model-name="' + scope.modelName + '" smo-data-source="smoDataSource"></div>');
					} else if (field.type == 'Image' || field.type == 'MPLPlot') {
						navPillPanes.push('<div ' + showCode + ' smo-img field-var="fields.' + field.name + '" model-name="' + scope.modelName + '" smo-data-source="smoDataSource"></div>');
					}
					
					navPillPanes.push('</div>'); 
					
				}
				
				if (scope.smoViewGroup.hideContainer) {
					var style = "background-color: transparent; border: none;";
				} else {
					style = "";
				}
				
				template += '\
						<div class="view-group-container" style="' + style + '">\
							<div style="vertical-align: top; cursor: pointer; margin-bottom: 10px;">\
								<ul class="nav nav-pills nav-stacked">' + navPills.join("") + '</ul>\
							</div>\
							<div class="tab-content" style="overflow-x:auto;">'
								+ navPillPanes.join("") + 
							'</div>\
						</div>';
				
			} else if (scope.smoViewGroup.fields.length == 1) {
				var field = scope.smoViewGroup.fields[0];
				var showCode = "";
				if (typeof field.show !== "undefined"){
					showCode = 'ng-show="' + field.show.replace(/self/g, 'smoDataSource') + '"';
				}
				
				
				if (scope.smoViewGroup.hideContainer) {
					var style = "background-color: transparent; border: none;";
				} else {
					style = "background-color: white; padding :10px; text-align: center;";
				}
				
				template += '<div style="' + style + '">';
				
				if (field.type == 'TableView' || field.type == 'PlotView') {
					template += '<div ' + showCode + ' smo-data-series-view field-var="smoViewGroup.fields[0]" model-name="' + scope.modelName + '" smo-data-source="smoDataSource"></div>';
				} else if (field.type == 'Image' || field.type == 'MPLPlot') {
					template += '<div ' + showCode + ' smo-img field-var="smoViewGroup.fields[0]" model-name="' + scope.modelName + '" smo-data-source="smoDataSource"></div>';
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

smoModule.directive('smoSuperGroup', ['$compile', function($compile) {
	return {
		restrict : 'A',
		scope : {
			smoSuperGroup : '=',
			dataSource : '=smoDataSource',
			modelName: '@modelName',
			viewType: '@viewType'
		},
		link : function(scope, element, attr) {
				// Passing values from dataSourceRoot if such property exists in a view-group
				if (typeof scope.smoSuperGroup.dataSourceRoot !== 'undefined') {
					scope.smoDataSource = scope.dataSource[scope.smoSuperGroup.dataSourceRoot];
				} else {
					scope.smoDataSource = scope.dataSource;
				}
				
				var template = "";
				for (var j = 0; j < scope.smoSuperGroup.groups.length; j++) {
					var group = scope.smoSuperGroup.groups[j];
					var showCode = "";
					if (typeof group.show !== "undefined") {
						showCode = 'ng-show="' + group.show.replace(/self/g, 'smoDataSource') + '"';
					}
					if (group.type == 'FieldGroup') {
						template += '<div ' + showCode + ' smo-field-group="smoSuperGroup.groups[' + j + ']" view-type="' + scope.viewType + '" smo-data-source="smoDataSource"></div>';
					} else if (group.type == 'ViewGroup') {
						template += '<div ' + showCode + ' smo-view-group="smoSuperGroup.groups[' + j + ']" model-name="' + scope.modelName + '" smo-data-source="smoDataSource"></div>';
					}					
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
					
					var showCode = "";
					if (typeof superGroup.show !== "undefined"){
						showCode = 'ng-show="' + superGroup.show.replace(/self/g, 'smoDataSource') + '"';
					}
					
					if (i==0){
						navTabs.push('<li ' + showCode + ' class="active"><a id="' + scope.modelName + superGroup.name + 'Tab" data-target="#' + scope.modelName + superGroup.name + '" role="tab" data-toggle="tab">' + superGroup.label + '</a></li>');
						navTabPanes.push('<div ' + showCode + ' class="tab-pane active" id="' + scope.modelName + superGroup.name + '">');
					} else {
						navTabs.push('<li ' + showCode + '><a id="' + scope.modelName + superGroup.name + 'Tab" data-target="#' + scope.modelName + superGroup.name + '" role="tab" data-toggle="tab">' + superGroup.label + '</a></li>');
						navTabPanes.push('<div ' + showCode + ' class="tab-pane" id="' + scope.modelName + superGroup.name + '">');
					}
					
					navTabPanes.push('<div smo-super-group="smoSuperGroupSet[' + i + ']" model-name="' + scope.modelName + '" view-type="' + scope.viewType + '" smo-data-source="smoDataSource"></div>');
					navTabPanes.push('</div>');
				}
				
				var template = '<ul class="nav nav-tabs" role="tablist">' +
									navTabs.join("") + 
								'</ul>' +
								'<div class="tab-content super-group">' + 
									navTabPanes.join("") + 
								'</div>';
			} else if (scope.smoSuperGroupSet.length == 1) {
				var showCode = "";
				if (typeof scope.smoSuperGroupSet[0].show !== "undefined"){
					showCode = 'ng-show="' + scope.smoSuperGroupSet[0].show.replace(/self/g, 'smoDataSource') + '"';
				}
				var template = '<div class="super-group" ' + showCode + '>\
									<div smo-super-group="smoSuperGroupSet[0]" model-name="' + scope.modelName + '" view-type="' + scope.viewType + '" smo-data-source="smoDataSource"></div>\
								</div>';
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
			if ($scope.smoRecordArray.toggle == true) {
				$scope.expanded = false;
				$scope.toggle = function(){
					$scope.expanded = !$scope.expanded;
				}
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
				
				$scope.defaultDisplayRow[col]
					= util.formatNumber(($scope.smoRecordArray.defaultRow[col] - offset) / field.dispUnitDef.mult);
				
				field.minDisplayValue = (field.minValue - offset) / field.dispUnitDef.mult;
				field.maxDisplayValue = (field.maxValue - offset) / field.dispUnitDef.mult;
			}
			
			$scope.addRow = function(row) {
				if (row == -1) {
					$scope.smoDataSource[$scope.smoRecordArray.name].unshift(angular.copy($scope.smoRecordArray.defaultRow));
					$scope.arrDisplayValue.unshift(angular.copy($scope.defaultDisplayRow));
					return;
				}
				$scope.smoDataSource[$scope.smoRecordArray.name].splice(row, 0, 
						angular.copy($scope.smoDataSource[$scope.smoRecordArray.name][row]));
				$scope.arrDisplayValue.splice(row, 0, 
						angular.copy($scope.arrDisplayValue[row]));
			}
			
			$scope.delRow = function(row) {
				if ($scope.smoDataSource[$scope.smoRecordArray.name].length == 1) {
					if ($scope.smoRecordArray.empty == false) {
						return;
					}
				}
				$scope.smoDataSource[$scope.smoRecordArray.name].splice(row, 1);
				$scope.arrDisplayValue.splice(row, 1);
			}
			
		},
		link : function(scope, element, attr) {
			scope.util = util;
			if (typeof scope.smoRecordArray.description === "undefined"){
				scope.smoRecordArray.description = "";
			}
			
			scope.arrValue = scope.smoDataSource[scope.smoRecordArray.name];
			scope.arrDisplayValue = angular.copy(scope.arrValue);
			scope.defaultDisplayRow = angular.copy(scope.smoRecordArray.defaultRow);
			
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
								<div ng-hide="smoRecordArray.fields[' + String(col) + '].quantity==\'Float\'" class="field-select quantity"> \
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
						
						scope.defaultDisplayRow[col]
							= util.formatNumber((scope.smoRecordArray.defaultRow[col] - dispUnitOffset) / field.dispUnitDef.mult);
					}
					
					field.minDisplayValue = (field.minValue - dispUnitOffset) / field.dispUnitDef.mult;
					field.maxDisplayValue = (field.maxValue - dispUnitOffset) / field.dispUnitDef.mult;
					
					rowTemplate += '\
						<td>\
							<div class="field-input">\
								<div ng-form name="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form">\
									<input style="width:' + field.inputBoxWidth + 'px" name="input" required type="text" ng-pattern="/^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$/" \
										ng-model="arrDisplayValue[i][' + String(col) + ']" ng-change="checkValueValidity(i,' + String(col) + ', ' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form)">\
								</div>\
							</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.pattern">Enter a number</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.required">Required value</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.minVal">Value should be above ' + util.formatNumber(scope.smoRecordArray.fields[col].minDisplayValue) + ' ' + scope.smoRecordArray.fields[col].displayUnit + '</div>\
							<div style="margin-left: 5px; color:red;" ng-show="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form.input.$error.maxVal">Value should be below ' + util.formatNumber(scope.smoRecordArray.fields[col].maxDisplayValue) + ' ' + scope.smoRecordArray.fields[col].displayUnit + '</div>\
						</td>';
					
				} else if (field.type == 'Integer') {
					rowTemplate += '\
						<td>\
							<div class="field-input">\
								<div ng-form name="' + scope.smoRecordArray.name + '_{{i}}_' + String(col) + 'Form">\
									<input style="width:' + field.inputBoxWidth + 'px" name="input" required type="number" \
										ng-model="arrValue[i][' + String(col) + ']" \
										min="' + scope.smoRecordArray.fields[col].minValue + '" max="' + scope.smoRecordArray.fields[col].maxValue + '">\
								</div>\
							</div>\
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
									<input style="width:' + field.inputBoxWidth + 'px" name="input" required type="text" \
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
			
			var template = '';
			
			if (scope.smoRecordArray.toggle == true) {
				template += '\
				<div class="field-label"><div style="display: inline-block;" data-toggle="tooltip" title="' + scope.smoRecordArray.description + '" tooltip>' + scope.smoRecordArray.label + '</div></div>\
				<div class="field-input"><smo-button action="toggle()" icon="edit" tip="Edit" size="md"></smo-button></div>';
			}
			
			if (scope.smoRecordArray.toggle == true) {
				template += '\
					<div class="record-array" ng-show="expanded" ng-click="toggle()">';
			}
			
			editModeTemplate = '\
				<table class="nice-table">\
					<tr>\
						<th style="min-width: 10px;">\
						</th>' +
							headerRowTemplate +
						'<th style="min-width: 10px; cursor: pointer;">\
							<smo-button action="addRow(-1)" icon="plus" tip="Add row"></smo-button>\
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
				</table>';
			
			template += editModeTemplate;
			
			if (scope.smoRecordArray.toggle == true) {
				template += '</div>';
			}
			
	        var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
	        $(".record-array > table").bind('click', function(e){
                e.stopPropagation();
            });
		}
	}
}]);

smoModule.directive('smoViewToolbar', ['$compile', '$rootScope', 'util', function($compile, $rootScope, util) {
	return {
		scope: {
			model: "=",
			viewName: "=",
			actions: "=",
			reader: "="
		},
		controller: function($scope) {
			var formName = $scope.model.name + $scope.viewName + 'Form';
			$scope.form = $scope.$parent[formName];
//			var onFetchSuccess = function(comm){
//				if (comm.data.values.recordId){
//					comm.model.recordId = comm.data.values.recordId;
//				} 
//			}
			
			$scope.actionHandler = function(action, params) {
				var targetView = action.outputView || $scope.viewName;
				var communicator = $scope.model[targetView + 'Communicator'];
				
				if (action.name == 'save') {
					if (params == 'local') {
						data = JSON.stringify(communicator.data.values, undefined, 4);
						var link = document.getElementById(communicator.modelName + '_' + communicator.viewName + 'Save');
					 	if (link.download === undefined) { 
					 		//if HTML5 download attribute is not supported, 
					 		//perform server-side export
					 		obj = {
					 				url: "/SmoWebBase/Export",
					 				exportOption: "json",
					 				data: data.replace(/"/g, "'"),
					 				divID: communicator.modelName + '_' + communicator.viewName + 'SaveDiv'
					 		}
					 		util.serverExport(obj);
					 		
					 	} else {
					 	  // download stuff
						  var blob = new Blob([data], {
						 	  "type": "text/plain;charset=utf8;"			
						 	});
					 	  link.setAttribute("href", window.URL.createObjectURL(blob));
					 	  link.setAttribute("download", communicator.modelName + ".dat");
					 	  link.click();
					 	}
					} else if (params == 'global') {
						communicator.saveUserInput();
					}
					return;
				} else if (action.name == 'loadLocal') {
					$scope.reader.readAsText(params);
					return;
				} else if (action.name == 'loadEg') {
					parameters = params;
				} else if (action.name == 'compute') {
					parameters = $scope.model[$scope.viewName + 'Communicator'].data.values;
					if (communicator.model.recordId) {
						parameters['recordId'] =
							communicator.model.recordId;
					}
					if ($scope.model.computeAsync) {
						communicator.computeAsync(parameters);
						return;
					}
				} else if (action.name == 'abort') {
					communicator.abortAsync();
					return;	
				}
				communicator.fetchData(action.name,
						parameters);
			}
		},
		link : function(scope, element, attr) {
			buttons = [];
			for (var i = 0; i < scope.actions.length; i++) {
				if (scope.actions[i].options.length>0) {
					buttons.push('\
					<div class="btn-group dropup">\
					  <button type="button" ng-disabled="!form.$valid" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-expanded="false">\
						 {{actions[' + i + '].label}} <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu">\
					     <li ng-repeat="option in actions[' + i + '].options"><a ng-click="actionHandler(actions[' + i + '], option[0])" style="cursor:pointer">{{option[1]}}</a></li>\
					  </ul>\
					</div>');
					
				} else {
					buttons.push('<button type="button" ng-hide="actions[' + i + '].name==\'abort\' && !model.computeAsync" id="' + scope.model.name + '_' + scope.actions[i].name + 'Button" ng-disabled="!form.$valid" class="btn btn-primary" ng-click="actionHandler(actions[' + i + '])">' + scope.actions[i].label + '</button>');
				}
			}
			
			buttons.push('<span class="btn btn-primary btn-file">Load <input type="file" id="' + scope.model.name + '_' + scope.viewName + 'fileInput"></span>');
			
			var template = '<div style="margin-left: 20px;" class="btn-group" role="group">'+ buttons.join("") + '</div>\
							<a id="' + scope.model.name + '_' + scope.viewName + 'Save" hidden></a>\
							<div id="' + scope.model.name + '_' + scope.viewName + 'SaveDiv" hidden></div>';
			var el = angular.element(template);
	        compiled = $compile(el);
	        element.append(el);
	        compiled(scope);
	        $('#' + scope.model.name + '_' + scope.viewName + 'fileInput').on('change', function(evt) {
	        	scope.actionHandler({name: 'loadLocal'}, evt.target.files[0]);
	        });
		
		}		
	}
}]);
                                     

smoModule.directive('smoModelView', ['$compile', '$location', 'communicator', 
         function($compile, $location, communicator) {
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
			$scope.Math = window.Math
			$scope.formName = $scope.modelName + $scope.viewName + 'Form';
			$scope.model = $scope.$parent[$scope.modelName];
			if ($scope.model.computeAsync) {
				$scope.communicator = new communicator.AsyncModelCommunicator($scope.model, $scope.modelName, $scope.viewName);
			} else {
				$scope.communicator = new communicator.ModelCommunicator($scope.model, $scope.modelName, $scope.viewName);
			}
			$scope.model[$scope.viewName + 'Communicator'] = $scope.communicator;
			if ($scope.autoFetch) {
				$scope.communicator.fetchData("load", {viewRecordId: $scope.viewRecordId});				
			}
			
			$scope.showProgress = false;
			if ($scope.model.computeAsync) {
				if ($scope.viewType == 'output') {
					$scope.showProgress = true;
				}
			} 
		},
		link : function(scope, element, attr) {
			var template = '\
				<div ng-if="communicator.loading" class="alert alert-info" role="alert">\
					<div ng-if="!showProgress">Loading... (may well take a few moments)</div>\
					<div ng-if="showProgress">\
				  	  <div ng-if="communicator.state==\'PENDING\'">Pending...</div>\
					  <div ng-if="communicator.state==\'STARTED\' || communicator.state==\'PROGRESS\'">\
						In progress...\
						<div class="progress" style="margin-top: 10px; margin-bottom: 0px;">\
						  <div id="' + scope.modelName + '_' + scope.viewName + 'ProgressBar" class="progress-bar progress-bar-info" role="progressbar"\
						  		aria-valuenow="{{communicator.current}}" aria-valuemin="0" aria-valuemax="{{communicator.total}}" style="background-color: #31708F; width: {{communicator.current/communicator.total*100}}%; min-width: 10%;">\
						  			<span ng-if="communicator.fractionOutput">{{Math.round(communicator.current)}} / {{Math.round(communicator.total)}}&nbsp{{communicator.suffix}}</span>\
						  			<span ng-if="!communicator.fractionOutput">{{Math.round(communicator.current/communicator.total*100)}}{{communicator.suffix}}</span>\
						  </div>\
						</div>\
					  </div>\
					  <div ng-if="communicator.state==\'FAILURE\'">Failed</div>\
					  <div ng-if="communicator.state==\'SUCCESS\'">Success</div>\
					  <div ng-if="communicator.state==\'REVOKED\'">Aborted</div>\
					</div>\
				</div>\
				<div ng-if="communicator.commError" class="alert alert-danger" role="alert">Communication error: <span ng-bind="communicator.errorMsg"></span></div>\
				<div ng-if="communicator.serverError" class="alert alert-danger" role="alert">Server error: <span ng-bind="communicator.errorMsg"></span>\
					<div>Stack trace:</div><pre><div ng-bind="communicator.stackTrace"></div></pre>\
				</div>\
				<div ng-form name="' + scope.formName + '">\
					<div ng-if="communicator.dataReceived">\
						<div smo-super-group-set="communicator.data.definitions" model-name="' + scope.modelName + '" view-type="' + scope.viewType + '" smo-data-source="communicator.data.values"></div>';
						
			if (scope.viewType == 'input') {
				template +='\
						<div smo-view-toolbar model="model" view-name="viewName" actions="communicator.data.actions" reader="reader"></div>';
			}
				template +='\
						<div ng-if="communicator.saveSuccess">\
							<div class="alert alert-success alert-dismissible" role="alert">\
							<button type="button" class="close" data-dismiss="alert" aria-label="Close">\
								<span aria-hidden="true">&times;</span></button>\
							<span>{{communicator.saveFeedbackMsg}}</span>\
							URL: <a ng-href={{communicator.savedRecordUrl}} target="_blank">{{communicator.savedRecordUrl}}</a>\
						</div>\
						<div ng-if="!communicator.saveSuccess">\
							<div class="alert alert-danger alert-dismissible" role="alert">\
							<button type="button" class="close" data-dismiss="alert" aria-label="Close">\
								<span aria-hidden="true">&times;</span></button>\
							<span>{{communicator.saveFeedbackMsg}}</span>\
						</div>\
					</div>\
				</div>';
			
			scope.reader = new FileReader();
			scope.reader.onloadend = function() {
				scope.communicator.data.values = JSON.parse(scope.reader.result);
				scope.communicator.dataReceived = false;
				scope.$digest();
				scope.communicator.dataReceived = true;
				scope.$digest();
			}

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
