smoGui.io.json.circuitsReader = draw2d.io.Reader.extend({
    
    NAME : "smoGui.io.json.circuitsReader",
    
    init: function(){
        this._super();
    },
    
    unmarshal: function(canvas, json){   
        if(typeof json === "string"){
            json = JSON.parse(json);
        }
        var circuit = {"components": {}, "connections": []};
        $.each(json.components, $.proxy(function(i, element){
            try{
            	var o = eval("new "+canvas.appName+".componentTypes."+element.type+"()");
                o.setPersistentAttributes(element);
                o.name = element.name;
                if (element.rotation !== undefined) {
                	o.setRotationAngle(element.rotation);
                }
                if (element.values !== undefined) {
                	o.values = element.values;
                } 
                canvas.add(o);
                circuit.components[element.name] = o;
            }
            catch(exc){
                debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                debug.error(exc);
                debug.warn(element);
            }
        },this));
        
        $.each(json.connections, $.proxy(function(i, element){
            try{
            	var o = new draw2d.Connection();
            	var sourceData = element[0].split(".");
            	var targetData = element[1].split(".");
                var source= null;
                var target=null;
                sourceNode = circuit.components[sourceData[0]];
                if(sourceNode===null){
                    throw "Source figure with id '"+sourceNode.getId()+"' not found";
                }
                source = sourceNode.getPort(sourceData[1]);
                if(source===null){
                    throw "Unable to find source port '"+sourceData[1]+"' at figure '"+sourceData[0]+"' to unmarshal '"+element.type+"'";
                }
                targetNode = circuit.components[targetData[0]];
                if(targetNode===null){
                    throw "Source figure with id '"+targetNode.getId()+"' not found";
                }
                target = targetNode.getPort(targetData[1]);
                if(target===null){
                    throw "Unable to find target port '"+targetData[1]+"' at figure '"+targetData[0]+"' to unmarshal '"+element.type+"'";
                }
                if(source!==null && target!==null){
                    o.setSource(source);
                    o.setTarget(target);
                }
                o.setPersistentAttributes(element);
                canvas.add(o);
                circuit.connections.push(o);
            }
            catch(exc){
                debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                debug.error(exc);
                debug.warn(element);
            }
        },this));
        // restore group assignment
        //
        $.each(circuit.components, $.proxy(function(i, element){
        	if(element.composite){
               var figure = canvas.getFigure(element.id);
               if(figure===null){
                   figure = canvas.getLine(element.id);
               }
               var group = canvas.getFigure(element.composite);
               group.assignFigure(figure);
            }
        },this));
        // recalculate all crossings and repaint the connections with 
        // possible crossing decoration
        canvas.calculateConnectionIntersection();
        canvas.getLines().each(function(i,line){
            line.svgPathString=null;
            line.repaint();
        });
        canvas.linesToRepaintAfterDragDrop = canvas.getLines().clone();

        canvas.showDecoration();
        return circuit;
    }
});

smoGui.io.json.circuitsWriter = draw2d.io.Writer.extend({
    
    NAME : "smoGui.io.json.circuitsWriter",
    
    init: function(){
        this._super();
    },
    marshal: function(canvas, resultCallback) {
        // I change the API signature from version 2.10.1 to 3.0.0. Throw an exception
        // if any application not care about this changes.
        if(typeof resultCallback !== "function"){
            throw "Writer.marshal method signature has been change from version 2.10.1 to version 3.0.0. Please consult the API documentation about this issue.";
        }
        var figures = [];
        canvas.getFigures().each(function(i, figure){
            figures.push(figure.getPersistentAttributes());
        });
        canvas.getLines().each(function(i, element){
            figures.push(element.getPersistentAttributes());
        });
    	var base64Content = draw2d.util.Base64.encode(JSON.stringify(figures, null, 2));
    	
    	resultCallback(this.toCircuit(canvas, figures), base64Content);
    },
    toCircuit: function(canvas, figures) {
    	var components = [];
    	var connections = [];
    	for (var i=0; i<figures.length; i++){
    		if (figures[i].type == "draw2d.Connection") {
    			connections.push(figures[i]);
    		} else {
    			components.push(figures[i]);
    		}
    	}
    	
    	for (var i=0; i<components.length; i++) {
    		components[i] = {"name": canvas.getFigure(components[i].id).name,
    						"type": components[i].type,
    						"id": components[i].id,
    						"x": components[i].x,
    						"y": components[i].y};
    	}
    	for (var i=0; i<connections.length; i++) {
    		connections[i] = [canvas.getFigure(connections[i].source.node).name+"."+connections[i].source.port,
    		                  canvas.getFigure(connections[i].target.node).name+"."+connections[i].target.port];
    	}
    	return {"components": components, "connections": connections};
    }   
});

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
            	var portsData = {};
            	var ports;
            	var fields;
            	if (typeof componentDef.ports !== 'undefined') {
	            	eval('ports = ' + JSON.stringify(componentDef.ports)); 
            	} else {
            		ports = [];
            	}
            	if (typeof componentDef.fields !== 'undefined') {
	            	eval('var fields = ' + JSON.stringify(componentDef.fields)); 
            	} else {
            		fields = [];
            	}
            	var count = 0;
            	eval('result.' + componentDef.name + ' = smoGui.SVGFigure\
            			.extend({\
            				NAME : "' + componentDef.name + '",\
	            			init : function(attr, setter, getter)\
	            			{\
            					this.count = count;\
            					this._super($.extend({ports: ports, fields: fields}, attr), setter, getter);\
            					count++;\
            				},\
                    		getSVG: function(){\
                    			return \'' + componentDef.geometry +
                    		'\';}\
                    	});');
            }
            catch(exc){
                debug.error(componentDef,"Unable to create component name '"+ componentDef.name);
                debug.error(exc);
                debug.warn(componentDef);
            }
        },this));
        return result;
    }
});