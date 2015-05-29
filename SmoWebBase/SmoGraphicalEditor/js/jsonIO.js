// Json reader for the circuit

smoGui.io.json.circuitReader = draw2d.io.Reader.extend({
    
    NAME : "smoGui.io.json.circuitReader",
    
    init: function(){
        this._super();
    },
    
    unmarshal: function(app, json){   
        if(typeof json === "string"){
            json = JSON.parse(json);
        }
        // Creatng the components
        $.each(json.components, $.proxy(function(i, element){
            try{
            	var o = eval("new app.componentTypes."+element.type+"()");
                // Assigning UUIDs
            	if (element.id === undefined) {
                	element.id = draw2d.util.UUID.create();
                }
            	o.setPersistentAttributes(element);
                o.name = element.name;
                if (element.rotation !== undefined) {
                	o.setRotationAngle(element.rotation);
                }
                // Adding the component to th canvas
                app.canvas.add(o);
                o.type = element.type;
                // Setting default values if values are not defined for the component
                if (element.values === undefined) {
                	o.values = o.superGroupSet.defaultValues;
                } else {
                	o.values = element.values;
                }
                // Adding to the angular scope
                o.addToScope();
            }
            catch(exc){
                debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                debug.error(exc);
                debug.warn(element);
            }
        },this));
        
        // Creating the connnections
        $.each(json.connections, $.proxy(function(i, element){
            try{
            	var o = new draw2d.Connection();
            	// The connection source data
            	var sourceData = element[0];
            	// The connection target data
            	var targetData = element[1];
                var source= null;
                var target=null;
                sourceNode = app.components[sourceData.component];
                if(sourceNode===null){
                    throw "Source figure with id '"+sourceNode.getId()+"' not found";
                }
                source = sourceNode.getPort(sourceData.port);
                if(source===null){
                    throw "Unable to find source port '"+sourceData.port+"' at figure '"+sourceData.component+"' to unmarshal '"+element.type+"'";
                }
                targetNode = app.components[targetData.component];
                if(targetNode===null){
                    throw "Source figure with id '"+targetNode.getId()+"' not found";
                }
                target = targetNode.getPort(targetData.port);
                if(target===null){
                    throw "Unable to find target port '"+targetData.port+"' at figure '"+targetData.component+"' to unmarshal '"+element.type+"'";
                }
                if(source!==null && target!==null){
                    o.setSource(source);
                    o.setTarget(target);
                }
                o.setPersistentAttributes(element);
                // Adding the connnection to the canvas
                app.canvas.add(o);
            }
            catch(exc){
                debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                debug.error(exc);
                debug.warn(element);
            }
        },this));
        // restore group assignment
        //
        $.each(app.components, $.proxy(function(i, element){
        	if(element.composite){
               var figure = app.canvas.getFigure(element.id);
               if(figure===null){
                   figure = app.canvas.getLine(element.id);
               }
               var group = app.canvas.getFigure(element.composite);
               group.assignFigure(figure);
            }
        },this));
        // recalculate all crossings and repaint the connections with 
        // possible crossing decoration
        app.canvas.calculateConnectionIntersection();
        app.canvas.getLines().each(function(i,line){
            line.svgPathString=null;
            line.repaint();
        });
        app.canvas.linesToRepaintAfterDragDrop = app.canvas.getLines().clone();
        app.canvas.showDecoration();
    }
});

// Json writer for the circuit

smoGui.io.json.circuitWriter = draw2d.io.Writer.extend({
    
    NAME : "smoGui.io.json.circuitWriter",
    
    init: function(){
        this._super();
    },
    // draw2d marshal method returning an array of figures on the canvas. It is modified to call a custom method
    // to create the circuit json
    marshal: function(app, resultCallback) {
        // I change the API signature from version 2.10.1 to 3.0.0. Throw an exception
        // if any application not care about this changes.
        if(typeof resultCallback !== "function"){
            throw "Writer.marshal method signature has been change from version 2.10.1 to version 3.0.0. Please consult the API documentation about this issue.";
        }
        var figures = [];
        app.canvas.getFigures().each(function(i, figure){
            figures.push(figure.getPersistentAttributes());
        });
        app.canvas.getLines().each(function(i, element){
            figures.push(element.getPersistentAttributes());
        });
    	var base64Content = draw2d.util.Base64.encode(JSON.stringify(figures, null, 2));
    	
    	resultCallback(this.toCircuit(app, figures), base64Content);
    },
    // Custom method creating the circuit json
    toCircuit: function(app, figures) {
    	var components = [];
    	var connections = [];
    	for (var i=0; i<figures.length; i++){
    		if (figures[i].type == "draw2d.Connection") {
    			connections.push(figures[i]);
    		}
    	}
    	for (var i=0; i<connections.length; i++) {
    		connections[i] = [
    		                  {"component": app.canvas.getFigure(connections[i].source.node).name, 
    							"port": connections[i].source.port}, 
    						  {"component": app.canvas.getFigure(connections[i].target.node).name,
    						  	"port": connections[i].target.port}
    						 ];
    	}
    	for (var componentName in app.components) {
    		components.push({"name": componentName,
    						"type": app.components[componentName].type,
    						"id": app.components[componentName].id,
    						"values": app.components[componentName].values,
    						"x": app.components[componentName].x,
    						"y": app.components[componentName].y});
    	}
    	return {"components": components, "connections": connections};
    }   
});

// Reader for the component types
smoGui.io.json.componentsReader = draw2d.io.Reader.extend({
    
    NAME : "smoGui.io.json.componentsReader",
    
    init: function(){
        this._super();
    },
    
    read: function(json){
    	var result = {}
        if(typeof json ==="string"){
            json = JSON.parse(json);
        }
        
        $.each(json, $.proxy(function(i, componentDef){
            try{
            	var ports;
            	var superGroupSet;
            	// Reading the array of ports
            	if (typeof componentDef.ports !== 'undefined') {
	            	eval('ports = ' + JSON.stringify(componentDef.ports)); 
            	} else {
            		ports = [];
            	}
            	// Reading the super group set definition
            	if (typeof componentDef.superGroupSet !== 'undefined') {
	            	eval('var superGroupSet = ' + JSON.stringify(componentDef.superGroupSet));
            	} else {
            		throw ('Super-group set is undefined.');
            	}
            	// Creating the component types
            	eval('result.' + componentDef.name + ' = smoGui.SVGFigure\
            			.extend({\
            				NAME : "' + componentDef.name + '",\
	            			init : function(attr, setter, getter)\
	            			{\
            					this.ports = ports;\
            					this.superGroupSet = angular.copy(superGroupSet);\
            					this._super(attr, setter, getter);\
            				},\
                    		getSVG: function(){\
            					this.getCanvas().count++;\
                    			return \'' + componentDef.geometry +
                    		'\';}\
                    	});');
            }
            catch(exc){
                debug.error(componentDef,"Unable to create component type '"+ componentDef.name);
                debug.error(exc);
                debug.warn(componentDef);
            }
        },this));
        return result;
    }
});