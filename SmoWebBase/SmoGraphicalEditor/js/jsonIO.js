smoGui.io.json.circuitsReader = draw2d.io.Reader.extend({
    
    NAME : "smoGui.io.json.circuitsReader",
    
    init: function(){
        this._super();
    },
    
    /**
     * @method
     * 
     * Restore the canvas from a given JSON object.
     * 
     * @param {draw2d.Canvas} canvas the canvas to restore
     * @param {Object} document the json object to load.
     */
    unmarshal: function(canvas, json){
//    	var result = new draw2d.util.ArrayList();      
        if(typeof json === "string"){
            json = JSON.parse(json);
        }
        $.each(json, $.proxy(function(i, circuit){
        	canvas.circuits[circuit.name] = {"components": {}, "connections": []};
            $.each(circuit.components, $.proxy(function(i, element){
                try{
                	var o = eval("new "+canvas.appName+".components."+element.type+"()");
                    o.setPersistentAttributes(element);
                    canvas.add(o);
                    canvas.circuits[circuit.name].components[element.name] = o.getId();
                }
                catch(exc){
                    debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                    debug.error(exc);
                    debug.warn(element);
                }
            },this));
            
            $.each(circuit.connections, $.proxy(function(i, element){
                try{
                	var o = new draw2d.Connection();
                	var sourceData = element[0].split(".");
                	var targetData = element[1].split(".");
                	//console.log(canvas.circuits[circuit.name].components[sourceData[0]]);
                	//console.log(targetData);
                    var source= null;
                    var target=null;
                    sourceNode = canvas.getFigure(canvas.circuits[circuit.name].components[sourceData[0]]);
                    if(sourceNode===null){
                        throw "Source figure with id '"+sourceNode.getId()+"' not found";
                    }
                    source = sourceNode.getPort(sourceData[1]);
                    if(source===null){
                        throw "Unable to find source port '"+sourceData[1]+"' at figure '"+sourceData[0]+"' to unmarshal '"+element.type+"'";
                    }
                    targetNode = canvas.getFigure(canvas.circuits[circuit.name].components[targetData[0]]);
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
                    canvas.circuits[circuit.name].connections.push(o);
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
                if(typeof element.composite !== "undefined"){
                   var figure = canvas.getFigure(element.id);
                   if(figure===null){
                       figure =canvas.getLine(element.id);
                   }
                   var group = canvas.getFigure(element.composite);
                   group.assignFigure(figure);
                }
            },this));
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
        
//        return result;
    }
});

smoGui.io.json.componentsReader = draw2d.io.json.Reader.extend({
    
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
            	if (typeof componentDef.ports !== 'undefined') {
	            	eval('var ports = ' + JSON.stringify(componentDef.ports)); 
            	}
            	eval('result.' + componentDef.name + ' = draw2d.SVGFigure\
            			.extend({\
                    		NAME : "' + componentDef.name + '",\
                    		SmoPortLocator : draw2d.layout.locator.PortLocator.extend({\
                    	        init: function(x_frac, y_frac){\
                    	            this._super();\
                    				this.x_frac = x_frac;\
                    				this.y_frac = y_frac;\
                    	        },\
	                    		relocate:function(index, port){\
	                    			var x = port.getParent().getWidth() * this.x_frac;\
	                    			var y = port.getParent().getHeight() * this.y_frac;\
		                            this.applyConsiderRotation(port, x, y);\
		                        }\
            				}),\
                    		init : function(attr, setter, getter)\
                    		{\
                    			this._super(attr, setter, getter);\
                    			for (var i=0; i<ports.length; i++) {\
                    				var portLocator =  new this.SmoPortLocator(ports[i][2][0], ports[i][2][1]);\
                    				var port = this.createPort(ports[i][1], portLocator);\
                    				port.setName(ports[i][0]);\
            	            	}\
                    			this.installEditPolicy(new smoGui.FigureEditPolicy());\
                    		},\
                    		getSVG: function(){\
                    			return \'' + componentDef.geometry +
                    		'\';}\
                    	});'
            	);
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