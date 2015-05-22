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
        var result = new draw2d.util.ArrayList();
        
        if(typeof json ==="string"){
            json = JSON.parse(json);
        }

        var node=null;
        $.each(json, $.proxy(function(i, element){
            try{
            	var o = eval("new "+canvas.appName+".components."+element.type+"()");
                var source= null;
                var target=null;
                for(i in element){
                    var val = element[i];
                    if(i === "source"){
                        node = canvas.getFigure(val.node);
                        if(node===null){
                            throw "Source figure with id '"+val.node+"' not found";
                        }
                        source = node.getPort(val.port);
                        if(source===null){
                            throw "Unable to find source port '"+val.port+"' at figure '"+val.node+"' to unmarschal '"+element.type+"'";
                        }
                    }
                    else if (i === "target"){
                        node = canvas.getFigure(val.node);
                        if(node===null){
                            throw "Target figure with id '"+val.node+"' not found";
                        }
                        target = node.getPort(val.port);
                        if(target===null){
                            throw "Unable to find target port '"+val.port+"' at figure '"+val.node+"' to unmarschal '"+element.type+"'";
                        }
                    }
                }
                if(source!==null && target!==null){
                    o.setSource(source);
                    o.setTarget(target);
                }
                o.setPersistentAttributes(element);
                canvas.add(o);
                result.add(o);
            }
            catch(exc){
                debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                debug.error(exc);
                debug.warn(element);
            }
        },this));
        
        // restore group assignment
        //
        $.each(json, $.proxy(function(i, element){
            if(typeof element.composite !== "undefined"){
               var figure = canvas.getFigure(element.id);
               if(figure===null){
                   figure =canvas.getLine(element.id);
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
        
        return result;
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
	            	eval('var portsData = ' + JSON.stringify(componentDef.ports));    	
            	}
            	eval('result.' + componentDef.name + ' = draw2d.SVGFigure\
            			.extend({\
                    		NAME : "' + componentDef.name + '",\
                    		init : function(attr, setter, getter)\
                    		{\
                    			this._super(attr, setter, getter);\
                    			for (var portType in portsData) {\
            	            		for (var n=1; n<=portsData[portType]; n++) {\
            	            			this.addPort(eval("new draw2d." + portType + "()"));\
            	            		}\
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