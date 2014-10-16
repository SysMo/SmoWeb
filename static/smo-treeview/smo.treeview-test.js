/*
	@license Angular Treeview version 0.1.6
	ⓒ 2013 AHN JAE-HA http://github.com/eu81273/angular.treeview
	License: MIT


	[TREE attribute]
	angular-treeview: the treeview directive
	tree-id : each tree's unique id.
	tree-model : the tree model on $scope.
	node-id : each node's id
	node-label : each node's label
	node-children: each node's children

	<div
		data-angular-treeview="true"
		data-tree-id="tree"
		data-tree-model="roleList"
		data-node-id="roleId"
		data-node-label="roleName"
		data-node-children="children" >
	</div>
*/

(function ( angular ) {
	'use strict';

	angular.module( 'angularTreeview', [] )
	.config(['$httpProvider', function($httpProvider) {
		$httpProvider.defaults.xsrfCookieName = 'csrftoken';
		$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
		//$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	}])
	
	.directive( 'treeModel', ['$compile', '$http', function( $compile, $http ) {
		return {
			restrict: 'A',
			link: function ( scope, element, attrs ) {
				//tree id
				var treeId = attrs.treeId;
			
				//tree model
				var treeModel = attrs.treeModel;

				//node id
				var nodeId = attrs.nodeId || 'id';

				//node label
				var nodeLabel = attrs.nodeLabel || 'label';

				//children
				var nodeChildren = attrs.nodeChildren || 'children';
				
				//var nodeType = attrs.nodeType || 'type';
				
				//tree template
//				var template =
//					'<ul>' +
//						'<li data-ng-repeat="node in ' + treeModel + '">' +
//							'<i data-ng-style="' + treeId + '.setImgStyle(node)" data-ng-click="' + treeId + '.selectNodeHead(node)"></i> ' +
//							'<span data-ng-class="node.selected" data-ng-click="' + treeId + '.selectNodeLabel(node)">{{node.' + nodeLabel + '}}</span>' +
//							'<div data-ng-hide="node.collapsed" data-tree-id="' + treeId + '" data-tree-model="node.' + nodeChildren + '" data-node-id=' + nodeId + ' data-node-label=' + nodeLabel + ' data-node-children=' + nodeChildren + '></div>' +
//						'</li>' +
//					'</ul>';

				var dropdownHTML = "<div class=\"dropdown\" ng-style=\"{cursor: 'pointer'}\">" +  
				"<div class=\"navbar-collapse collapse\">" +
				  "<button class=\"btn btn-xs btn-default dropdown-toggle\" type=\"button\" id=\"dropdownMenu1\" data-toggle=\"dropdown\">" +
				    "<span class=\"caret\"></span>" +
				  "</button>" +
				  "<ul ng-show=\"" + treeId + ".isDataSet(" + treeId + ".currentNode.type)\" class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu1\">" +
				  	"<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".view(" + treeId + ".currentNode)\">View</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".del(" + treeId + ".currentNode)\">Delete</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".rename(" + treeId + ".currentNode)\">Rename</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".copy(" + treeId + ".currentNode)\">Copy</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".move(" + treeId + ".currentNode)\">Move</a></li>" +				    
				  "</ul>" +
				  "<ul ng-show=\"!" + treeId + ".isDataSet(" + treeId + ".currentNode.type) && !" + treeId + ".isFile(" + treeId + ".currentNode.type)\" class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu1\">" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".createGroup(" + treeId + ".currentNode)\">Create group</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".createDataset(" + treeId + ".currentNode)\">Create dataset</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".del(" + treeId + ".currentNode)\">Delete</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".rename(" + treeId + ".currentNode)\">Rename</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".copy(" + treeId + ".currentNode)\">Copy</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".move(" + treeId + ".currentNode)\">Move</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".expandAll(" + treeId + ".currentNode)\">Expand all</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".collapseAll(" + treeId + ".currentNode)\">Collapse all</a></li>" +
				    
				  "</ul>" +
				  "<ul ng-show=\"" + treeId + ".isFile(" + treeId + ".currentNode.type)\" class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu1\">" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".loadTree()\">Refresh</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".createGroup(" + treeId + ".currentNode)\">Create group</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".createDataset(" + treeId + ".currentNode)\">Create dataset</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".expandAll(" + treeId + ".currentNode)\">Expand all</a></li>" +
				    "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" ng-click=\"" + treeId + ".collapseAll(" + treeId + ".currentNode)\">Collapse all</a></li>" +
				  "</ul>" +
				"</div>" +  
				"</div>"
				
				
				
				var template =
					'<ul>' +
						'<li data-ng-repeat="node in ' + treeModel + '">' +
							'<table>' +
								'<tr>' +
									'<td> ' +
										'<i data-ng-style="' + treeId + '.setImgStyle(node)" data-ng-click="' + treeId + '.selectNodeHead(node)"></i> ' +
										'<span data-ng-class="node.selected" data-ng-click="' + treeId + '.selectNodeLabel(node)">{{node.' + nodeLabel + '}} </span>' +
									'</td>' +
									'<td ng-show="node.selected">' +
										dropdownHTML +
									'</td>' +	
								'</tr>' +
							'</table>' +
							'<div data-ng-hide="node.collapsed" data-tree-id="' + treeId + '" data-tree-model="node.' + nodeChildren + '" data-node-id=' + nodeId + ' data-node-label=' + nodeLabel + ' data-node-children=' + nodeChildren + '></div>' +
						'</li>' +
					'</ul>';
							

				//check tree id, tree model
				if( treeId && treeModel ) {

					//root node
					if( attrs.angularTreeview ) {
						
						//create tree object if not exists
						
											
						scope[treeId].action = 'getHdfFileContent';
						
						scope[treeId].actionText = "";
						
						scope[treeId].input = "";
						
						console.log(treeModel);
						
//						scope[treeId].currentNode = treeModel[]
						
						scope[treeId].setAttrAll = function(node, Attr, value){
							var index;
							node[Attr] = value;
							if (node[nodeChildren].length){
								for (index in node[nodeChildren]){
									scope[treeId].setAttrAll(node[nodeChildren][index], Attr, value);
								}
							}
							
						}

						//if node head clicks,
						scope[treeId].selectNodeHead = scope[treeId].selectNodeHead || function( selectedNode ){

							//Collapse or Expand
							selectedNode.collapsed = !selectedNode.collapsed;
							
//							scope[treeId].action = "";
//							
//							scope[treeId].input = "";
							
							scope["tableLoaded"] = false;
						};

						//if node label clicks,
						scope[treeId].selectNodeLabel = scope[treeId].selectNodeLabel || function( selectedNode ){

							//remove highlight from previous node
							if( scope[treeId].currentNode && scope[treeId].currentNode.selected ) {
								scope[treeId].currentNode.selected = undefined;
		
							}

							//set highlight to selected node
							selectedNode.selected = 'selected';

							//set currentNode
							scope[treeId].currentNode = selectedNode;
							
//							scope[treeId].action = "";
//							
//							scope[treeId].input = "";
							
							scope["tableLoaded"] = false;
														
						};
						
						scope[treeId].isDataSet = function(nodeType) {
							
							if (nodeType == 'dataset'){
								return true;
							} else {
								return false;
							}
						}
						
						scope[treeId].isFile = function(nodeType) {
							if (nodeType == 'hdf_file'){
								return true;
							} else {
								return false;
							}
						}
						
						scope[treeId].setImgStyle = scope[treeId].setImgStyle || function (node) {
							var img;
							if (node.type == 'dataset') {
								img = "url('/static/smo-treeview/img/file.png')";
							} else if (node.type == 'group') { 
								if (node.collapsed) { 
									img = "url('/static/smo-treeview/img/folder-closed.png')";
								} else {
									img = "url('/static/smo-treeview/img/folder.png')";
								}
							} else if (node.type == 'hdf_file') { 
								if (node.collapsed) { 
									img = "url('/static/smo-treeview/img/folder-closed.png')";
								} else {
									img = "url('/static/smo-treeview/img/folder.png')";
								}								
							}
							var imgStyle = { "padding" : "1px 10px",
						  		"background-repeat": "no-repeat",
						  		"background-image" : img
				  			};
							return imgStyle;
						};
						
						scope[treeId].view = function (node) {
					    	scope[treeId].action = "view";
					    	console.log('Viewing ' + node.path);
					    	console.log(scope[treeId].action);
					    	scope[treeId].sendActionData();						    
						};
						
						scope[treeId].del = function (node) {
						    if (confirm('You are about to delete' + node.path) == true) {
						    	scope[treeId].action = "delete";
						    	console.log('Deleting ' + node.path);
						    	scope[treeId].sendActionData();
						    } 
						};
						
						scope[treeId].copy = function (node) {
							scope.focus = true;
							scope[treeId].input = "";
							scope[treeId].action = "copy";
							console.log('Copying ' + node.path);
						};
						
						scope[treeId].move = function (node) {
							scope.focus = true;
							scope[treeId].input = "";
							scope[treeId].action = "move";
							console.log('Moving ' + node.path);
						};
						scope[treeId].rename = function (node) {
							scope.focus = true;
							scope[treeId].input = "";
							scope[treeId].action = "rename";
							console.log('Renaming ' + node.path);
						};
						
						scope[treeId].createGroup = function (node) {
							scope.focus = true;
							scope[treeId].input = "";
							scope[treeId].action = "createGroup";
							console.log('Creating group ' + node.path);
						};
						
						scope[treeId].createDataset = function (node) {
							scope.focus = true;
							scope[treeId].input = "";
							scope[treeId].action = "createDataset";
							alert("Not implemented!");
						};
						
						
						scope[treeId].expandAll = function (node) {
							scope[treeId].setAttrAll(node, "collapsed", false);						
							console.log('Expanding all from' + node.path);
						};
						
						scope[treeId].collapseAll = function (node) {
							scope[treeId].setAttrAll(node, "collapsed", true);
							console.log('Collapsing all from' + node.path);				
						};
						
						scope[treeId].isInputAction = function (action) {
							if (action == "copy"){				
								return true;
							} else if (action == "move" ){
								return true;
							} else if (action == "rename"){
								return true;
							} else if (action == "createGroup"){
								return true;
							} else if (action == "createDataset"){
								return true;
							} else {
								return false;
							}
						}
						
						scope[treeId].getActionText = function(action) {
							if (action == "copy"){
								scope[treeId].actionText = "Enter copy destination";
							} else if (action == "move" ){
								scope[treeId].actionText = "Enter move destination";
							} else if (action == "rename"){
								scope[treeId].actionText = "Enter new name";
							} else if (action == "createGroup"){
								scope[treeId].actionText = "Enter group name";
							} else if (action == "createDataset"){
								scope[treeId].actionText = "Enter dataset name";
							} else {
								scope[treeId].actionText = "";
							}
							return scope[treeId].actionText;
						}
						
					}

					//Rendering template.
					element.html('').append( $compile( template )( scope ) );
				}
			
			}
		};
	}])
	
	.directive( 'smoHdfBrowser', ['$compile', '$http', function( $compile, $http ) {
		return {
			restrict: 'E',
			link: function ( scope, element, attrs ) {
				var treeId = attrs.treeId;
					
				scope[treeId] = scope[treeId] || {};
				
				scope[treeId].loadTree = function() {
					
					$http.post('/DataManagement/HdfInterface/', {
						action : 'getHdfFileContent',
						input: '',
						currentNode: ''
					})
					.success(function(data){
						scope[treeId].fileContent = data.fileContent;
//						console.log(angular.toJson(scope.fileContent, true));
					})
					.error(function(data){
						console.log("Load error!");
					});
				}
				
				scope[treeId].loadTree();
				
				var treeViewTemplate = 
					'<div ' + 
						'data-angular-treeview="true" ' +
					    'data-tree-id="' + treeId + '" ' +	
						'data-tree-model="' + treeId + '.fileContent" ' +
						'data-node-id="id" ' +
						'data-node-label="name" ' +
						'data-node-children="children" >' +
					'</div>' +
					'<br>' +
					 '<div ng-show="' + treeId + '.isInputAction(' + treeId + '.action)">' +
						  '<div style="font-weight: bold;" ng-bind="' + treeId + '.getActionText(' + treeId + '.action)"></div>' +
						  '<input focus-me="focus" ng-model="' + treeId + '.input"></input>' +
						  '<button ng-click="' + treeId + '.sendActionData()">Submit</button>' +
					 '</div>';
//					 '<div>Current node: <span ng-bind="' + treeId + '.currentNode.path"></span></div>';
				
				scope[treeId].sendActionData = function () {
 
					$http.post('/DataManagement/HdfInterface/', {
						action : scope[treeId].action,
						input : scope[treeId].input,
						currentNode: scope[treeId].currentNode
					})
					.success(function(data){
						console.log("action:" + scope[treeId].action);
						if (scope[treeId].action == "view"){
							scope["columnTable"] = data;
//							scope["initTable"]();
							scope["tableLoaded"] = true;
						}					
					})
					.error(function(data){
						console.log("action:" + scope[treeId].action);
						console.log("Action error!");
					});
					
//					scope[treeId].action = "";
//					
//					scope[treeId].input = "";
					
					scope[treeId].loadTree();
					
					
				}
				
				element.html('').append( $compile( treeViewTemplate )( scope ) );
			}
		
		};
	}])
	.directive('focusMe', function($timeout) {
		  return {
		    scope: { trigger: '=focusMe' },
		    link: function(scope, element) {
		      scope.$watch('trigger', function(value) {
		        if(value === true) { 
		          //console.log('trigger',value);
		          //$timeout(function() {
		            element[0].focus();
		            scope.trigger = false;
		          //});
		        }
		      });
		    }
		  };
		});
	
})( angular );
